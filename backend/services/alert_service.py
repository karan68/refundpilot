"""Alert Service — fraud spike detection and merchant alerts.

Detects suspicious patterns:
- N escalated refunds from same city in X hours
- Sudden spike in refund rate for a product
- New fraud ring detected
"""

from models.database import get_db
from datetime import datetime, timedelta


async def check_fraud_spikes() -> list[dict]:
    """Check for fraud spikes — clusters of suspicious refunds by city/time."""
    db = await get_db()
    alerts = []

    # Alert 1: Multiple escalated refunds from same city in last 24 hours
    cutoff = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    cursor = await db.execute(
        """SELECT c.city, COUNT(*) as count, SUM(r.amount) as total
           FROM refunds r JOIN customers c ON r.customer_id = c.id
           WHERE r.decision = 'ESCALATE' AND r.created_at >= ?
           GROUP BY c.city HAVING count >= 2
           ORDER BY count DESC""",
        (cutoff,),
    )
    for row in await cursor.fetchall():
        row = dict(row)
        alerts.append({
            "type": "city_spike",
            "severity": "high" if row["count"] >= 3 else "medium",
            "title": f"Fraud spike in {row['city']}",
            "message": f"{row['count']} escalated refunds from {row['city']} in last 24h, totaling ₹{row['total']:.0f}",
            "data": row,
        })

    # Alert 2: Products with abnormally high refund rate
    cursor = await db.execute(
        """SELECT p.sku, p.name, p.expected_refund_rate,
                  COUNT(r.id) as refund_count,
                  (SELECT COUNT(*) FROM orders WHERE product_sku = p.sku) as order_count
           FROM products p
           JOIN orders o ON p.sku = o.product_sku
           JOIN refunds r ON o.id = r.order_id
           GROUP BY p.sku
           HAVING CAST(refund_count AS REAL) / MAX(order_count, 1) > p.expected_refund_rate * 2"""
    )
    for row in await cursor.fetchall():
        row = dict(row)
        actual_rate = row["refund_count"] / max(row["order_count"], 1)
        alerts.append({
            "type": "product_defect",
            "severity": "medium",
            "title": f"High refund rate for {row['name']}",
            "message": f"{row['name']} ({row['sku']}) has {actual_rate*100:.0f}% refund rate vs {row['expected_refund_rate']*100:.0f}% expected — possible quality issue",
            "data": row,
        })

    # Alert 3: Fraud rings detected (addresses with 2+ refunding accounts)
    cursor = await db.execute(
        """SELECT o.shipping_address, COUNT(DISTINCT o.customer_id) as accounts
           FROM orders o
           JOIN refunds r ON r.customer_id = o.customer_id
           WHERE o.shipping_address != ''
           GROUP BY o.shipping_address HAVING accounts >= 2"""
    )
    for row in await cursor.fetchall():
        row = dict(row)
        alerts.append({
            "type": "fraud_ring",
            "severity": "high",
            "title": f"Fraud ring at {row['shipping_address'][:30]}...",
            "message": f"{row['accounts']} different accounts at same address have filed refunds",
            "data": row,
        })

    await db.close()
    return alerts