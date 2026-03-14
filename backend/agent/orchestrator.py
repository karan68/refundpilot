"""Agent Orchestrator — main loop: observe → collect signals → score → decide → act.
Includes F22: concurrent refund locking per customer_id.
"""

from agent.signal_collector import collect_signals
from agent.decision_engine import evaluate_refund
from agent.action_executor import execute_action
from services.fraud_detector import check_fraud_ring
import asyncio
import time

# F22: Customer-level locks — serialize refund processing per customer
_customer_locks: dict[str, asyncio.Lock] = {}


async def process_refund(
    customer_id: str,
    order_id: str,
    reason: str,
    message: str,
    refund_id: str = "",
    language: str = "en",
    preset: str = "default",
) -> dict:
    """Full agent loop for processing a refund request.

    F22: Only one refund per customer processes at a time.
    Second concurrent request waits and sees updated refund count.
    """
    # F22: Acquire customer lock
    if customer_id not in _customer_locks:
        _customer_locks[customer_id] = asyncio.Lock()

    async with _customer_locks[customer_id]:
        start_time = time.time()

        # Step 1: Collect all 10 signals
        signals_data = await collect_signals(customer_id, order_id, reason, message)

        # Step 2: Run decision engine (score + 3-tier logic + counterfactuals)
        decision_result = await evaluate_refund(signals_data, message, reason, preset=preset)

        # Step 3: Check fraud ring (F20) — runs in parallel with action
        fraud_ring = await check_fraud_ring(customer_id, order_id)

        # Step 4: Execute action
        action = await execute_action(
            decision_result,
            refund_id=refund_id,
            order_id=order_id,
            amount=signals_data["order_amount"],
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "refund_id": refund_id,
            "risk_score": decision_result["risk_score"],
            "decision": decision_result["decision"],
            "confidence": decision_result["confidence"],
            "processing_time_ms": elapsed_ms,
            "reasoning_chain": decision_result["reasoning_chain"],
            "explanation": decision_result["explanation"],
            "counterfactuals": decision_result["counterfactuals"],
            "recommended_action": decision_result["recommended_action"],
            "react_steps": decision_result.get("react_steps", []),
            "action": action,
            "fraud_ring": fraud_ring,
            "seasonal": decision_result["seasonal"],
            "preset_used": decision_result["preset_used"],
            "is_cold_start": decision_result["is_cold_start"],
            "circuit_breaker_fired": decision_result["circuit_breaker_fired"],
            "signals": {
                name: {"score": sig["score"], "detail": sig["detail"]}
                for name, sig in signals_data["signals"].items()
            },
        }
