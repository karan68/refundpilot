"""Pine Labs API integration — Refund, Transaction, Payment Links."""

import httpx
from config import PINELABS_API_BASE, PINELABS_API_KEY, PINELABS_MERCHANT_ID


def _headers():
    return {
        "Authorization": f"Bearer {PINELABS_API_KEY}",
        "Content-Type": "application/json",
        "X-Merchant-Id": PINELABS_MERCHANT_ID,
    }


async def initiate_refund(order_id: str, amount: float, reason: str) -> dict:
    """Call Pine Labs Refund API to process a refund."""
    # When Pine Labs creds are provided, this calls the real API.
    # For now, returns a simulated successful response.
    if not PINELABS_API_KEY:
        return {
            "success": True,
            "pine_labs_ref": f"PL-REF-{order_id[-4:]}",
            "amount": amount,
            "status": "refund_initiated",
            "message": f"Refund of ₹{amount} initiated for order {order_id}",
            "simulated": True,
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PINELABS_API_BASE}/refunds",
            headers=_headers(),
            json={
                "order_id": order_id,
                "amount": amount,
                "reason": reason,
            },
        )
        return response.json()


async def create_payment_link(amount: float, customer_email: str, description: str) -> dict:
    """Create a Pine Labs Payment Link for partial/negotiated refunds."""
    if not PINELABS_API_KEY:
        return {
            "success": True,
            "payment_link": f"https://pay.pinelabs.com/link/demo-{int(amount)}",
            "amount": amount,
            "status": "link_created",
            "simulated": True,
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PINELABS_API_BASE}/payment-links",
            headers=_headers(),
            json={
                "amount": amount,
                "customer_email": customer_email,
                "description": description,
            },
        )
        return response.json()


async def get_transaction(transaction_id: str) -> dict:
    """Fetch transaction details from Pine Labs."""
    if not PINELABS_API_KEY:
        return {
            "transaction_id": transaction_id,
            "status": "completed",
            "payment_method": "UPI",
            "simulated": True,
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PINELABS_API_BASE}/transactions/{transaction_id}",
            headers=_headers(),
        )
        return response.json()
