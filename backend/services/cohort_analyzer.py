"""Cohort Analyzer — refund clustering by product, region, timeframe.

Surfaces root causes: "SKU#4421 has 22% refund rate — quality issue, not fraud."
"""

from models.database import get_db


async def get_product_cohorts() -> list[dict]:
    """Group refunds by product SKU and compute refund rates."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT p.sku, p.name, p.category, p.expected_refund_rate,
                  COUNT(DISTINCT o.id) as total_orders,
                  COUNT(DISTINCT r.id) as total_refunds,
                  ROUND(COUNT(DISTINCT r.id) * 100.0 / MAX(COUNT(DISTINCT o.id), 1), 1) as actual_refund_pct,
                  SUM(r.amount) as total_refund_amount
           FROM products p
           LEFT JOIN orders o ON p.sku = o.product_sku
           LEFT JOIN refunds r ON o.id = r.order_id
           GROUP BY p.sku
           ORDER BY actual_refund_pct DESC"""
    )
    cohorts = []
    for row in await cursor.fetchall():
        row = dict(row)
        expected = row["expected_refund_rate"] * 100
        actual = row["actual_refund_pct"] or 0
        is_anomaly = actual > expected * 2

        row["is_anomaly"] = is_anomaly
        row["insight"] = (
            f"{row['name']} has {actual}% refund rate vs {expected:.0f}% expected — {'possible quality issue' if is_anomaly else 'within normal range'}"
        )
        cohorts.append(row)

    await db.close()
    return cohorts


async def get_city_cohorts() -> list[dict]:
    """Group refunds by customer city."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT c.city, COUNT(r.id) as refund_count, SUM(r.amount) as total_amount,
                  COUNT(DISTINCT r.customer_id) as unique_customers,
                  ROUND(AVG(r.risk_score), 1) as avg_risk_score
           FROM refunds r JOIN customers c ON r.customer_id = c.id
           WHERE r.risk_score IS NOT NULL
           GROUP BY c.city ORDER BY refund_count DESC"""
    )
    rows = [dict(r) for r in await cursor.fetchall()]
    await db.close()
    return rows


async def get_reason_cohorts() -> list[dict]:
    """Group refunds by reason."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT reason, COUNT(*) as count, SUM(amount) as total,
                  ROUND(AVG(risk_score), 1) as avg_score,
                  SUM(CASE WHEN decision = 'ESCALATE' THEN 1 ELSE 0 END) as escalated
           FROM refunds WHERE risk_score IS NOT NULL
           GROUP BY reason ORDER BY count DESC"""
    )
    rows = [dict(r) for r in await cursor.fetchall()]
    await db.close()
    return rows