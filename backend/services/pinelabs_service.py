"""Pine Labs Online (Plural) API integration — Refund + Payment Links.

UAT: https://pluraluat.v2.pinepg.in/api/pay/v1/
PROD: https://api.pluralpay.in/api/pay/v1/
Auth: Bearer token from Generate Token API (client_id + client_secret).
Amount: in PAISA (₹1 = 100 paisa).
"""

import httpx
import uuid
from datetime import datetime, timezone
from config import (
    PINELABS_API_BASE,
    PINELABS_MERCHANT_ID,
    PINELABS_CLIENT_ID,
    PINELABS_CLIENT_SECRET,
    PINELABS_API_KEY,
)

# Pine Labs UAT base URL
PLURAL_UAT_BASE = "https://pluraluat.v2.pinepg.in/api/pay/v1"

# Cached access token
_access_token: str | None = None


def _is_configured() -> bool:
    """Check if Pine Labs credentials are available."""
    return bool(PINELABS_CLIENT_ID and PINELABS_CLIENT_SECRET)


async def _get_access_token() -> str:
    """Get or refresh access token from Pine Labs Generate Token API."""
    global _access_token
    if _access_token:
        return _access_token

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://pluraluat.v2.pinepg.in/api/auth/v1/token",
            headers={"accept": "application/json", "content-type": "application/json"},
            json={
                "client_id": PINELABS_CLIENT_ID,
                "client_secret": PINELABS_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        data = response.json()
        _access_token = data.get("access_token") or data.get("token")
        return _access_token


def _request_headers(token: str) -> dict:
    """Build Pine Labs API headers with auth + request tracking."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Request-ID": str(uuid.uuid4()),
        "Request-Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    }


async def initiate_refund(order_id: str, amount: float, reason: str) -> dict:
    """Call Pine Labs Refund API: POST /refunds/{order_id}"""
    if not _is_configured():
        return _simulated_refund(order_id, amount)

    try:
        token = await _get_access_token()
        refund_ref = f"refundpilot-{uuid.uuid4().hex[:12]}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{PLURAL_UAT_BASE}/refunds/{order_id}",
                headers=_request_headers(token),
                json={
                    "merchant_order_reference": refund_ref,
                    "order_amount": {
                        "value": int(amount * 100),  # Paisa
                        "currency": "INR",
                    },
                },
            )
            data = response.json()

            if response.status_code in (200, 201):
                return {
                    "success": True,
                    "pine_labs_ref": data.get("data", {}).get("order_id", refund_ref),
                    "parent_order_id": data.get("data", {}).get("parent_order_id"),
                    "amount": amount,
                    "status": data.get("data", {}).get("status", "PROCESSED"),
                    "message": f"Refund of ₹{amount} initiated via Pine Labs",
                    "raw_response": data,
                    "simulated": False,
                }
            else:
                return {
                    "success": False,
                    "pine_labs_ref": refund_ref,
                    "amount": amount,
                    "status": "api_error",
                    "message": data.get("message", f"Pine Labs returned {response.status_code}"),
                    "raw_response": data,
                    "simulated": False,
                }

    except Exception as e:
        return _simulated_refund(order_id, amount, f"Pine Labs API error: {type(e).__name__}")


async def create_payment_link(amount: float, customer_email: str, description: str) -> dict:
    """Call Pine Labs Payment Link API: POST /paymentlink"""
    if not _is_configured():
        return _simulated_payment_link(amount)

    try:
        token = await _get_access_token()
        link_ref = f"rp-link-{uuid.uuid4().hex[:10]}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{PLURAL_UAT_BASE}/paymentlink",
                headers=_request_headers(token),
                json={
                    "merchant_payment_link_reference": link_ref,
                    "amount": {
                        "value": int(amount * 100),  # Paisa
                        "currency": "INR",
                    },
                    "description": description,
                    "customer": {
                        "email_id": customer_email,
                    },
                    "allowed_payment_methods": ["CARD", "UPI", "NETBANKING", "WALLET"],
                },
            )
            data = response.json()

            if response.status_code in (200, 201):
                return {
                    "success": True,
                    "payment_link": data.get("payment_link", ""),
                    "payment_link_id": data.get("payment_link_id", ""),
                    "amount": amount,
                    "status": data.get("status", "CREATED"),
                    "raw_response": data,
                    "simulated": False,
                }
            else:
                return _simulated_payment_link(amount, f"Pine Labs returned {response.status_code}")

    except Exception as e:
        return _simulated_payment_link(amount, f"Pine Labs API error: {type(e).__name__}")


async def get_transaction(transaction_id: str) -> dict:
    """Fetch order/transaction details from Pine Labs."""
    if not _is_configured():
        return {"transaction_id": transaction_id, "status": "completed", "payment_method": "UPI", "simulated": True}

    try:
        token = await _get_access_token()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{PLURAL_UAT_BASE}/orders/{transaction_id}",
                headers=_request_headers(token),
            )
            return {"transaction_id": transaction_id, "raw_response": response.json(), "simulated": False}
    except Exception:
        return {"transaction_id": transaction_id, "status": "completed", "payment_method": "UPI", "simulated": True}


async def create_order(amount: float, customer_name: str, customer_email: str, reference: str) -> dict:
    """Create a Pine Labs order. Returns order_id for use in refund flow."""
    if not _is_configured():
        return {"order_id": f"v1-demo-{reference}", "status": "CREATED", "simulated": True}

    try:
        token = await _get_access_token()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PLURAL_UAT_BASE}/orders",
                headers=_request_headers(token),
                json={
                    "merchant_order_reference": reference,
                    "order_amount": {"value": int(amount * 100), "currency": "INR"},
                    "purchase_details": {
                        "customer": {
                            "email_id": customer_email,
                            "first_name": customer_name.split()[0] if customer_name else "Customer",
                            "last_name": customer_name.split()[-1] if len(customer_name.split()) > 1 else "",
                            "mobile_number": "9876543210",
                            "country_code": "91",
                        }
                    },
                },
            )
            data = response.json()
            if response.status_code in (200, 201):
                return {
                    "order_id": data.get("data", {}).get("order_id", ""),
                    "merchant_id": data.get("data", {}).get("merchant_id", ""),
                    "status": data.get("data", {}).get("status", "CREATED"),
                    "raw_response": data,
                    "simulated": False,
                }
            return {"order_id": "", "status": "failed", "message": data.get("message", ""), "simulated": False}
    except Exception as e:
        return {"order_id": f"v1-demo-{reference}", "status": "CREATED", "simulated": True}


async def get_settlements() -> dict:
    """Get settlement list from Pine Labs."""
    if not _is_configured():
        return {"settlements": [], "simulated": True}

    try:
        token = await _get_access_token()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://pluraluat.v2.pinepg.in/api/settlements/v1/list",
                headers=_request_headers(token),
            )
            return {"settlements": response.json(), "simulated": False}
    except Exception:
        return {"settlements": [], "simulated": True}


# ── Simulated fallbacks ──

def _simulated_refund(order_id: str, amount: float, note: str = "") -> dict:
    return {
        "success": True,
        "pine_labs_ref": f"PL-REF-{order_id[-4:]}",
        "amount": amount,
        "status": "refund_initiated",
        "message": f"Refund of ₹{amount} initiated for {order_id}" + (f" ({note})" if note else ""),
        "simulated": True,
    }


def _simulated_payment_link(amount: float, note: str = "") -> dict:
    return {
        "success": True,
        "payment_link": f"https://pay.pinelabs.com/link/demo-{int(amount)}",
        "amount": amount,
        "status": "link_created",
        "message": note or "",
        "simulated": True,
    }
