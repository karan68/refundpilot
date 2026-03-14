from fastapi import APIRouter
from pydantic import BaseModel
from models.schemas import MerchantQueryRequest, MerchantQueryResponse
from services.nl_query_service import process_nl_query
from models.database import get_db
import uuid
import re

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
    decision: str | None = None
    case_status: str | None = None
    risk_score: int | None = None


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

def _extract_order_id(text: str) -> str | None:
    """Extract order ID from free text."""
    match = re.search(r'ORD-\d+', text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _extract_customer_id(text: str) -> str | None:
    """Extract customer ID from free text."""
    match = re.search(r'CUST-\d+', text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _extract_product_sku(text: str) -> str | None:
    """Extract product SKU from free text."""
    match = re.search(r'\b(?!(?:CUST)-)[A-Z]{4,5}-\d{3}\b', text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _extract_reason(text: str) -> str:
    """Extract refund reason from free text using keyword matching."""
    text_lower = text.lower()
    for keyword, reason in REASON_KEYWORDS.items():
        if keyword in text_lower:
            return reason
    return "other"


async def _fetch_recent_orders(db, customer_id: str, limit: int = 5) -> list[dict]:
    cursor = await db.execute(
        """SELECT id, product_sku, product_name, amount, order_date
           FROM orders
           WHERE customer_id = ?
           ORDER BY order_date DESC
           LIMIT ?""",
        (customer_id, limit),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


def _format_order_list(orders: list[dict]) -> str:
    if not orders:
        return "No recent orders found for this account."
    return "\n".join(
        f"- {order['id']} | {order['product_sku']} | {order['product_name']} | Rs {order['amount']}"
        for order in orders
    )


def _build_chat_resolution(result: dict, refund_id: str) -> tuple[bool, str]:
    decision = result["decision"]
    risk_score = result["risk_score"]
    explanation = result["explanation"][:220]
    action_message = result.get("action", {}).get("message")

    if decision == "AUTO_APPROVE":
        return True, f"Refund approved and initiated for {refund_id}. Score: {risk_score}/100 -> {decision}. {explanation}"

    workflow_text = {
        "INVESTIGATE": "Refund request logged and moved to investigation",
        "ESCALATE": "Refund request logged and escalated to human review",
    }.get(decision, "Refund request logged")

    message = f"{workflow_text} as {refund_id}. Score: {risk_score}/100 -> {decision}. {explanation}"
    if action_message:
        message += f" Next step: {action_message}"

    return False, message


@router.post("/chat/refund")
async def chat_refund(request: ChatRefundRequest):
    """F25: Conversational refund submission — parse free text into refund request."""
    text = request.message

    order_id = _extract_order_id(text)
    customer_id = _extract_customer_id(text)
    product_sku = _extract_product_sku(text)
    reason = _extract_reason(text)

    if not customer_id:
        reason_text = reason.replace("_", " ") if reason != "other" else "your issue"
        return ChatRefundResponse(
            parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason, "product_sku": product_sku},
            message=f"I understand the issue with {reason_text}. Please choose a customer first so I can validate the claim against the correct purchase history.",
            refund_submitted=False,
        )

    db = await get_db()
    recent_orders = await _fetch_recent_orders(db, customer_id)

    if not order_id and not product_sku:
        await db.close()
        return ChatRefundResponse(
            parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason, "product_sku": product_sku},
            message=(
                "Tell me which item this refund is about. Pick one of the customer's recent purchases, "
                "or send an order ID like ORD-1001 or an item SKU like FASH-001.\n\n"
                f"Recent purchases for {customer_id}:\n{_format_order_list(recent_orders)}"
            ),
            refund_submitted=False,
        )

    order = None

    if product_sku and not order_id:
        cursor = await db.execute(
            """SELECT * FROM orders
               WHERE customer_id = ? AND product_sku = ?
               ORDER BY order_date DESC""",
            (customer_id, product_sku),
        )
        matching_orders = [dict(row) for row in await cursor.fetchall()]

        if not matching_orders:
            await db.close()
            return ChatRefundResponse(
                parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason, "product_sku": product_sku},
                message=(
                    f"I could not match {product_sku} to {customer_id}'s purchase history. "
                    "Please choose one of the recent purchases below or send a valid order ID.\n\n"
                    f"Recent purchases for {customer_id}:\n{_format_order_list(recent_orders)}"
                ),
                refund_submitted=False,
            )

        if len(matching_orders) > 1:
            await db.close()
            return ChatRefundResponse(
                parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason, "product_sku": product_sku},
                message=(
                    f"{customer_id} bought {product_sku} more than once. "
                    "Send the exact order ID for the purchase you want to refund.\n\n"
                    f"Matching purchases:\n{_format_order_list(matching_orders[:5])}"
                ),
                refund_submitted=False,
            )

        order = matching_orders[0]
        order_id = order["id"]

    if not order:
        cursor = await db.execute(
            "SELECT * FROM orders WHERE id = ? AND customer_id = ?",
            (order_id, customer_id),
        )
        order_row = await cursor.fetchone()
        if not order_row:
            await db.close()
            return ChatRefundResponse(
                parsed={"order_id": order_id, "customer_id": customer_id, "reason": reason, "product_sku": product_sku},
                message=(
                    f"I could not find {order_id} in {customer_id}'s purchase history. "
                    "Please pick a valid order from the recent purchases below or use another order ID or item SKU.\n\n"
                    f"Recent purchases for {customer_id}:\n{_format_order_list(recent_orders)}"
                ),
                refund_submitted=False,
            )
        order = dict(order_row)

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

    refund_submitted, response_message = _build_chat_resolution(result, refund_id)
    case_status = status_map.get(result["decision"], "pending")

    return ChatRefundResponse(
        parsed={
            "order_id": order_id,
            "customer_id": customer_id,
            "reason": reason,
            "product_sku": order["product_sku"],
            "amount": order["amount"],
        },
        message=response_message,
        refund_submitted=refund_submitted,
        refund_id=refund_id,
        decision=result["decision"],
        case_status=case_status,
        risk_score=result["risk_score"],
    )
