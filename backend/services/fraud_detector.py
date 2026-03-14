"""Fraud Detector — F20 fraud ring detection + behavioral profiling.

F20: Detects fraud rings by finding multiple customer accounts
sharing the same shipping address that have recent refunds.
"""

from models.database import get_db
from datetime import datetime, timedelta


async def check_fraud_ring(customer_id: str, order_id: str) -> dict:
    """F20: Check if this customer's shipping address is linked to other accounts with recent refunds.

    Query: Find all other customer_ids who have orders shipped to the same address
    AND have filed refunds in the last 30 days.
    """
    db = await get_db()

    # Get the shipping address for this order
    cursor = await db.execute(
        "SELECT shipping_address FROM orders WHERE id = ?", (order_id,)
    )
    row = await cursor.fetchone()
    if not row or not row["shipping_address"]:
        await db.close()
        return {"ring_detected": False, "linked_accounts": [], "message": "No shipping address on record"}

    address = row["shipping_address"]

    # Find other customers with orders at the same address who have recent refunds
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor = await db.execute(
        """SELECT DISTINCT o.customer_id, c.name, COUNT(r.id) as refund_count
           FROM orders o
           JOIN customers c ON o.customer_id = c.id
           JOIN refunds r ON r.customer_id = o.customer_id
           WHERE o.shipping_address = ?
             AND o.customer_id != ?
             AND r.created_at >= ?
           GROUP BY o.customer_id""",
        (address, customer_id, cutoff),
    )
    linked = [dict(row) for row in await cursor.fetchall()]
    await db.close()

    if not linked:
        return {
            "ring_detected": False,
            "linked_accounts": [],
            "address": address,
            "message": "No other accounts with recent refunds at this address",
        }

    return {
        "ring_detected": True,
        "linked_accounts": [
            {"customer_id": l["customer_id"], "name": l["name"], "refund_count": l["refund_count"]}
            for l in linked
        ],
        "total_linked": len(linked),
        "address": address,
        "message": f"FRAUD RING: {len(linked)} other account(s) at same address ({address}) filed refunds in last 30 days: {', '.join(l['name'] for l in linked)}",
    }


async def get_customer_rfm_profile(customer_id: str) -> dict:
    """Get full RFM profile for a customer — used for dashboard fraud profiling."""
    db = await get_db()

    cursor = await db.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = dict(await cursor.fetchone())

    cursor = await db.execute(
        "SELECT * FROM refunds WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,),
    )
    refunds = [dict(row) for row in await cursor.fetchall()]

    cursor = await db.execute(
        "SELECT SUM(amount) as total FROM orders WHERE customer_id = ?", (customer_id,)
    )
    total_purchased = (await cursor.fetchone())["total"] or 0

    cursor = await db.execute(
        "SELECT * FROM cross_merchant_claims WHERE customer_id = ?", (customer_id,)
    )
    cross_merchant = [dict(row) for row in await cursor.fetchall()]

    await db.close()

    total_refunded = sum(r.get("amount", 0) for r in refunds)
    now = datetime.now()

    # RFM calculations
    if refunds:
        try:
            last_date = datetime.strptime(refunds[0]["created_at"][:10], "%Y-%m-%d")
            recency_days = (now - last_date).days
        except (ValueError, TypeError):
            recency_days = 999
    else:
        recency_days = 999

    cutoff_90 = now - timedelta(days=90)
    frequency_90d = sum(
        1 for r in refunds
        if r.get("created_at") and datetime.strptime(r["created_at"][:10], "%Y-%m-%d") >= cutoff_90
    )

    monetary_ratio = total_refunded / max(total_purchased, 1)

    return {
        "customer_id": customer_id,
        "name": customer["name"],
        "customer_type": customer["customer_type"],
        "total_orders": customer["total_orders"],
        "total_refunds": customer["total_refunds"],
        "refund_rate": customer["refund_rate"],
        "rfm": {
            "recency_days": recency_days,
            "frequency_90d": frequency_90d,
            "monetary_ratio": round(monetary_ratio, 4),
            "total_refunded": total_refunded,
            "total_purchased": total_purchased,
        },
        "cross_merchant_claims": len(cross_merchant),
        "cross_merchant_details": cross_merchant,
    }