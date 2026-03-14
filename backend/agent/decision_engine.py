"""Decision Engine — 3-tier hybrid: math decides clear cases, LLM handles gray zone.

Tier 1 (score 0-30):  Math decides → AUTO_APPROVE. LLM generates explanation only.
Tier 2 (score 31-70): LLM decides → INVESTIGATE. Agent picks next action.
Tier 3 (score 71-100): Math decides → ESCALATE. Agent builds case brief.
"""

from agent.risk_scorer import compute_risk_score
from agent.counterfactual import compute_counterfactuals
from agent.react_loop import run_react_loop
from config import RETURNLESS_REFUND_THRESHOLD, LLM_ENABLED
import json


# F21: Hard circuit-breaker rules — math overrides LLM
CIRCUIT_BREAKER_SIGNALS = {
    "delivery_contradiction": 100,  # S2 = 100 → force escalate
    "cross_merchant_fraud": 100,    # S10 = 100 → force escalate
}


def check_circuit_breakers(signals: dict) -> tuple[bool, str]:
    """F21: Check if any hard fraud signal fires, forcing escalation regardless of score."""
    for signal_name, threshold in CIRCUIT_BREAKER_SIGNALS.items():
        if signal_name in signals and signals[signal_name]["score"] >= threshold:
            return True, f"GUARDRAIL: {signal_name} = {signals[signal_name]['score']} (hard fraud signal). Forcing escalation."

    # Combined check: S1 > 90 AND S8 > 75
    s1 = signals.get("customer_refund_rate", {}).get("score", 0)
    s8 = signals.get("rfm_frequency", {}).get("score", 0)
    if s1 > 90 and s8 > 75:
        return True, f"GUARDRAIL: S1={s1} AND S8={s8} (chronic abuser with burst). Forcing escalation."

    return False, ""


async def evaluate_refund(signals_data: dict, message: str, reason: str, preset: str = "default") -> dict:
    """Run the full decision engine: score → circuit breakers → 3-tier logic → counterfactuals."""

    signals = signals_data["signals"]
    is_cold_start = signals_data.get("is_cold_start", False)

    # Step 1: Compute deterministic risk score
    score_result = compute_risk_score(signals, preset=preset)
    risk_score = score_result["risk_score"]
    decision = score_result["decision"]
    confidence = score_result["confidence"]
    reasoning_chain = score_result["reasoning_chain"]

    # Step 2: F21 — Circuit breaker check (math overrides everything)
    breaker_fired, breaker_reason = check_circuit_breakers(signals)
    if breaker_fired and decision != "ESCALATE":
        decision = "ESCALATE"
        confidence = 0.99
        reasoning_chain.append({
            "step": len(reasoning_chain) + 1,
            "signal": "circuit_breaker",
            "value": "FIRED",
            "score": 100,
            "weight": 0,
            "weighted": 0,
            "impact": "negative",
            "detail": breaker_reason,
        })

    # Step 3: Cold start handling
    cold_start_note = None
    if is_cold_start and decision == "AUTO_APPROVE":
        # New customer with < 3 orders — flag for precautionary evidence request
        decision = "INVESTIGATE"
        cold_start_note = "New customer (<3 orders). Requesting evidence as precaution."
        confidence = 0.6

    # Step 4: 3-Tier decision logic
    amount = signals_data.get("order_amount", 0)
    if decision == "AUTO_APPROVE":
        # Tier 1: Math decides. Determine returnless vs return-required.
        is_returnless = amount < RETURNLESS_REFUND_THRESHOLD
        recommended_action = "refund_returnless" if is_returnless else "refund_with_return"
        explanation = await _generate_llm_explanation(risk_score, decision, reasoning_chain, is_returnless)
        react_steps = []

    elif decision == "INVESTIGATE":
        # Tier 2: LLM ReAct loop — agent autonomously picks tools
        react_result = await run_react_loop(signals_data, {"risk_score": risk_score}, message, reason)
        recommended_action = react_result.get("final_action", "request_evidence")
        # Map terminal react actions back to our action names
        if recommended_action == "approve_refund":
            recommended_action = "refund_with_return" if amount >= RETURNLESS_REFUND_THRESHOLD else "refund_returnless"
        elif recommended_action == "escalate":
            recommended_action = "escalate_to_human"

        explanation = await _generate_llm_explanation(risk_score, decision, reasoning_chain)
        if cold_start_note:
            explanation = cold_start_note + " " + explanation
        react_steps = react_result.get("steps", [])

    else:  # ESCALATE
        recommended_action = "escalate_to_human"
        explanation = await _generate_llm_explanation(risk_score, decision, reasoning_chain)
        react_steps = []

    # Step 5: Counterfactual explanations
    counterfactuals = compute_counterfactuals(
        signals, risk_score, decision, reasoning_chain,
        preset=preset,
        seasonal_shift=score_result["seasonal_adjustment"]["threshold_shift"],
    )

    return {
        "risk_score": risk_score,
        "decision": decision,
        "confidence": confidence,
        "reasoning_chain": reasoning_chain,
        "recommended_action": recommended_action,
        "explanation": explanation,
        "counterfactuals": counterfactuals,
        "react_steps": react_steps,
        "seasonal": score_result["seasonal_adjustment"],
        "preset_used": preset,
        "is_cold_start": is_cold_start,
        "circuit_breaker_fired": breaker_fired,
    }


def _pick_investigate_action(signals: dict, is_cold_start: bool) -> str:
    """Heuristic for investigate zone — pick the most useful next action."""
    if is_cold_start:
        return "request_evidence"

    # If cross-merchant score is moderate but not max, check further
    cm_score = signals.get("cross_merchant_fraud", {}).get("score", 0)
    if 0 < cm_score < 100:
        return "check_cross_merchant"

    # If sentiment is formulaic, request evidence
    sentiment_score = signals.get("sentiment", {}).get("score", 0)
    if sentiment_score >= 10:
        return "request_evidence"

    # If delivery contradiction is partial, request evidence
    dc_score = signals.get("delivery_contradiction", {}).get("score", 0)
    if 0 < dc_score < 100:
        return "request_evidence"

    # Default: offer store credit for borderline cases
    return "offer_store_credit"


async def _generate_llm_explanation(risk_score: int, decision: str, reasoning_chain: list, is_returnless: bool = False) -> str:
    """Generate explanation using ZhipuAI GLM, with template fallback on failure."""
    if not LLM_ENABLED:
        return _generate_fallback_explanation(risk_score, decision, reasoning_chain, is_returnless)

    try:
        from services.zhipu_service import invoke_llm

        # Build signal summary for the LLM
        signal_lines = []
        for s in reasoning_chain:
            if s.get("signal") == "circuit_breaker":
                signal_lines.append(f"  CIRCUIT BREAKER: {s['detail']}")
                continue
            signal_lines.append(f"  S{s['step']} {s['signal']}: {s['detail']} (score: {s['score']}/100, weighted: {s['weighted']:+.1f})")

        prompt = f"""You are RefundPilot, an autonomous refund decision agent. 
A refund was scored {risk_score}/100 → decision: {decision}.

Signal breakdown:
{chr(10).join(signal_lines)}

Explain this decision in 2-3 concise sentences for a merchant. 
Highlight the top 2-3 signals that drove the decision.
Be direct and factual. No markdown formatting."""

        explanation = await invoke_llm(prompt, system="You are a fraud detection analyst. Be concise and factual.")
        return explanation.strip()

    except Exception:
        # Fallback to template
        return _generate_fallback_explanation(risk_score, decision, reasoning_chain, is_returnless)


def _generate_fallback_explanation(risk_score: int, decision: str, reasoning_chain: list, is_returnless: bool = False) -> str:
    """Generate a template-based explanation without LLM (fallback)."""
    # Find top 3 signals by weighted impact
    sorted_signals = sorted(reasoning_chain, key=lambda s: abs(s.get("weighted", 0)), reverse=True)
    top_3 = sorted_signals[:3]

    parts = []
    for s in top_3:
        if s.get("signal") == "circuit_breaker":
            continue
        parts.append(f"{s['signal']}: {s['detail']} (impact: {s['weighted']:+.1f})")

    decision_text = {
        "AUTO_APPROVE": "Auto-approved" + (" (returnless — amount below ₹500 threshold)" if is_returnless else " (return pickup will be scheduled)"),
        "INVESTIGATE": "Under investigation — agent is gathering more information",
        "ESCALATE": "Escalated to human review — high-risk signals detected",
    }.get(decision, decision)

    return f"Score: {risk_score}/100 → {decision_text}. Key factors: {'; '.join(parts)}"
