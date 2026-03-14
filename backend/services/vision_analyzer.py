"""Vision Analyzer — Enhanced F8: EXIF extraction + Bedrock Vision analysis.

Pipeline:
1. EXIF metadata extraction (check timestamp, GPS, device info)
2. Damage & authenticity analysis (Bedrock Vision)
3. Barcode/tag verification (if visible)
"""

import io
import json
from datetime import datetime


def extract_exif_metadata(image_bytes: bytes) -> dict:
    """Extract EXIF metadata from image for fraud detection.

    Checks:
    - Timestamp: Was photo taken recently? Or is it old/reused?
    - GPS: Does location match shipping address city?
    - Device: Consistent device across evidence submissions?
    """
    # Try to extract EXIF using PIL if available
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        img = Image.open(io.BytesIO(image_bytes))
        exif_data = img._getexif()

        if not exif_data:
            return {
                "has_exif": False,
                "suspicious": False,
                "detail": "No EXIF metadata — photo may have been stripped or is a screenshot",
                "timestamp": None,
                "device": None,
            }

        parsed = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):
                continue
            parsed[tag] = str(value)

        timestamp = parsed.get("DateTime") or parsed.get("DateTimeOriginal")
        device = parsed.get("Make", "") + " " + parsed.get("Model", "")
        device = device.strip() or None

        # Check if photo is older than 7 days (suspicious for "just received damaged")
        is_old = False
        if timestamp:
            try:
                photo_dt = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
                days_old = (datetime.now() - photo_dt).days
                is_old = days_old > 7
            except (ValueError, TypeError):
                pass

        return {
            "has_exif": True,
            "suspicious": is_old,
            "detail": f"Photo taken {'>' if is_old else '<'}7 days ago" + (f" on {device}" if device else ""),
            "timestamp": timestamp,
            "device": device,
            "raw_fields": list(parsed.keys())[:10],
        }
    except ImportError:
        return {
            "has_exif": False,
            "suspicious": False,
            "detail": "PIL not available — EXIF extraction skipped",
            "timestamp": None,
            "device": None,
        }
    except Exception:
        return {
            "has_exif": False,
            "suspicious": False,
            "detail": "Could not parse EXIF from image",
            "timestamp": None,
            "device": None,
        }


async def analyze_evidence_photo(
    image_bytes: bytes,
    product_description: str,
    damage_reason: str,
    media_type: str = "image/jpeg",
) -> dict:
    """Full evidence analysis pipeline: EXIF + Vision AI.

    Returns a structured analysis result.
    """
    # Step 1: EXIF extraction
    exif = extract_exif_metadata(image_bytes)

    # Step 2: Vision analysis via Bedrock (if available)
    vision_result = await _analyze_with_vision(image_bytes, product_description, damage_reason, media_type)

    # Step 3: Combine results
    overall_authentic = not exif["suspicious"] and vision_result.get("is_damaged", True)

    return {
        "exif": exif,
        "vision": vision_result,
        "overall": {
            "authentic": overall_authentic,
            "confidence": vision_result.get("confidence", 0.5),
            "recommendation": _get_recommendation(exif, vision_result),
        },
    }


async def _analyze_with_vision(
    image_bytes: bytes, product_description: str, damage_reason: str, media_type: str
) -> dict:
    """Call Groq (Llama 4 Scout) for vision analysis. Falls back to simulated if unavailable."""
    try:
        import httpx
        import base64
        from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_VISION_MODEL

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = f"""Analyze this product image submitted as refund evidence.
Product ordered: {product_description}
Claimed issue: {damage_reason}

Respond with JSON ONLY:
{{"is_damaged": true/false, "matches_order": true/false, "is_stock_photo": true/false, "severity": "none"/"minor"/"moderate"/"severe", "confidence": 0.0-1.0, "explanation": "brief"}}"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_VISION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_b64}"}},
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                    "max_tokens": 200,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]

        # Parse JSON
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            return {
                "is_damaged": True,
                "matches_order": True,
                "is_stock_photo": False,
                "severity": "unknown",
                "confidence": 0.5,
                "explanation": "Vision returned non-JSON response",
                "raw_response": response_text[:200],
            }

    except Exception as e:
        # GLM not available — return simulated analysis
        return {
            "is_damaged": True,
            "matches_order": True,
            "is_stock_photo": False,
            "severity": "moderate",
            "confidence": 0.7,
            "explanation": f"Simulated vision analysis (GLM unavailable: {type(e).__name__}). Assuming genuine damage for demo.",
            "simulated": True,
        }


def _get_recommendation(exif: dict, vision: dict) -> str:
    """Determine recommendation based on combined EXIF + vision analysis."""
    if exif.get("suspicious"):
        return "EXIF_SUSPICIOUS — photo may be old/reused. Request fresh photo."

    if vision.get("is_stock_photo"):
        return "STOCK_PHOTO — this appears to be an internet image. Deny and flag account."

    if not vision.get("matches_order", True):
        return "MISMATCH — product in photo doesn't match order. Escalate."

    if not vision.get("is_damaged", True):
        return "NO_DAMAGE — no visible damage detected. Request additional evidence."

    severity = vision.get("severity", "unknown")
    if severity in ("moderate", "severe"):
        return "GENUINE_DAMAGE — approve refund."
    elif severity == "minor":
        return "MINOR_DAMAGE — consider partial refund or store credit."
    else:
        return "INCONCLUSIVE — escalate to human reviewer."