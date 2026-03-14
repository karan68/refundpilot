from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime


class RefundReason(str, Enum):
    DAMAGED_IN_TRANSIT = "damaged_in_transit"
    WRONG_PRODUCT = "wrong_product"
    DEFECTIVE = "defective"
    NOT_AS_DESCRIBED = "not_as_described"
    SIZE_ISSUE = "size_issue"
    NOT_DELIVERED = "not_delivered"
    CHANGED_MIND = "changed_mind"
    OTHER = "other"


class Decision(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    INVESTIGATE = "INVESTIGATE"
    ESCALATE = "ESCALATE"


class DeliveryStatus(str, Enum):
    DELIVERED = "delivered"
    DELIVERED_SIGNED = "delivered_signed"
    IN_TRANSIT = "in_transit"
    RETURNED_TO_SELLER = "returned_to_seller"
    NOT_SHIPPED = "not_shipped"


class CustomerType(str, Enum):
    LOYAL = "loyal"
    REGULAR = "regular"
    NEW = "new"
    SUSPECT = "suspect"
    ABUSER = "abuser"


# ── Request / Response Models ──


class RefundRequest(BaseModel):
    customer_id: str
    order_id: str
    reason: RefundReason
    message: str
    language: str = "en"


class ReasoningStep(BaseModel):
    step: int
    signal: str
    value: str
    impact: str  # positive / negative / neutral
    detail: str


class ActionTaken(BaseModel):
    type: str  # pine_labs_refund, evidence_request, escalate, store_credit
    amount: Optional[float] = None
    status: str = "initiated"
    pine_labs_ref: Optional[str] = None
    message: Optional[str] = None


class RefundDecision(BaseModel):
    refund_id: str
    customer_id: str
    order_id: str
    status: str
    risk_score: int
    decision: Decision
    confidence: float
    processing_time_ms: int
    reasoning_chain: list[ReasoningStep]
    action_taken: ActionTaken
    store_credit_offered: bool = False
    store_credit_amount: Optional[float] = None
    created_at: datetime


# ── Database Row Models ──


class CustomerRow(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    total_orders: int
    total_refunds: int
    refund_rate: float
    customer_type: CustomerType
    city: str
    created_at: str


class ProductRow(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    expected_refund_rate: float


class OrderRow(BaseModel):
    id: str
    customer_id: str
    product_sku: str
    product_name: str
    amount: float
    order_date: str
    delivery_status: DeliveryStatus
    delivery_date: Optional[str] = None
    return_window_days: int = 15


class RefundRow(BaseModel):
    id: str
    order_id: str
    customer_id: str
    amount: float
    reason: RefundReason
    message: str
    language: str
    risk_score: Optional[int] = None
    decision: Optional[str] = None
    confidence: Optional[float] = None
    reasoning_json: Optional[str] = None
    action_type: Optional[str] = None
    pine_labs_ref: Optional[str] = None
    processing_time_ms: Optional[int] = None
    status: str = "pending"  # pending, approved, investigating, escalated, denied
    created_at: str


# ── Dashboard Models ──


class DashboardStats(BaseModel):
    total_refunds: int
    auto_approved: int
    investigated: int
    escalated: int
    avg_processing_time_ms: float
    fraud_savings: float
    auto_approve_rate: float
    total_refund_amount: float


class MerchantQueryRequest(BaseModel):
    query: str


class MerchantQueryResponse(BaseModel):
    answer: str
    data: Optional[dict] = None
