from fastapi import APIRouter
from models.database import get_db
from services.alert_service import check_fraud_spikes
from services.cohort_analyzer import get_product_cohorts, get_city_cohorts, get_reason_cohorts
from services.fraud_similarity_service import get_fraud_similarity, compute_fraudster_centroid

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


@router.get("/alerts")
async def get_alerts():
    """Get fraud spike alerts."""
    alerts = await check_fraud_spikes()
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/cohorts/products")
async def get_product_cohort_data():
    """Get refund cohorts by product."""
    return await get_product_cohorts()


@router.get("/cohorts/cities")
async def get_city_cohort_data():
    """Get refund cohorts by city."""
    return await get_city_cohorts()


@router.get("/cohorts/reasons")
async def get_reason_cohort_data():
    """Get refund cohorts by reason."""
    return await get_reason_cohorts()


@router.get("/audit-log")
async def get_audit_log(limit: int = 50):
    """Get audit trail entries."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    logs = [dict(row) for row in await cursor.fetchall()]
    await db.close()
    return logs


@router.get("/reconciliation")
async def get_reconciliation():
    """F24: Get refund settlement status for reconciliation view."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT r.id, r.order_id, r.customer_id, r.amount, r.decision,
                  r.pine_labs_ref, r.settlement_status, r.status, r.created_at,
                  c.name as customer_name
           FROM refunds r JOIN customers c ON r.customer_id = c.id
           WHERE r.decision = 'AUTO_APPROVE'
           ORDER BY r.created_at DESC"""
    )
    refunds = [dict(row) for row in await cursor.fetchall()]
    await db.close()

    settled = sum(1 for r in refunds if r["settlement_status"] == "settled")
    pending = sum(1 for r in refunds if r["settlement_status"] == "pending")
    failed = sum(1 for r in refunds if r["settlement_status"] == "failed")

    return {
        "refunds": refunds,
        "summary": {"settled": settled, "pending": pending, "failed": failed, "total": len(refunds)},
    }


@router.get("/fraud-graph")
async def get_fraud_graph():
    """F27: Graph analytics — Customer ↔ Address network for fraud ring visualization."""
    db = await get_db()

    # Build nodes: customers + addresses
    cursor = await db.execute("SELECT id, name, customer_type, refund_rate FROM customers")
    customers = [dict(row) for row in await cursor.fetchall()]

    cursor = await db.execute(
        "SELECT DISTINCT shipping_address FROM orders WHERE shipping_address != ''"
    )
    addresses = [dict(row)["shipping_address"] for row in await cursor.fetchall()]

    # Build edges: customer → address (from orders)
    cursor = await db.execute(
        """SELECT DISTINCT customer_id, shipping_address FROM orders
           WHERE shipping_address != ''"""
    )
    edges_raw = [dict(row) for row in await cursor.fetchall()]

    await db.close()

    # Format for frontend graph visualization
    nodes = []
    for c in customers:
        nodes.append({
            "id": c["id"],
            "label": c["name"],
            "type": "customer",
            "group": c["customer_type"],
            "refund_rate": c["refund_rate"],
        })
    for addr in addresses:
        nodes.append({
            "id": f"addr_{hash(addr) % 10000}",
            "label": addr[:25] + ("..." if len(addr) > 25 else ""),
            "full_address": addr,
            "type": "address",
            "group": "address",
        })

    edges = []
    for e in edges_raw:
        edges.append({
            "source": e["customer_id"],
            "target": f"addr_{hash(e['shipping_address']) % 10000}",
        })

    # Detect rings (addresses with 2+ customers)
    addr_counts = {}
    for e in edges_raw:
        addr_counts.setdefault(e["shipping_address"], set()).add(e["customer_id"])
    rings = [
        {"address": addr, "customers": list(custs)}
        for addr, custs in addr_counts.items()
        if len(custs) >= 2
    ]

    return {"nodes": nodes, "edges": edges, "rings": rings}


@router.get("/fraud-similarity/{customer_id}")
async def get_customer_fraud_similarity(customer_id: str):
    """F26: Compute fraud similarity score for a customer."""
    from agent.signal_collector import collect_signals

    db = await get_db()
    # Get customer's most recent order for signal computation
    cursor = await db.execute(
        "SELECT id FROM orders WHERE customer_id = ? ORDER BY order_date DESC LIMIT 1",
        (customer_id,),
    )
    order = await cursor.fetchone()
    await db.close()

    if not order:
        return {"error": "No orders found for customer"}

    signals_data = await collect_signals(customer_id, order["id"], "damaged_in_transit", "")
    similarity = await get_fraud_similarity(signals_data["signals"])

    return {
        "customer_id": customer_id,
        "fraud_similarity": similarity,
    }
