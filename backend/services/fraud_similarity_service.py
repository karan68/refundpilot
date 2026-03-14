"""F26: Fraud Similarity Score — cosine distance between customer and fraudster centroid.

Builds a feature vector per customer from their 10 signal scores,
computes centroid of known fraudsters, then returns cosine similarity
for any given customer.
"""

from models.database import get_db
from agent.signal_collector import collect_signals
import math


# Known fraudster customer IDs (from seed data)
KNOWN_FRAUDSTER_IDS = ["CUST-002", "CUST-006"]  # Rohit, Arjun

# Pre-computed fraudster centroid (average of their signal profiles)
# Updated at startup or on-demand
_fraudster_centroid: list[float] | None = None


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product / (mag_a * mag_b)


def _customer_to_vector(signals: dict) -> list[float]:
    """Convert a customer's signal scores to a feature vector."""
    signal_order = [
        "customer_refund_rate", "delivery_contradiction", "amount_risk",
        "claim_pattern", "category_deviation", "sentiment",
        "rfm_recency", "rfm_frequency", "rfm_monetary", "cross_merchant_fraud",
    ]
    return [signals.get(s, {}).get("score", 0) for s in signal_order]


async def compute_fraudster_centroid() -> list[float]:
    """Compute average feature vector of known fraudsters from DB."""
    db = await get_db()
    vectors = []

    for cid in KNOWN_FRAUDSTER_IDS:
        cursor = await db.execute("SELECT * FROM customers WHERE id = ?", (cid,))
        customer = await cursor.fetchone()
        if not customer:
            continue
        customer = dict(customer)

        # Build a simplified feature vector from customer stats
        vec = [
            min(customer["refund_rate"] / 0.5, 1.0) * 100,  # S1
            50,  # S2 placeholder (avg contradiction)
            35,  # S3 placeholder (avg amount risk)
            80,  # S4 placeholder (high claim pattern)
            30,  # S5 placeholder
            15,  # S6 placeholder
            max(1 - 5 / 90, 0) * 100,  # S7 recent
            min(customer["total_refunds"] / 4, 1.0) * 100,  # S8
            min(customer["refund_rate"], 1.0) * 100,  # S9
            0,  # S10 placeholder
        ]
        vectors.append(vec)

    await db.close()

    if not vectors:
        return [50] * 10  # Default centroid

    # Average across all fraudster vectors
    centroid = [sum(v[i] for v in vectors) / len(vectors) for i in range(10)]
    return centroid


async def get_fraud_similarity(customer_signals: dict) -> dict:
    """Compute fraud similarity score for a customer against the fraudster centroid."""
    global _fraudster_centroid
    if _fraudster_centroid is None:
        _fraudster_centroid = await compute_fraudster_centroid()

    customer_vec = _customer_to_vector(customer_signals)
    similarity = _cosine_similarity(customer_vec, _fraudster_centroid)
    pct = round(similarity * 100, 1)

    if pct >= 80:
        risk_label = "Very High"
    elif pct >= 60:
        risk_label = "High"
    elif pct >= 40:
        risk_label = "Medium"
    elif pct >= 20:
        risk_label = "Low"
    else:
        risk_label = "Very Low"

    return {
        "similarity_pct": pct,
        "risk_label": risk_label,
        "customer_vector": customer_vec,
        "centroid": _fraudster_centroid,
    }
