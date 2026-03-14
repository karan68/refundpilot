"""Counterfactual Explanations — pure math, no LLM.

For each decision, computes "what would need to change" for a different outcome.
Hold all signals constant, vary one, find the decision-boundary threshold.
"""

from config import SIGNAL_WEIGHTS, MERCHANT_PRESETS, RISK_AUTO_APPROVE_MAX, RISK_INVESTIGATE_MAX


def compute_counterfactuals(
    signals: dict,
    risk_score: int,
    decision: str,
    reasoning_chain: list,
    preset: str = "default",
    seasonal_shift: int = 0,
) -> list[dict]:
    """Compute what would need to change for a different outcome.

    Returns list of counterfactual statements like:
    "Would be APPROVED if refund frequency was under 2 in 90 days (currently 8)"
    """
    weights = MERCHANT_PRESETS.get(preset, SIGNAL_WEIGHTS)
    approve_threshold = RISK_AUTO_APPROVE_MAX + seasonal_shift
    escalate_threshold = RISK_INVESTIGATE_MAX + seasonal_shift

    counterfactuals = []

    if decision == "AUTO_APPROVE":
        # Already approved — no counterfactual needed
        return [{"message": "Approved — no changes needed", "signal": None, "target": None}]

    # For INVESTIGATE or ESCALATE, find which signals would bring the score below approve_threshold
    target_score = approve_threshold

    for step in reasoning_chain:
        signal_name = step["signal"]
        weight = step["weight"]
        current_weighted = step["weighted"]
        current_raw_score = step["score"]

        if weight == 0 or current_weighted <= 0:
            continue

        # How much does this signal need to drop to bring total below target?
        excess = risk_score - target_score
        if excess <= 0:
            continue

        # If we zeroed this signal, would it be enough?
        if current_weighted >= excess:
            # Find what raw score this signal would need
            needed_weighted = current_weighted - excess
            needed_raw = needed_weighted / weight if weight > 0 else 0
            needed_raw = max(0, needed_raw)

            # Generate human-readable counterfactual
            cf = _format_counterfactual(signal_name, current_raw_score, needed_raw, step["detail"])
            if cf:
                counterfactuals.append(cf)

    # Sort by impact (largest delta first)
    counterfactuals.sort(key=lambda x: x.get("delta", 0), reverse=True)

    return counterfactuals[:3] if counterfactuals else [
        {"message": "Multiple signals contribute — no single change would alter the decision", "signal": None, "target": None}
    ]


def _format_counterfactual(signal_name: str, current: float, needed: float, detail: str) -> dict | None:
    """Format a counterfactual explanation for a specific signal."""
    delta = current - needed

    if delta < 1:
        return None

    messages = {
        "customer_refund_rate": f"Would be APPROVED if refund rate was under {needed/2:.0f}% (currently in detail: {detail})",
        "delivery_contradiction": f"Would be APPROVED if there was no delivery contradiction (currently: {detail})",
        "claim_pattern": f"Would be APPROVED if same claim reason was used fewer times ({detail})",
        "rfm_recency": f"Would be APPROVED if last refund was more than {90*(1-needed/100):.0f} days ago ({detail})",
        "rfm_frequency": f"Would be APPROVED if refund frequency was under {needed*4/100:.0f} in 90 days ({detail})",
        "rfm_monetary": f"Would be APPROVED if refund-to-purchase ratio was under {needed:.0f}% ({detail})",
        "cross_merchant_fraud": f"Would be APPROVED if no cross-merchant claims existed ({detail})",
        "sentiment": f"Would be APPROVED if message tone was less formulaic ({detail})",
        "amount_risk": f"Would be APPROVED if claim amount was lower ({detail})",
        "category_deviation": f"Would be APPROVED if return rate was within category norms ({detail})",
    }

    msg = messages.get(signal_name, f"Would be APPROVED if {signal_name} score was {needed:.0f} (currently {current:.0f})")

    return {
        "signal": signal_name,
        "current_score": round(current, 1),
        "needed_score": round(needed, 1),
        "delta": round(delta, 1),
        "message": msg,
    }
