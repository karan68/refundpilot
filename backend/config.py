import os

# ZhipuAI (GLM-5) Configuration
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = "https://api.z.ai/api/paas/v4"
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-5")
ZHIPU_CHAT_MODEL = os.getenv("ZHIPU_CHAT_MODEL", "glm-5")

# LLM Usage Control — minimize token burn
# Set to False to skip LLM explanation calls (use template fallback)
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() == "true"

# Groq Configuration (free tier — used for VISION only)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

# AWS Bedrock Configuration (legacy — kept for fallback)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
BEDROCK_VISION_MODEL_ID = os.getenv("BEDROCK_VISION_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

# Pine Labs Configuration
PINELABS_API_BASE = os.getenv("PINELABS_API_BASE", "https://api.pinelabs.com/v1")
PINELABS_MERCHANT_ID = os.getenv("PINELABS_MERCHANT_ID", "")
PINELABS_CLIENT_ID = os.getenv("PINELABS_CLIENT_ID", "")
PINELABS_CLIENT_SECRET = os.getenv("PINELABS_CLIENT_SECRET", "")
# Legacy key field (kept for backward compat)
PINELABS_API_KEY = os.getenv("PINELABS_API_KEY", "")

# App Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "refundpilot.db")
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]

# Risk Thresholds
RISK_AUTO_APPROVE_MAX = 30
RISK_INVESTIGATE_MAX = 70
# Above 70 = ESCALATE

# 10-Signal Weights — Default (must sum to 1.0)
SIGNAL_WEIGHTS = {
    "customer_refund_rate": 0.18,       # S1: Chronic returner detection (highest — most predictive)
    "delivery_contradiction": 0.14,     # S2: Reason vs delivery status mismatch
    "amount_risk": 0.07,                # S3: High-value claim scrutiny
    "claim_pattern": 0.11,              # S4: Same excuse repeated
    "category_deviation": 0.07,         # S5: Refund rate above category norm
    "sentiment": 0.06,                  # S6: Formulaic = suspicious, angry = genuine
    "rfm_recency": 0.08,               # S7: Days since last refund
    "rfm_frequency": 0.08,             # S8: Refund burst count (last 90 days)
    "rfm_monetary": 0.08,              # S9: Cumulative refunded / purchased ratio
    "cross_merchant_fraud": 0.13,       # S10: Pine Labs network — corroborating signal (not primary)
}

# Merchant Weight Presets (Fashion/Electronics/Custom)
MERCHANT_PRESETS = {
    "default": SIGNAL_WEIGHTS,
    "fashion": {
        "customer_refund_rate": 0.15,
        "delivery_contradiction": 0.18,  # ↑ wardrobing detection
        "amount_risk": 0.05,              # ↓ fashion is generally cheaper
        "claim_pattern": 0.12,
        "category_deviation": 0.08,
        "sentiment": 0.06,
        "rfm_recency": 0.08,
        "rfm_frequency": 0.08,
        "rfm_monetary": 0.07,
        "cross_merchant_fraud": 0.13,
    },
    "electronics": {
        "customer_refund_rate": 0.16,
        "delivery_contradiction": 0.12,
        "amount_risk": 0.12,              # ↑ high-value items
        "claim_pattern": 0.10,
        "category_deviation": 0.06,
        "sentiment": 0.08,                # ↑ scripted claim detection
        "rfm_recency": 0.08,
        "rfm_frequency": 0.08,
        "rfm_monetary": 0.08,
        "cross_merchant_fraud": 0.12,
    },
}

# Amount Risk Tiers (S3)
AMOUNT_RISK_TIERS = [
    (500, 5),      # < ₹500 → score 5
    (1500, 15),    # < ₹1500 → score 15
    (3000, 35),    # < ₹3000 → score 35
    (5000, 55),    # < ₹5000 → score 55
    (float("inf"), 80),  # ≥ ₹5000 → score 80
]

# Delivery Contradiction Map (S2): (reason, delivery_status) → score
# 100 = full contradiction, 0 = no contradiction
DELIVERY_CONTRADICTIONS = {
    ("damaged_in_transit", "delivered_signed"): 100,
    ("not_delivered", "delivered"): 100,
    ("not_delivered", "delivered_signed"): 100,
    ("damaged_in_transit", "delivered"): 40,
}

# RFM Windows
RFM_RECENCY_WINDOW_DAYS = 90      # S7: max lookback
RFM_FREQUENCY_WINDOW_DAYS = 90    # S8: count window
RFM_FREQUENCY_THRESHOLD = 4       # S8: 4 refunds in 90 days = max score

# Cross-Merchant Fraud (S10) — Pine Labs network intelligence
# Score based on number of other merchants with refund claims in 30 days
CROSS_MERCHANT_WINDOW_DAYS = 30
CROSS_MERCHANT_SCORES = {
    0: 0,     # 0 other merchants = no risk
    1: 40,    # 1 other merchant = moderate risk
}
CROSS_MERCHANT_SCORE_DEFAULT = 100  # 2+ other merchants = max risk

# Available merchant preset names
AVAILABLE_PRESETS = list(MERCHANT_PRESETS.keys())  # ["default", "fashion", "electronics"]

# Seasonal Adjustments (F23) — adjust tier BOUNDARIES, not weights
SEASONAL_ADJUSTMENTS = {
    "diwali":          {"start": "10-15", "end": "11-30", "threshold_shift": 8},
    "big_billion_day": {"start": "10-01", "end": "10-15", "threshold_shift": 10},
    "new_year":        {"start": "12-26", "end": "01-15", "threshold_shift": 5},
}

# Returnless Refund Threshold
# Items below this amount get instant refund without requiring return shipment
RETURNLESS_REFUND_THRESHOLD = 500  # ₹500 — merchant-adjustable
