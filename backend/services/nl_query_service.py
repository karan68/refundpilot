"""NL Query Service — natural language merchant queries against refund data.

Parses merchant questions like "Show me flagged refunds this week" into SQL queries
and returns natural language answers with data.
"""

from models.database import get_db
import re


# Intent patterns — regex-based NL→SQL mapping (no LLM needed for common queries)
QUERY_PATTERNS = [
    {
        "patterns": [r"flagged|escalated|suspicious", r"this week|last 7|recent"],
        "query": "SELECT r.*, c.name as customer_name FROM refunds r JOIN customers c ON r.customer_id = c.id WHERE r.decision = 'ESCALATE' ORDER BY r.created_at DESC LIMIT 20",
        "template": "You have {count} escalated refunds totaling ₹{total:.0f}. {detail}",
    },
    {
        "patterns": [r"approved|auto.?approv"],
        "query": "SELECT r.*, c.name as customer_name FROM refunds r JOIN customers c ON r.customer_id = c.id WHERE r.decision = 'AUTO_APPROVE' ORDER BY r.created_at DESC LIMIT 20",
        "template": "{count} refunds were auto-approved totaling ₹{total:.0f}.",
    },
    {
        "patterns": [r"fraud|cost|loss|save"],
        "query": "SELECT SUM(amount) as total, COUNT(*) as count FROM refunds WHERE decision = 'ESCALATE'",
        "template": "Fraud detection saved ₹{total:.0f} across {count} escalated cases.",
    },
    {
        "patterns": [r"top|worst|abuser|serial"],
        "query": "SELECT c.*, COUNT(r.id) as refund_count, SUM(r.amount) as total_amount FROM customers c JOIN refunds r ON c.id = r.customer_id GROUP BY c.id ORDER BY c.refund_rate DESC LIMIT 5",
        "template": "Top {count} customers by refund rate: {detail}",
    },
    {
        "patterns": [r"product|sku|category|defect"],
        "query": """SELECT p.sku, p.name, p.category, COUNT(r.id) as refund_count,
                    ROUND(COUNT(r.id) * 100.0 / MAX(1, (SELECT COUNT(*) FROM orders WHERE product_sku = p.sku)), 1) as refund_pct
                    FROM products p
                    JOIN orders o ON p.sku = o.product_sku
                    JOIN refunds r ON o.id = r.order_id
                    GROUP BY p.sku ORDER BY refund_count DESC""",
        "template": "Product refund breakdown: {detail}",
    },
    {
        "patterns": [r"ring|linked|address|network"],
        "query": """SELECT o.shipping_address, COUNT(DISTINCT o.customer_id) as accounts,
                    GROUP_CONCAT(DISTINCT c.name) as names
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    JOIN refunds r ON r.customer_id = o.customer_id
                    GROUP BY o.shipping_address HAVING accounts > 1
                    ORDER BY accounts DESC""",
        "template": "{count} address(es) linked to multiple refund accounts: {detail}",
    },
]


def _match_intent(query_text: str) -> dict | None:
    """Match a natural language query to a known pattern."""
    q = query_text.lower()
    for pattern in QUERY_PATTERNS:
        if any(re.search(p, q) for p in pattern["patterns"]):
            return pattern
    return None


async def process_nl_query(query_text: str) -> dict:
    """Process a natural language merchant query and return structured answer."""
    intent = _match_intent(query_text)

    if not intent:
        return {
            "answer": f"I don't understand that query yet. Try asking about: flagged refunds, auto-approved, fraud costs, top abusers, product defects, or fraud rings.",
            "data": None,
        }

    db = await get_db()
    cursor = await db.execute(intent["query"])
    rows = [dict(r) for r in await cursor.fetchall()]
    await db.close()

    if not rows:
        return {"answer": "No data found for that query.", "data": None}

    # Build answer from template
    count = len(rows)
    total = sum(r.get("amount", 0) or r.get("total", 0) or r.get("total_amount", 0) or 0 for r in rows)

    # Build detail string
    if "customer_name" in rows[0]:
        detail = "; ".join(f"{r['customer_name']} (₹{r.get('amount', 0)})" for r in rows[:5])
    elif "name" in rows[0] and "refund_rate" in rows[0]:
        detail = "; ".join(f"{r['name']} ({r['refund_rate']*100:.0f}% rate)" for r in rows[:5])
    elif "sku" in rows[0]:
        detail = "; ".join(f"{r['name']} ({r.get('refund_count', 0)} refunds, {r.get('refund_pct', 0)}%)" for r in rows[:5])
    elif "shipping_address" in rows[0]:
        detail = "; ".join(f"{r['shipping_address']} ({r['accounts']} accounts: {r['names']})" for r in rows[:3])
    else:
        # Single-row aggregate
        if len(rows) == 1 and "total" in rows[0]:
            total = rows[0].get("total", 0) or 0
            count = rows[0].get("count", 0) or 0
        detail = ""

    answer = intent["template"].format(count=count, total=total, detail=detail)

    return {"answer": answer, "data": rows[:10]}