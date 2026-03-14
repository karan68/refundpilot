from fastapi import APIRouter
from pydantic import BaseModel
from models.schemas import MerchantQueryRequest, MerchantQueryResponse
from services.nl_query_service import process_nl_query
from models.database import get_db
import uuid

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query")
async def merchant_query(request: MerchantQueryRequest):
    """Natural language merchant query — powered by regex intent matching."""
    result = await process_nl_query(request.query)
    return MerchantQueryResponse(
        answer=result["answer"],
        data=result.get("data"),
    )


# F25: Conversational Commerce — free-text refund submission
class ChatRefundRequest(BaseModel):
    message: str
    language: str = "en"


class ChatRefundResponse(BaseModel):
    parsed: dict | None = None
    message: str = ""
    refund_submitted: bool = False
    refund_id: str | None = None


# Keyword-based extraction (Bedrock can be added later for smarter parsing)
REASON_KEYWORDS = {
    "damaged": "damaged_in_transit",
    "damage": "damaged_in_transit",
    "broken": "damaged_in_transit",
    "torn": "damaged_in_transit",
    "crushed": "damaged_in_transit",
    "wrong": "wrong_product",
    "different": "wrong_product",
    "defective": "defective",
    "not working": "defective",
    "doesnt work": "defective",
    "size": "size_issue",
    "small": "size_issue",
    "large": "size_issue",
    "tight": "size_issue",
    "loose": "size_issue",
    "not delivered": "not_delivered",
    "didnt receive": "not_delivered",
    "never got": "not_delivered",
    "changed mind": "changed_mind",
    "dont want": "changed_mind",
    # Hindi
    "tuta": "damaged_in_transit",
    "kharab": "defective",
    "galat": "wrong_product",
    "nahi mila": "not_delivered",
    "nahi aaya": "not_delivered",
    "chhota": "size_issue",
    "bada": "size_issue",
}

import re

def _extract_order_id(text: str) -> str | None:
    """Extract order ID from free text."""
    match = re.search(r'ORD-\d+', text, re.IGNORECASE)
    return match.group(0) if match else None


def _extract_customer_id(text: str) -> str | None:
    """Extract customer ID from free text."""
    match = re.search(r'CUST-\d+', text, re.IGNORECASE)
    return match.group(0) if match else None


def _extract_reason(text: str) -> str:
    """Extract refund reason from free text using keyword matching."""
    text_lower = text.lower()
    for keyword, reason in REASON_KEYWORDS.items():
        if keyword in text_lower:
            return reason
    return "other"


@router.post("/chat/refund")
async def chat_refund(request: ChatRefundRequest):
    """F25: Conversational refund submission — parse free text into refund request."""
    text = request.message

    order_id = _extract_order_id(text)
    customer_id = _extract_customer_id(text)
    reason = _extract_reason(text)

    if not order_id or not customer_id:
        return ChatRefundResponse(
            parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason},
            message="I couldn't find the order ID or customer ID in your message. Please include them like: 'CUST-001 wants refund for ORD-1001, kurta was damaged'",
            refund_submitted=False,
        )

    # Validate order exists
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM orders WHERE id = ? AND customer_id = ?",
        (order_id, customer_id),
    )
    order = await cursor.fetchone()
    if not order:
        await db.close()
        return ChatRefundResponse(
            parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason},
            message=f"Order {order_id} not found for customer {customer_id}.",
            refund_submitted=False,
        )

    order = dict(order)

    # Submit the refund via the orchestrator
    from agent.orchestrator import process_refund

    refund_id = f"REF-{uuid.uuid4().hex[:6].upper()}"

    await db.execute(
        """INSERT INTO refunds (id, order_id, customer_id, amount, reason, message, language, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (refund_id, order_id, customer_id, order["amount"], reason, text, request.language, "pending"),
    )
    await db.commit()
    await db.close()

    result = await process_refund(
        customer_id=customer_id,
        order_id=order_id,
        reason=reason,
        message=text,
        refund_id=refund_id,
        language=request.language,
    )

    # Update DB with decision
    db = await get_db()
    import json
    status_map = {"AUTO_APPROVE": "approved", "INVESTIGATE": "investigating", "ESCALATE": "escalated"}
    await db.execute(
        """UPDATE refunds SET risk_score=?, decision=?, confidence=?, reasoning_json=?,
           processing_time_ms=?, status=?, action_type=? WHERE id=?""",
        (result["risk_score"], result["decision"], result["confidence"],
         json.dumps(result["reasoning_chain"]), result["processing_time_ms"],
         status_map.get(result["decision"], "pending"), result["recommended_action"], refund_id),
    )
    await db.commit()
    await db.close()

    return ChatRefundResponse(
        parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason, "amount": order["amount"]},
        message=f"Refund processed! Score: {result['risk_score']}/100 → {result['decision']}. {result['explanation'][:200]}",
        refund_submitted=True,
        refund_id=refund_id,
    )
