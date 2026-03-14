"""Signal Collector — gathers raw data AND computes all 10 signal scores."""

from models.database import get_db
from config import (
    DELIVERY_CONTRADICTIONS,
    AMOUNT_RISK_TIERS,
    RFM_RECENCY_WINDOW_DAYS,
    RFM_FREQUENCY_WINDOW_DAYS,
    RFM_FREQUENCY_THRESHOLD,
    CROSS_MERCHANT_WINDOW_DAYS,
    CROSS_MERCHANT_SCORES,
    CROSS_MERCHANT_SCORE_DEFAULT,
)
from datetime import datetime, timedelta


async def collect_signals(customer_id: str, order_id: str, reason: str, message: str) -> dict:
    """Fetch all data and compute 10 signal scores for the risk scorer."""
    db = await get_db()

    # ── Raw data queries ──
    cursor = await db.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = dict(await cursor.fetchone())

    cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = dict(await cursor.fetchone())

    cursor = await db.execute("SELECT * FROM products WHERE sku = ?", (order["product_sku"],))
    product = dict(await cursor.fetchone())

    cursor = await db.execute(
        "SELECT * FROM refunds WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,),
    )
    refund_history = [dict(row) for row in await cursor.fetchall()]

    cursor = await db.execute(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC",
        (customer_id,),
    )
    order_history = [dict(row) for row in await cursor.fetchall()]

    # Cross-merchant claims
    cursor = await db.execute(
        "SELECT * FROM cross_merchant_claims WHERE customer_id = ?",
        (customer_id,),
    )
    cross_merchant_claims = [dict(row) for row in await cursor.fetchall()]

    # Product-wide refund rate (for defect dampener F19)
    cursor = await db.execute(
        "SELECT COUNT(*) FROM refunds WHERE order_id IN (SELECT id FROM orders WHERE product_sku = ?)",
        (order["product_sku"],),
    )
    product_refund_count = (await cursor.fetchone())[0]
    cursor = await db.execute(
        "SELECT COUNT(*) FROM orders WHERE product_sku = ?",
        (order["product_sku"],),
    )
    product_order_count = (await cursor.fetchone())[0]

    await db.close()

    # ── Compute 10 signal scores ──
    now = datetime.now()

    # S1: Customer Refund Rate — min(refund_rate / 0.5, 1.0) × 100
    refund_rate = customer["refund_rate"]
    s1_raw = min(refund_rate / 0.5, 1.0) * 100

    # F19: Product defect dampener — if product refund rate > 2× expected, halve S1
    product_actual_rate = product_refund_count / max(product_order_count, 1)
    product_expected_rate = product["expected_refund_rate"]
    is_product_defect = product_actual_rate > (2 * product_expected_rate)
    if is_product_defect:
        s1_raw = s1_raw * 0.5

    # S2: Delivery Contradiction — lookup table
    delivery_status = order["delivery_status"]
    s2_raw = DELIVERY_CONTRADICTIONS.get((reason, delivery_status), 0)

    # S3: Amount Risk — tiered
    amount = order["amount"]
    s3_raw = 80  # default highest
    for threshold, score in AMOUNT_RISK_TIERS:
        if amount < threshold:
            s3_raw = score
            break

    # S4: Claim Pattern Repetition — min(same_reason_count / 3, 1.0) × 100
    same_reason_count = sum(1 for r in refund_history if r.get("reason") == reason)
    s4_raw = min(same_reason_count / 3, 1.0) * 100

    # Wardrobing timing heuristic: if Fashion + return_timing_ratio > 0.8 → S4 += 25
    if product["category"] == "Fashion" and order.get("delivery_date"):
        try:
            delivery_dt = datetime.strptime(order["delivery_date"], "%Y-%m-%d")
            days_since_delivery = (now - delivery_dt).days
            return_window = order.get("return_window_days", 15)
            if return_window > 0:
                timing_ratio = days_since_delivery / return_window
                if timing_ratio > 0.8:
                    s4_raw = min(s4_raw + 25, 100)
        except (ValueError, TypeError):
            pass

    # S5: Product Category Deviation — max((cust_rate - expected_rate) / expected_rate, 0) × 50
    if product_expected_rate > 0:
        s5_raw = max((refund_rate - product_expected_rate) / product_expected_rate, 0) * 50
    else:
        s5_raw = 0
    s5_raw = min(s5_raw, 100)

    # S6: Sentiment — keyword-based (LLM optional, Phase 2 uses keywords)
    from services.sentiment_analyzer import analyze_sentiment_keywords
    sentiment_result = analyze_sentiment_keywords(message)
    s6_raw = sentiment_result["score"]

    # S7: RFM Recency — max(1 - days_since_last_refund / 90, 0) × 100
    if refund_history:
        try:
            last_refund_date = datetime.strptime(refund_history[0]["created_at"][:10], "%Y-%m-%d")
            days_since_last = (now - last_refund_date).days
        except (ValueError, TypeError):
            days_since_last = 999
    else:
        days_since_last = 999
    s7_raw = max(1 - days_since_last / RFM_RECENCY_WINDOW_DAYS, 0) * 100

    # S8: RFM Frequency — min(refund_count_last_90_days / 4, 1.0) × 100
    cutoff_date = now - timedelta(days=RFM_FREQUENCY_WINDOW_DAYS)
    refund_count_90d = 0
    for r in refund_history:
        try:
            rd = datetime.strptime(r["created_at"][:10], "%Y-%m-%d")
            if rd >= cutoff_date:
                refund_count_90d += 1
        except (ValueError, TypeError):
            pass
    s8_raw = min(refund_count_90d / RFM_FREQUENCY_THRESHOLD, 1.0) * 100

    # S9: RFM Monetary Ratio — min(total_refunded / total_purchased, 1.0) × 100
    total_refunded = sum(r.get("amount", 0) for r in refund_history)
    total_purchased = sum(o.get("amount", 0) for o in order_history)
    if total_purchased > 0:
        s9_raw = min(total_refunded / total_purchased, 1.0) * 100
    else:
        s9_raw = 0

    # S10: Cross-Merchant Fraud — based on claims at other merchants in last 30 days
    cm_cutoff = now - timedelta(days=CROSS_MERCHANT_WINDOW_DAYS)
    recent_cm_merchants = set()
    for claim in cross_merchant_claims:
        try:
            cd = datetime.strptime(claim["claim_date"], "%Y-%m-%d")
            if cd >= cm_cutoff:
                recent_cm_merchants.add(claim["merchant_name"])
        except (ValueError, TypeError):
            pass
    cm_count = len(recent_cm_merchants)
    s10_raw = CROSS_MERCHANT_SCORES.get(cm_count, CROSS_MERCHANT_SCORE_DEFAULT)

    # Cold start flag
    is_cold_start = customer["total_orders"] < 3

    return {
        "customer": customer,
        "order": order,
        "product": product,
        "refund_history": refund_history,
        "order_history": order_history,
        "cross_merchant_claims": cross_merchant_claims,
        "order_amount": amount,
        "is_cold_start": is_cold_start,
        "is_product_defect": is_product_defect,
        "signals": {
            "customer_refund_rate":   {"raw": round(refund_rate, 4), "score": round(s1_raw, 1), "detail": f"{refund_rate*100:.0f}% refund rate ({customer['total_refunds']}/{customer['total_orders']}){'  [dampened: product defect detected]' if is_product_defect else ''}"},
            "delivery_contradiction": {"raw": f"{reason} vs {delivery_status}", "score": round(s2_raw, 1), "detail": f"{'CONTRADICTION' if s2_raw > 0 else 'No contradiction'}: {reason} with delivery={delivery_status}"},
            "amount_risk":            {"raw": amount, "score": round(s3_raw, 1), "detail": f"₹{amount} — {'low' if s3_raw <= 15 else 'medium' if s3_raw <= 35 else 'high'} risk tier"},
            "claim_pattern":          {"raw": same_reason_count, "score": round(s4_raw, 1), "detail": f"'{reason}' used {same_reason_count} times before"},
            "category_deviation":     {"raw": round(product_expected_rate, 4), "score": round(s5_raw, 1), "detail": f"Customer rate {refund_rate*100:.0f}% vs category expected {product_expected_rate*100:.0f}%"},
            "sentiment":              {"raw": sentiment_result["label"], "score": round(s6_raw, 1), "detail": sentiment_result["detail"]},
            "rfm_recency":            {"raw": days_since_last, "score": round(s7_raw, 1), "detail": f"Last refund {days_since_last} days ago"},
            "rfm_frequency":          {"raw": refund_count_90d, "score": round(s8_raw, 1), "detail": f"{refund_count_90d} refunds in last 90 days"},
            "rfm_monetary":           {"raw": round(total_refunded / max(total_purchased, 1), 4), "score": round(s9_raw, 1), "detail": f"Refunded ₹{total_refunded:.0f} of ₹{total_purchased:.0f} purchased ({total_refunded/max(total_purchased,1)*100:.0f}%)"},
            "cross_merchant_fraud":   {"raw": cm_count, "score": round(s10_raw, 1), "detail": f"{cm_count} other merchant(s) with claims in last 30 days{': ' + ', '.join(recent_cm_merchants) if recent_cm_merchants else ''}"},
        },
    }
