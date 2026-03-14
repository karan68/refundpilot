from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.schemas import RefundRequest, RefundDecision
from models.database import get_db
from agent.orchestrator import process_refund
from datetime import datetime
import json
import uuid
import traceback

router = APIRouter(prefix="/api/refund", tags=["refund"])


@router.post("")
async def submit_refund(request: RefundRequest):
    """Submit a new refund request — agent processes it immediately."""
    db = await get_db()

    refund_id = f"REF-{uuid.uuid4().hex[:6].upper()}"

    # Validate order exists and belongs to customer
    cursor = await db.execute(
        "SELECT * FROM orders WHERE id = ? AND customer_id = ?",
        (request.order_id, request.customer_id),
    )
    order = await cursor.fetchone()
    if not order:
        await db.close()
        return {"error": "Order not found or does not belong to this customer"}

    order_amount = dict(order)["amount"]

    # Save refund request as pending
    await db.execute(
        """INSERT INTO refunds (id, order_id, customer_id, amount, reason, message, language, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            refund_id,
            request.order_id,
            request.customer_id,
            order_amount,
            request.reason.value,
            request.message,
            request.language,
            "pending",
        ),
    )
    await db.commit()
    await db.close()

    # Run agent orchestrator
    try:
        result = await process_refund(
            customer_id=request.customer_id,
            order_id=request.order_id,
            reason=request.reason.value,
            message=request.message,
            refund_id=refund_id,
            language=request.language,
        )
    except Exception as e:
        print(f"❌ Agent error: {e}")
        traceback.print_exc()
        return {
            "refund_id": refund_id,
            "error": str(e),
            "status": "pending",
        }

    # Update refund record with agent decision
    db = await get_db()
    status_map = {
        "AUTO_APPROVE": "approved",
        "INVESTIGATE": "investigating",
        "ESCALATE": "escalated",
    }
    await db.execute(
        """UPDATE refunds SET risk_score = ?, decision = ?, confidence = ?,
           reasoning_json = ?, processing_time_ms = ?, status = ?,
           action_type = ?
           WHERE id = ?""",
        (
            result["risk_score"],
            result["decision"],
            result["confidence"],
            json.dumps(result["reasoning_chain"]),
            result["processing_time_ms"],
            status_map.get(result["decision"], "pending"),
            result["recommended_action"],
            refund_id,
        ),
    )
    await db.commit()

    # Log to audit trail
    await db.execute(
        """INSERT INTO audit_logs (refund_id, event_type, detail)
           VALUES (?, ?, ?)""",
        (
            refund_id,
            f"decision_{result['decision'].lower()}",
            json.dumps({
                "risk_score": result["risk_score"],
                "decision": result["decision"],
                "explanation": result["explanation"],
                "processing_time_ms": result["processing_time_ms"],
            }),
        ),
    )
    await db.commit()
    await db.close()

    return {
        "refund_id": refund_id,
        "risk_score": result["risk_score"],
        "decision": result["decision"],
        "confidence": result["confidence"],
        "processing_time_ms": result["processing_time_ms"],
        "reasoning_chain": result["reasoning_chain"],
        "explanation": result["explanation"],
        "counterfactuals": result["counterfactuals"],
        "recommended_action": result["recommended_action"],
        "react_steps": result.get("react_steps", []),
        "action": result["action"],
        "fraud_ring": result["fraud_ring"],
        "seasonal": result["seasonal"],
        "is_cold_start": result["is_cold_start"],
        "circuit_breaker_fired": result["circuit_breaker_fired"],
        "signals": result["signals"],
    }


@router.get("/{refund_id}")
async def get_refund(refund_id: str):
    """Get refund details by ID."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM refunds WHERE id = ?", (refund_id,))
    refund = await cursor.fetchone()
    await db.close()

    if not refund:
        return {"error": "Refund not found"}
    return dict(refund)


@router.get("")
async def list_refunds(limit: int = 50):
    """List recent refunds."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM refunds ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    refunds = [dict(row) for row in await cursor.fetchall()]
    await db.close()
    return refunds
