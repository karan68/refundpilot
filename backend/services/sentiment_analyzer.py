"""Sentiment Analyzer — keyword-based scoring with optional LLM upgrade."""


# Keyword sets for sentiment detection
ANGRY_KEYWORDS = [
    "ridiculous", "unacceptable", "worst", "terrible", "horrible", "disgusting",
    "furious", "angry", "outraged", "scam", "fraud", "cheat", "never again",
    "waste", "pathetic", "useless", "complaint", "lawsuit", "consumer forum",
    "i want my money back", "immediately", "disgusted", "rubbish",
]

FORMULAIC_KEYWORDS = [
    "damaged in transit", "not as described", "defective product", "please process",
    "kindly refund", "request refund", "please refund", "i would like a refund",
    "product was damaged", "item was broken", "package was damaged",
]


def analyze_sentiment_keywords(message: str) -> dict:
    """Keyword-based sentiment scoring. Returns score + label.
    angry = -10 (genuine frustration), neutral = 0, formulaic = +20 (suspicious template)
    """
    msg_lower = message.lower()

    angry_count = sum(1 for kw in ANGRY_KEYWORDS if kw in msg_lower)
    formulaic_count = sum(1 for kw in FORMULAIC_KEYWORDS if kw in msg_lower)

    if angry_count >= 2:
        return {"score": -10, "label": "angry", "detail": f"Genuinely upset ({angry_count} anger indicators)"}
    elif angry_count == 1:
        return {"score": -5, "label": "frustrated", "detail": "Frustrated tone detected"}
    elif formulaic_count >= 2:
        return {"score": 20, "label": "formulaic", "detail": f"Templated/formulaic message ({formulaic_count} template phrases)"}
    elif formulaic_count == 1:
        return {"score": 10, "label": "scripted", "detail": "Possibly scripted message"}
    else:
        return {"score": 0, "label": "neutral", "detail": "Neutral tone"}