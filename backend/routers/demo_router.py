"""Demo Router — pre-built demo scenarios for hackathon presentation.

3 scenarios that can be triggered with one click:
1. Priya (loyal) → AUTO_APPROVE in ~3s
2. Vikram (suspect) → INVESTIGATE with ReAct loop
3. Rohit (abuser) → ESCALATE with fraud ring + case brief
"""

from fastapi import APIRouter
from agent.orchestrator import process_refund

router = APIRouter(prefix="/api/demo", tags=["demo"])

SCENARIOS = {
    "priya": {
        "customer_id": "CUST-001",
        "order_id": "ORD-1001",
        "reason": "damaged_in_transit",
        "message": "My Cotton Kurta arrived with a tear on the sleeve. Very disappointed.",
        "language": "en",
        "label": "Priya Sharma — Loyal Customer",
        "expected": "AUTO_APPROVE",
    },
    "vikram": {
        "customer_id": "CUST-004",
        "order_id": "ORD-4001",
        "reason": "not_as_described",
        "message": "These shoes don't match the description at all. Color is different.",
        "language": "en",
        "label": "Vikram Singh — Suspect",
        "expected": "INVESTIGATE",
    },
    "rohit": {
        "customer_id": "CUST-002",
        "order_id": "ORD-2001",
        "reason": "damaged_in_transit",
        "message": "Shoes were damaged in transit, completely unusable",
        "language": "en",
        "label": "Rohit Mehta — Serial Abuser",
        "expected": "ESCALATE",
    },
}


@router.get("/scenarios")
async def list_scenarios():
    """List available demo scenarios."""
    return {
        name: {"label": s["label"], "expected": s["expected"], "order_id": s["order_id"]}
        for name, s in SCENARIOS.items()
    }


@router.post("/run/{scenario}")
async def run_scenario(scenario: str):
    """Run a pre-built demo scenario — triggers the full agent pipeline."""
    if scenario not in SCENARIOS:
        return {"error": f"Unknown scenario: {scenario}. Available: {list(SCENARIOS.keys())}"}

    s = SCENARIOS[scenario]

    # Save refund first
    from models.database import get_db
    import uuid, json

    db = await get_db()
    refund_id = f"REF-DEMO-{scenario.upper()}"

    # Delete previous demo refund for this scenario (allow re-running)
    await db.execute("DELETE FROM refunds WHERE id = ?", (refund_id,))

    # Get order amount
    cursor = await db.execute("SELECT amount FROM orders WHERE id = ?", (s["order_id"],))
    order = await cursor.fetchone()
    amount = dict(order)["amount"] if order else 0

    await db.execute(
        """INSERT INTO refunds (id, order_id, customer_id, amount, reason, message, language, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (refund_id, s["order_id"], s["customer_id"], amount, s["reason"], s["message"], s["language"], "pending"),
    )
    await db.commit()
    await db.close()

    # Run agent
    result = await process_refund(
        customer_id=s["customer_id"],
        order_id=s["order_id"],
        reason=s["reason"],
        message=s["message"],
        refund_id=refund_id,
        language=s["language"],
    )

    # Update DB
    db = await get_db()
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

    return {
        "scenario": scenario,
        "label": s["label"],
        "expected": s["expected"],
        **result,
    }
