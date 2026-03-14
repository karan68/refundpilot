"""ReAct Loop — LLM-based agentic reasoning for the INVESTIGATE zone (score 31-70).

When the math score is ambiguous (31-70), the agent enters a ReAct loop:
  THOUGHT → ACTION → OBSERVATION → THOUGHT → ... → FINAL DECISION

Tools available to the agent:
  - request_evidence: Ask customer to upload damage photo with barcode
  - analyze_photo: Run vision analysis on uploaded evidence
  - offer_store_credit: Calculate and offer store credit with bonus
  - check_cross_merchant: Query Pine Labs network for claims at other merchants
  - check_fraud_ring: Check if shipping address is linked to other refund accounts

Guardrails (F21):
  - Max 5 iterations
  - Tool whitelist enforcement
  - Hard circuit breakers override LLM decisions
"""

import json

ALLOWED_TOOLS = [
    "request_evidence",
    "analyze_photo",
    "offer_store_credit",
    "check_cross_merchant",
    "check_fraud_ring",
    "approve_refund",
    "escalate",
]

MAX_REACT_ITERATIONS = 5


async def run_react_loop(signals_data: dict, decision_result: dict, message: str, reason: str) -> dict:
    """Run a ReAct reasoning loop for investigate-zone cases.

    Uses GLM for LLM reasoning when LLM_ENABLED=true.
    Falls back to heuristic tool selection otherwise.
    """
    from config import LLM_ENABLED

    signals = signals_data["signals"]
    risk_score = decision_result["risk_score"]

    steps = []

    if not LLM_ENABLED:
        return await _heuristic_react_loop(signals, risk_score, signals_data, steps)

    # Try LLM-based ReAct
    try:
        result = await _llm_react_loop(signals_data, decision_result, message, reason, steps)
        return result
    except Exception:
        # GLM unavailable — use heuristic ReAct simulation
        return await _heuristic_react_loop(signals, risk_score, signals_data, steps)


async def _llm_react_loop(
    signals_data: dict, decision_result: dict, message: str, reason: str, steps: list
) -> dict:
    """LLM-powered ReAct loop using ZhipuAI GLM."""
    from services.zhipu_service import invoke_llm

    signals = signals_data["signals"]
    risk_score = decision_result["risk_score"]

    system_prompt = """You are RefundPilot's investigation agent. A refund request scored in the ambiguous zone (31-70).
Your job: decide what to do next by reasoning step-by-step.

Available tools (pick ONE per step):
- request_evidence: Ask customer for damage photo with barcode
- offer_store_credit: Offer store credit with bonus instead of cash refund
- check_cross_merchant: Query Pine Labs for claims at other merchants
- check_fraud_ring: Check if address is linked to other refund accounts
- approve_refund: Approve the refund (only if evidence is sufficient)
- escalate: Escalate to human (if too suspicious)

Respond in JSON: {"thought": "...", "action": "tool_name", "reason": "..."}
After gathering enough info, use "approve_refund" or "escalate" as your final action."""

    context = _build_context(signals_data, decision_result, message, reason)

    for iteration in range(MAX_REACT_ITERATIONS):
        prompt = f"""{context}

Iteration {iteration + 1}/{MAX_REACT_ITERATIONS}.
Previous steps: {json.dumps(steps) if steps else 'None'}

What should the agent do next? Respond in JSON only."""

        try:
            response = await invoke_llm(prompt, system=system_prompt, max_tokens=512)
            parsed = _parse_llm_response(response)
        except Exception:
            # LLM call failed — fall back
            raise

        action = parsed.get("action", "request_evidence")

        # F21: Tool whitelist enforcement
        if action not in ALLOWED_TOOLS:
            action = "request_evidence"
            parsed["thought"] = f"Invalid tool '{parsed.get('action')}' — defaulting to request_evidence"

        # Execute the tool observation
        observation = await _execute_tool(action, signals_data)

        step = {
            "iteration": iteration + 1,
            "thought": parsed.get("thought", ""),
            "action": action,
            "observation": observation,
        }
        steps.append(step)

        # Terminal actions
        if action in ("approve_refund", "escalate"):
            return {
                "steps": steps,
                "final_action": action,
                "iterations": iteration + 1,
                "source": "llm",
            }

    # Max iterations reached — auto-escalate (F21 Layer 3)
    steps.append({
        "iteration": MAX_REACT_ITERATIONS + 1,
        "thought": "Max iterations reached — auto-escalating to human",
        "action": "escalate",
        "observation": "GUARDRAIL: Iteration cap reached",
    })

    return {
        "steps": steps,
        "final_action": "escalate",
        "iterations": MAX_REACT_ITERATIONS,
        "source": "llm_capped",
    }


async def _heuristic_react_loop(signals: dict, risk_score: int, signals_data: dict, steps: list) -> dict:
    """Heuristic-based ReAct simulation when Bedrock is unavailable."""

    # Step 1: Assess the situation
    cm_score = signals.get("cross_merchant_fraud", {}).get("score", 0)
    dc_score = signals.get("delivery_contradiction", {}).get("score", 0)
    sentiment_score = signals.get("sentiment", {}).get("score", 0)
    is_cold_start = signals_data.get("is_cold_start", False)

    steps.append({
        "type": "THOUGHT",
        "content": f"Risk score is {risk_score}/100 — falls in the investigate zone (31-70). Let me analyze the key signals to determine what action to take. Cross-merchant fraud score: {cm_score}, delivery contradiction: {dc_score}, sentiment: {sentiment_score}.",
        "iteration": 1,
    })

    # Step 2: Pick action based on signals
    if is_cold_start:
        action = "request_evidence"
        thought = "This is a new customer with fewer than 3 orders. I don't have enough behavioral data to make a confident decision. Requesting photo evidence of the damage as a precautionary measure."
    elif 0 < cm_score < 100:
        action = "check_cross_merchant"
        thought = f"Cross-merchant fraud score is {cm_score} — this customer has filed claims at other Pine Labs merchants. Querying the Pine Labs network for detailed cross-merchant refund data."
    elif 0 < dc_score < 100:
        action = "request_evidence"
        thought = f"Delivery contradiction score is {dc_score} — the claimed issue doesn't fully match the delivery status. Requesting photo evidence with barcode/tag visible to verify the damage claim."
    elif sentiment_score >= 10:
        action = "request_evidence"
        thought = "The refund message appears formulaic — serial abusers often use copy-paste templates. Requesting photo evidence to verify this is a genuine claim."
    elif risk_score <= 45:
        action = "offer_store_credit"
        thought = f"Score {risk_score} is in the lower investigate zone. The customer profile suggests they may be retainable. Calculating a store credit offer with bonus to retain revenue."
    else:
        action = "request_evidence"
        thought = f"Score {risk_score} is in the upper investigate zone — more evidence needed before making a decision. Requesting damage photo with product barcode visible."

    observation = await _execute_tool(action, signals_data)

    steps.append({
        "type": "ACTION",
        "content": thought,
        "tool": action,
        "iteration": 2,
    })
    steps.append({
        "type": "OBSERVATION",
        "content": observation,
        "iteration": 2,
    })

    # Step 3: Final decision
    if action == "offer_store_credit" and risk_score <= 45:
        final = "approve_refund"
        final_thought = "Store credit offered as alternative. Approving with credit option."
    elif risk_score >= 55:
        final = "escalate"
        final_thought = f"Score {risk_score} plus investigation findings suggest escalation."
    else:
        final = "request_evidence"
        final_thought = "Awaiting customer evidence to make final determination."

    steps.append({
        "type": "THOUGHT",
        "content": final_thought,
        "iteration": 3,
    })

    return {
        "steps": steps,
        "final_action": final if final in ("approve_refund", "escalate") else "request_evidence",
        "iterations": 3,
        "source": "heuristic",
    }


async def _execute_tool(action: str, signals_data: dict) -> str:
    """Execute a ReAct tool and return the observation string."""
    if action == "request_evidence":
        return "Evidence request sent to customer. Awaiting photo upload with barcode/tag visible."

    elif action == "check_cross_merchant":
        cm = signals_data.get("cross_merchant_claims", [])
        if cm:
            merchants = [c.get("merchant_name", "unknown") for c in cm]
            return f"Pine Labs network query: {len(cm)} claims found at other merchants: {', '.join(merchants)}"
        return "Pine Labs network query: No claims at other merchants found."

    elif action == "check_fraud_ring":
        customer = signals_data.get("customer", {})
        return f"Checking fraud ring for customer {customer.get('name', 'unknown')} at shipping address..."

    elif action == "offer_store_credit":
        amount = signals_data.get("order_amount", 0)
        bonus = round(amount * 0.08)
        return f"Store credit offer: ₹{amount + bonus} (₹{amount} + ₹{bonus} bonus) generated."

    elif action == "analyze_photo":
        return "Photo analysis: awaiting customer upload."

    elif action in ("approve_refund", "escalate"):
        return f"Terminal action: {action}"

    return f"Unknown tool: {action}"


def _build_context(signals_data: dict, decision_result: dict, message: str, reason: str) -> str:
    """Build context string for the LLM."""
    signals = signals_data["signals"]
    customer = signals_data.get("customer", {})

    lines = [
        f"Customer: {customer.get('name', 'unknown')} ({customer.get('customer_type', 'unknown')})",
        f"Refund reason: {reason}",
        f"Message: {message}",
        f"Risk score: {decision_result['risk_score']}/100",
        f"Amount: ₹{signals_data.get('order_amount', 0)}",
        f"Cold start: {signals_data.get('is_cold_start', False)}",
        "",
        "Signal breakdown:",
    ]
    for name, sig in signals.items():
        lines.append(f"  {name}: score={sig['score']}, detail={sig['detail']}")

    return "\n".join(lines)


def _parse_llm_response(response: str) -> dict:
    """Parse LLM JSON response with fallback."""
    try:
        # Try direct JSON parse
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code block
    if "```json" in response:
        start = response.index("```json") + 7
        end = response.index("```", start)
        try:
            return json.loads(response[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # Try extracting any JSON object
    for i, c in enumerate(response):
        if c == "{":
            for j in range(len(response) - 1, i, -1):
                if response[j] == "}":
                    try:
                        return json.loads(response[i : j + 1])
                    except json.JSONDecodeError:
                        continue

    return {"thought": "Could not parse LLM response", "action": "request_evidence", "reason": "parse_failure"}
