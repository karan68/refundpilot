"""Action Executor — executes the agent's decision via Pine Labs APIs.

End-to-end Pine Labs integration:
- AUTO_APPROVE → Create Pine Labs Order → Attempt Refund → Payment Link as receipt
- INVESTIGATE → Request evidence / Offer store credit (real Pine Labs Payment Link)
- ESCALATE → Create Pine Labs Order (for tracking) → Build case brief
"""

from services.pinelabs_service import initiate_refund, create_payment_link, create_order
from agent.negotiator import should_offer_store_credit
from config import RETURNLESS_REFUND_THRESHOLD
import uuid


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
    """AUTO_APPROVE: Create Pine Labs order → attempt refund → show result."""

    is_returnless = amount < RETURNLESS_REFUND_THRESHOLD

    # Step 1: Create a Pine Labs order for this refund (real API call)
    pl_order = await create_order(
        amount=amount,
        customer_name="RefundPilot Customer",
        customer_email="refund@refundpilot.demo",
        reference=f"rp-{refund_id}",
    )

    # Step 2: Attempt refund against the Pine Labs order
    pl_order_id = pl_order.get("order_id", order_id)
    refund_result = await initiate_refund(pl_order_id, amount, "auto_approved_by_refundpilot")

    return {
        "type": "refund_returnless" if is_returnless else "refund_with_return",
        "status": "refund_initiated",
        "is_returnless": is_returnless,
        "pine_labs_order": pl_order,
        "pine_labs": refund_result,
        "amount": amount,
        "message": (
            f"Refund of ₹{amount} initiated (returnless — no return pickup needed). Pine Labs order: {pl_order_id}"
            if is_returnless
            else f"Refund of ₹{amount} approved. Pine Labs order created: {pl_order_id}. Return pickup will be scheduled."
        ),
    }


async def _execute_investigate(
    refund_id: str, order_id: str, amount: float, action: str, decision_result: dict
) -> dict:
    """INVESTIGATE: Execute the recommended investigate action with Pine Labs integration."""

    if action == "request_evidence":
        return {
            "type": "request_evidence",
            "status": "evidence_requested",
            "message": f"Please upload a photo of the damaged item with barcode/tag visible to process your refund (REF: {refund_id}).",
            "whatsapp_template": f"Hi, regarding your refund request {refund_id}: Please upload a clear photo showing the damage and the product barcode/tag.",
        }

    elif action == "offer_store_credit":
        credit_result = await should_offer_store_credit(amount, decision_result)
        if credit_result["offer_credit"]:
            # Create REAL Pine Labs Payment Link for store credit
            link_result = await create_payment_link(
                credit_result["credit_amount"],
                "customer@refundpilot.demo",
                f"RefundPilot store credit — ₹{credit_result['credit_amount']} (₹{amount} + ₹{credit_result['bonus']} bonus) for {refund_id}",
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
    """ESCALATE: Create Pine Labs order for tracking + build case brief."""

    # Create Pine Labs order so the escalated case has a PL reference
    pl_order = await create_order(
        amount=amount,
        customer_name="Escalated Case",
        customer_email="escalated@refundpilot.demo",
        reference=f"rp-esc-{refund_id}",
    )

    top_signals = sorted(
        decision_result["reasoning_chain"],
        key=lambda s: abs(s.get("weighted", 0)),
        reverse=True,
    )[:5]

    case_brief = {
        "refund_id": refund_id,
        "order_id": order_id,
        "pine_labs_order_id": pl_order.get("order_id", ""),
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
        "pine_labs_order": pl_order,
        "case_brief": case_brief,
        "message": f"Case escalated. Pine Labs order {pl_order.get('order_id', '')} created for tracking. Pre-built brief with {len(top_signals)} risk signals.",
    }
