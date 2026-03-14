"""Negotiator — smart store credit and policy negotiation.

Offers store credit with bonus when:
- Customer is in the investigate zone (not a clear abuser)
- Amount is moderate (not tiny, not huge)
- Credit with bonus retains revenue in merchant ecosystem + Pine Labs rails
"""


async def should_offer_store_credit(amount: float, decision_result: dict) -> dict:
    """Decide whether to offer store credit with a bonus.

    Logic: Offer credit when score is in the lower half of investigate zone (31-50),
    meaning the customer is borderline and retainable.
    """
    risk_score = decision_result.get("risk_score", 50)

    # Only offer credit for borderline-OK cases (score 31-50)
    if risk_score > 50:
        return {
            "offer_credit": False,
            "credit_amount": 0,
            "bonus": 0,
            "reason": "Risk score too high for store credit offer",
            "message": "",
        }

    # Calculate bonus (higher amount = higher bonus to incentivize acceptance)
    if amount < 500:
        bonus_pct = 0.10  # 10% bonus for small amounts
    elif amount < 2000:
        bonus_pct = 0.08  # 8% bonus
    else:
        bonus_pct = 0.06  # 6% bonus for larger amounts

    bonus = round(amount * bonus_pct)
    credit_amount = amount + bonus

    return {
        "offer_credit": True,
        "credit_amount": credit_amount,
        "bonus": bonus,
        "reason": f"Borderline case (score {risk_score}). Store credit retains revenue.",
        "message": f"We'd like to offer you ₹{credit_amount} in store credit (₹{amount} refund + ₹{bonus} bonus) — usable on your next purchase. This processes instantly!",
    }


async def negotiate_policy_exception(amount: float, customer: dict, order: dict) -> dict:
    """For edge cases like past-return-window loyal customers.

    If customer is loyal (refund_rate < 10%) but past return window,
    offer partial store credit as a gesture.
    """
    refund_rate = customer.get("refund_rate", 0)
    customer_type = customer.get("customer_type", "regular")

    if refund_rate > 0.10 or customer_type in ("abuser", "ring_member"):
        return {
            "offer": False,
            "message": "No policy exception — customer does not qualify.",
        }

    # Loyal customer past return window — offer 85% as store credit
    credit_amount = round(amount * 0.85)
    return {
        "offer": True,
        "type": "partial_store_credit",
        "credit_amount": credit_amount,
        "message": f"Your return window has passed, but as a valued customer, we'd like to offer ₹{credit_amount} in store credit as a gesture.",
    }
