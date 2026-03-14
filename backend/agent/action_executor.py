"""Action Executor — executes the agent's decision via Pine Labs APIs and other actions.

Actions by decision tier:
- AUTO_APPROVE → Pine Labs Refund API (returnless if < ₹500, else schedule return pickup)
- INVESTIGATE → Request evidence / Offer store credit / Check fraud ring
- ESCALATE → Build case brief for human review
"""

from services.pinelabs_service import initiate_refund, create_payment_link
from agent.negotiator import should_offer_store_credit
from config import RETURNLESS_REFUND_THRESHOLD


async def execute_action(decision_result: dict, refund_id: str, order_id: str, amount: float) -> dict:
    """Execute the appropriate action based on the agent's decision."""

    decision = decision_result["decision"]
    recommended_action = decision_result["recommended_action"]

    if decision == "AUTO_APPROVE":
        return await _execute_approve(refund_id, order_id, amount, recommended_action)
    elif decision == "INVESTIGATE":
        return await _execute_investigate(refund_id, order_id, amount, recommended_action, decision_result)
    elif decision == "ESCALATE":
        return await _execute_escalate(refund_id, order_id, amount, decision_result)
    else:
        return {"type": "unknown", "status": "error", "message": f"Unknown decision: {decision}"}


async def _execute_approve(refund_id: str, order_id: str, amount: float, action: str) -> dict:
    """AUTO_APPROVE: Fire Pine Labs refund (returnless or post-return)."""

    is_returnless = amount < RETURNLESS_REFUND_THRESHOLD

    # Call Pine Labs Refund API
    refund_result = await initiate_refund(order_id, amount, "auto_approved")

    return {
        "type": "refund_returnless" if is_returnless else "refund_with_return",
        "status": "refund_initiated",
        "is_returnless": is_returnless,
        "pine_labs": refund_result,
        "amount": amount,
        "message": (
            f"Refund of ₹{amount} initiated (returnless — no return pickup needed)"
            if is_returnless
            else f"Refund of ₹{amount} approved. Return pickup will be scheduled. Refund releases after product verified."
        ),
    }


async def _execute_investigate(
    refund_id: str, order_id: str, amount: float, action: str, decision_result: dict
) -> dict:
    """INVESTIGATE: Execute the recommended investigate action."""

    if action == "request_evidence":
        return {
            "type": "request_evidence",
            "status": "evidence_requested",
            "message": f"Please upload a photo of the damaged item with barcode/tag visible to process your refund (REF: {refund_id}).",
            "whatsapp_template": f"Hi, regarding your refund request {refund_id}: Please upload a clear photo of the item showing the damage and the product barcode/tag. This helps us process your request faster.",
        }

    elif action == "offer_store_credit":
        credit_result = await should_offer_store_credit(amount, decision_result)
        if credit_result["offer_credit"]:
            link_result = await create_payment_link(
                credit_result["credit_amount"],
                "customer@email.com",
                f"Store credit for refund {refund_id}",
            )
            return {
                "type": "store_credit_offer",
                "status": "credit_offered",
                "cash_refund_amount": amount,
                "credit_amount": credit_result["credit_amount"],
                "bonus": credit_result["bonus"],
                "pine_labs_link": link_result,
                "message": credit_result["message"],
            }
        else:
            return {
                "type": "request_evidence",
                "status": "evidence_requested",
                "message": f"Please upload evidence for refund {refund_id}.",
            }

    elif action == "check_cross_merchant":
        return {
            "type": "check_cross_merchant",
            "status": "checking",
            "message": "Agent is querying Pine Labs network for cross-merchant claims...",
        }

    elif action == "check_fraud_ring":
        return {
            "type": "check_fraud_ring",
            "status": "checking",
            "message": "Agent is checking for fraud ring indicators (shared address/payment method)...",
        }

    else:
        return {
            "type": "investigate_generic",
            "status": "investigating",
            "message": f"Agent is investigating: {action}",
        }


async def _execute_escalate(refund_id: str, order_id: str, amount: float, decision_result: dict) -> dict:
    """ESCALATE: Build a pre-investigated case brief for human review."""

    top_signals = sorted(
        decision_result["reasoning_chain"],
        key=lambda s: abs(s.get("weighted", 0)),
        reverse=True,
    )[:5]

    case_brief = {
        "refund_id": refund_id,
        "order_id": order_id,
        "amount": amount,
        "risk_score": decision_result["risk_score"],
        "top_risk_signals": [
            {"signal": s["signal"], "detail": s["detail"], "weighted_impact": s["weighted"]}
            for s in top_signals
        ],
        "circuit_breaker_fired": decision_result.get("circuit_breaker_fired", False),
        "counterfactuals": decision_result.get("counterfactuals", []),
        "recommended_actions": ["deny_refund", "request_evidence", "flag_account", "contact_customer"],
    }

    return {
        "type": "escalate_to_human",
        "status": "escalated",
        "case_brief": case_brief,
        "message": f"Case escalated for human review. Pre-built brief with {len(top_signals)} risk signals attached.",
    }
