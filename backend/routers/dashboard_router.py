from fastapi import APIRouter
from models.database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """Aggregate dashboard stats across all refunds."""
    db = await get_db()

    # Total refunds
    cursor = await db.execute("SELECT COUNT(*) FROM refunds")
    total = (await cursor.fetchone())[0]

    # By decision
    cursor = await db.execute("SELECT COUNT(*) FROM refunds WHERE decision = 'AUTO_APPROVE'")
    auto_approved = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM refunds WHERE decision = 'INVESTIGATE'")
    investigated = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM refunds WHERE decision = 'ESCALATE'")
    escalated = (await cursor.fetchone())[0]

    # Average processing time
    cursor = await db.execute("SELECT AVG(processing_time_ms) FROM refunds WHERE processing_time_ms IS NOT NULL")
    avg_time = (await cursor.fetchone())[0] or 0

    # Total refund amount
    cursor = await db.execute("SELECT SUM(amount) FROM refunds")
    total_amount = (await cursor.fetchone())[0] or 0

    # Fraud savings (escalated refund amounts that were blocked)
    cursor = await db.execute("SELECT SUM(amount) FROM refunds WHERE decision = 'ESCALATE'")
    fraud_savings = (await cursor.fetchone())[0] or 0

    await db.close()

    auto_approve_rate = (auto_approved / total * 100) if total > 0 else 0

    return {
        "total_refunds": total,
        "auto_approved": auto_approved,
        "investigated": investigated,
        "escalated": escalated,
        "avg_processing_time_ms": round(avg_time, 0),
        "fraud_savings": fraud_savings,
        "auto_approve_rate": round(auto_approve_rate, 1),
        "total_refund_amount": total_amount,
    }


@router.get("/refunds")
async def get_recent_refunds(limit: int = 20):
    """Get recent refunds with customer info for dashboard."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT r.*, c.name as customer_name, c.customer_type
           FROM refunds r
           JOIN customers c ON r.customer_id = c.id
           ORDER BY r.created_at DESC LIMIT ?""",
        (limit,),
    )
    refunds = [dict(row) for row in await cursor.fetchall()]
    await db.close()
    return refunds


@router.get("/customers")
async def get_customers():
    """Get all customer profiles for dashboard."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM customers ORDER BY refund_rate DESC")
    customers = [dict(row) for row in await cursor.fetchall()]
    await db.close()
    return customers


@router.get("/customers/{customer_id}")
async def get_customer_detail(customer_id: str):
    """Get customer profile with their refund history."""
    db = await get_db()

    cursor = await db.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = await cursor.fetchone()
    if not customer:
        await db.close()
        return {"error": "Customer not found"}

    cursor = await db.execute(
        "SELECT * FROM refunds WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,),
    )
    refunds = [dict(row) for row in await cursor.fetchall()]

    cursor = await db.execute(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC",
        (customer_id,),
    )
    orders = [dict(row) for row in await cursor.fetchall()]

    await db.close()

    return {
        "customer": dict(customer),
        "refunds": refunds,
        "orders": orders,
    }
