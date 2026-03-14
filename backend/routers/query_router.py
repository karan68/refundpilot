from fastapi import APIRouter
from models.schemas import MerchantQueryRequest, MerchantQueryResponse

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("")
async def merchant_query(request: MerchantQueryRequest):
    """Natural language merchant query — Phase 2 adds Bedrock NL engine."""
    return MerchantQueryResponse(
        answer=f"NL query engine will be connected in Phase 4. You asked: '{request.query}'",
        data=None,
    )
