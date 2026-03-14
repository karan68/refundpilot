from fastapi import APIRouter, UploadFile, File
from services.vision_analyzer import analyze_evidence_photo
from services.fraud_detector import check_fraud_ring
from models.database import get_db
import json

router = APIRouter(prefix="/api/webhook", tags=["webhook"])


@router.post("/evidence/{refund_id}")
async def upload_evidence(refund_id: str, file: UploadFile = File(...)):
    """Upload evidence photo for a refund — runs EXIF + Vision analysis pipeline."""
    contents = await file.read()

    # Get refund details for context
    db = await get_db()
    cursor = await db.execute(
        """SELECT r.*, o.product_name, o.product_sku
           FROM refunds r JOIN orders o ON r.order_id = o.id
           WHERE r.id = ?""",
        (refund_id,),
    )
    refund = await cursor.fetchone()

    if not refund:
        await db.close()
        return {"error": "Refund not found"}

    refund = dict(refund)
    product_desc = refund.get("product_name", "Unknown product")
    reason = refund.get("reason", "damaged_in_transit")

    # Determine media type
    media_type = file.content_type or "image/jpeg"

    # Run full vision analysis pipeline
    analysis = await analyze_evidence_photo(contents, product_desc, reason, media_type)

    # Log analysis to audit trail
    await db.execute(
        """INSERT INTO audit_logs (refund_id, event_type, detail)
           VALUES (?, ?, ?)""",
        (
            refund_id,
            "evidence_analyzed",
            json.dumps({
                "filename": file.filename,
                "size_bytes": len(contents),
                "exif_suspicious": analysis["exif"]["suspicious"],
                "recommendation": analysis["overall"]["recommendation"],
            }),
        ),
    )
    await db.commit()
    await db.close()

    return {
        "refund_id": refund_id,
        "filename": file.filename,
        "size_bytes": len(contents),
        "analysis": analysis,
    }


@router.post("/fraud-ring/{refund_id}")
async def check_fraud_ring_endpoint(refund_id: str):
    """Check if a refund is part of a fraud ring (F20)."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT customer_id, order_id FROM refunds WHERE id = ?", (refund_id,)
    )
    refund = await cursor.fetchone()
    await db.close()

    if not refund:
        return {"error": "Refund not found"}

    result = await check_fraud_ring(refund["customer_id"], refund["order_id"])
    return {
        "refund_id": refund_id,
        "fraud_ring": result,
    }
