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
    """Call Bedrock Vision for damage analysis. Falls back to simulated result if unavailable."""
    try:
        from services.bedrock_service import invoke_vision

        prompt = f"""Analyze this product image submitted as refund evidence.
Product ordered: {product_description}
Claimed issue: {damage_reason}

Evaluate and respond in JSON:
1. "is_damaged": Is the product visibly damaged? (true/false)
2. "matches_order": Does the product match the order description? (true/false)
3. "is_stock_photo": Does this appear to be a stock/internet image rather than genuine photo? (true/false)
4. "severity": Damage severity: "none" / "minor" / "moderate" / "severe"
5. "confidence": Your confidence in this assessment (0.0 to 1.0)
6. "explanation": Brief explanation of findings

Return ONLY valid JSON, no other text."""

        response_text = await invoke_vision(prompt, image_bytes, media_type)

        # Try to parse JSON from response
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            return {
                "is_damaged": True,
                "matches_order": True,
                "is_stock_photo": False,
                "severity": "unknown",
                "confidence": 0.5,
                "explanation": "Vision analysis returned non-JSON response",
                "raw_response": response_text[:200],
            }

    except Exception as e:
        # Bedrock not available — return simulated analysis
        return {
            "is_damaged": True,
            "matches_order": True,
            "is_stock_photo": False,
            "severity": "moderate",
            "confidence": 0.7,
            "explanation": f"Simulated vision analysis (Bedrock unavailable: {type(e).__name__}). Assuming genuine damage for demo.",
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