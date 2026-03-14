"""Risk Scorer — deterministic weighted formula: 10 signals → 0-100 score.

Score is PURE MATH — same input = same output, always.
LLM is only used for explanation text, never for scoring.
"""

from config import (
    SIGNAL_WEIGHTS,
    MERCHANT_PRESETS,
    RISK_AUTO_APPROVE_MAX,
    RISK_INVESTIGATE_MAX,
    SEASONAL_ADJUSTMENTS,
)
from datetime import datetime


def get_seasonal_shift() -> tuple[int, str]:
    """Check if current date falls within a seasonal window. Returns (shift, season_name)."""
    now = datetime.now()
    current_mmdd = now.strftime("%m-%d")

    for season, cfg in SEASONAL_ADJUSTMENTS.items():
        start = cfg["start"]
        end = cfg["end"]
        # Handle year wrap (e.g., new_year: 12-26 to 01-15)
        if start > end:
            if current_mmdd >= start or current_mmdd <= end:
                return cfg["threshold_shift"], season
        else:
            if start <= current_mmdd <= end:
                return cfg["threshold_shift"], season

    return 0, "default"


def compute_risk_score(signals: dict, preset: str = "default") -> dict:
    """Compute deterministic risk score from 10 signal scores.

    Args:
        signals: dict with signal name → {"raw": ..., "score": float, "detail": str}
        preset: merchant weight preset name ("default", "fashion", "electronics")

    Returns:
        dict with risk_score, decision, reasoning_chain, seasonal info
    """
    weights = MERCHANT_PRESETS.get(preset, SIGNAL_WEIGHTS)

    # Compute weighted score for each signal
    reasoning_chain = []
    total_score = 0.0
    step = 1

    signal_order = [
        "customer_refund_rate", "delivery_contradiction", "amount_risk",
        "claim_pattern", "category_deviation", "sentiment",
        "rfm_recency", "rfm_frequency", "rfm_monetary", "cross_merchant_fraud",
    ]

    for signal_name in signal_order:
        if signal_name not in signals:
            continue

        sig = signals[signal_name]
        weight = weights.get(signal_name, 0)
        raw_score = sig["score"]
        weighted = round(weight * raw_score, 2)
        total_score += weighted

        # Determine impact
        if weighted <= 0:
            impact = "positive"
        elif weighted < 5:
            impact = "neutral"
        else:
            impact = "negative"

        reasoning_chain.append({
            "step": step,
            "signal": signal_name,
            "value": str(sig["raw"]),
            "score": round(raw_score, 1),
            "weight": weight,
            "weighted": weighted,
            "impact": impact,
            "detail": sig["detail"],
        })
        step += 1

    risk_score = max(0, min(100, round(total_score)))

    # Apply seasonal threshold adjustment
    seasonal_shift, season_name = get_seasonal_shift()
    approve_threshold = RISK_AUTO_APPROVE_MAX + seasonal_shift
    escalate_threshold = RISK_INVESTIGATE_MAX + seasonal_shift

    # Classify decision
    if risk_score <= approve_threshold:
        decision = "AUTO_APPROVE"
    elif risk_score <= escalate_threshold:
        decision = "INVESTIGATE"
    else:
        decision = "ESCALATE"

    # Confidence: higher for extreme scores, lower near boundaries
    if risk_score <= 15 or risk_score >= 85:
        confidence = 0.95
    elif risk_score <= approve_threshold or risk_score > escalate_threshold:
        confidence = 0.85
    else:
        # In the investigate zone, confidence comes from how far from boundaries
        dist_from_approve = risk_score - approve_threshold
        dist_from_escalate = escalate_threshold - risk_score
        min_dist = min(dist_from_approve, dist_from_escalate)
        confidence = 0.5 + (min_dist / 40) * 0.3  # 0.5 to 0.8

    return {
        "risk_score": risk_score,
        "decision": decision,
        "confidence": round(confidence, 2),
        "reasoning_chain": reasoning_chain,
        "preset_used": preset,
        "seasonal_adjustment": {
            "season": season_name,
            "threshold_shift": seasonal_shift,
            "approve_threshold": approve_threshold,
            "escalate_threshold": escalate_threshold,
        },
    }
