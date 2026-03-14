"""Pre-built customer profiles, products, and orders for the RefundPilot demo."""

import aiosqlite
from models.database import DB_PATH


CUSTOMERS = [
    ("CUST-001", "Priya Sharma", "priya@email.com", "+91-9876543210", 23, 1, 0.02, "loyal", "Mumbai"),
    ("CUST-002", "Rohit Mehta", "rohit@email.com", "+91-9876543211", 12, 8, 0.67, "abuser", "Delhi"),
    ("CUST-003", "Anita Verma", "anita@email.com", "+91-9876543212", 45, 3, 0.07, "loyal", "Bangalore"),
    ("CUST-004", "Vikram Singh", "vikram@email.com", "+91-9876543213", 8, 4, 0.50, "suspect", "Hyderabad"),
    ("CUST-005", "Meera Patel", "meera@email.com", "+91-9876543214", 15, 0, 0.0, "loyal", "Pune"),
    ("CUST-006", "Arjun Reddy", "arjun@email.com", "+91-9876543215", 6, 5, 0.83, "abuser", "Bangalore"),
    ("CUST-007", "Neha Gupta", "neha@email.com", "+91-9876543216", 1, 0, 0.0, "new", "Chennai"),
    ("CUST-008", "Deepak Kumar", "deepak@email.com", "+91-9876543217", 3, 1, 0.33, "ring_member", "Delhi"),
    ("CUST-009", "Sunita Devi", "sunita@email.com", "+91-9876543218", 2, 1, 0.50, "ring_member", "Delhi"),
]

PRODUCTS = [
    ("FASH-001", "Cotton Kurta - Blue", "Fashion", 800.0, 0.10),
    ("FASH-002", "Running Shoes - Black", "Fashion", 2400.0, 0.12),
    ("ELEC-001", "Wireless Earbuds Pro", "Electronics", 3500.0, 0.03),
    ("ELEC-002", "USB-C Charging Cable", "Electronics", 499.0, 0.02),
    ("HOME-001", "Ceramic Vase - White", "Home & Decor", 1200.0, 0.06),
    ("HOME-002", "Scented Candle Set", "Home & Decor", 650.0, 0.04),
]

ORDERS = [
    # ── Priya (loyal: 23 orders, 1 refund) ──
    ("ORD-1001", "CUST-001", "FASH-001", "Cotton Kurta - Blue", 800.0, "2026-02-15", "delivered", "2026-02-18", 15, "12 Marine Drive, Mumbai"),
    ("ORD-1002", "CUST-001", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-01-10", "delivered", "2026-01-13", 15, "12 Marine Drive, Mumbai"),
    ("ORD-1003", "CUST-001", "HOME-002", "Scented Candle Set", 650.0, "2025-12-20", "delivered", "2025-12-23", 15, "12 Marine Drive, Mumbai"),
    ("ORD-1004", "CUST-001", "FASH-002", "Running Shoes - Black", 2400.0, "2025-11-05", "delivered", "2025-11-08", 15, "12 Marine Drive, Mumbai"),
    ("ORD-1005", "CUST-001", "ELEC-002", "USB-C Charging Cable", 499.0, "2025-10-18", "delivered", "2025-10-20", 15, "12 Marine Drive, Mumbai"),

    # ── Rohit (abuser: 12 orders, 8 refunds) — shares address with CUST-008, CUST-009 ──
    ("ORD-2001", "CUST-002", "FASH-002", "Running Shoes - Black", 2400.0, "2026-03-01", "delivered_signed", "2026-03-04", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-2002", "CUST-002", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-02-10", "delivered_signed", "2026-02-13", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-2003", "CUST-002", "FASH-001", "Cotton Kurta - Blue", 800.0, "2026-01-20", "delivered_signed", "2026-01-23", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-2004", "CUST-002", "HOME-001", "Ceramic Vase - White", 1200.0, "2025-12-28", "delivered_signed", "2025-12-31", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-2005", "CUST-002", "FASH-002", "Running Shoes - Black", 2400.0, "2025-12-05", "delivered_signed", "2025-12-08", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-2006", "CUST-002", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2025-11-15", "delivered_signed", "2025-11-18", 15, "42 MG Road, Karol Bagh, Delhi"),

    # ── Anita (loyal: 45 orders, 3 refunds) ──
    ("ORD-3001", "CUST-003", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-02-25", "delivered", "2026-02-28", 15, "88 Indiranagar, Bangalore"),
    ("ORD-3002", "CUST-003", "ELEC-002", "USB-C Charging Cable", 499.0, "2026-01-15", "delivered", "2026-01-17", 15, "88 Indiranagar, Bangalore"),
    ("ORD-3003", "CUST-003", "HOME-001", "Ceramic Vase - White", 1200.0, "2025-12-10", "delivered", "2025-12-13", 15, "88 Indiranagar, Bangalore"),

    # ── Vikram (suspect: 8 orders, 4 refunds) ──
    ("ORD-4001", "CUST-004", "FASH-002", "Running Shoes - Black", 2400.0, "2026-03-05", "delivered", "2026-03-08", 15, "5 Banjara Hills, Hyderabad"),
    ("ORD-4002", "CUST-004", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-02-01", "delivered", "2026-02-04", 15, "5 Banjara Hills, Hyderabad"),
    ("ORD-4003", "CUST-004", "FASH-001", "Cotton Kurta - Blue", 800.0, "2026-01-05", "delivered", "2026-01-08", 15, "5 Banjara Hills, Hyderabad"),

    # ── Meera (perfect: 15 orders, 0 refunds) ──
    ("ORD-5001", "CUST-005", "FASH-001", "Cotton Kurta - Blue", 800.0, "2026-03-08", "delivered", "2026-03-10", 15, "22 Koregaon Park, Pune"),
    ("ORD-5002", "CUST-005", "HOME-002", "Scented Candle Set", 650.0, "2026-02-12", "delivered", "2026-02-14", 15, "22 Koregaon Park, Pune"),
    # Extra orders (no refunds) to normalize product cohort rates
    ("ORD-5003", "CUST-005", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2025-11-10", "delivered", "2025-11-12", 15, "22 Koregaon Park, Pune"),
    ("ORD-5004", "CUST-005", "FASH-002", "Running Shoes - Black", 2400.0, "2025-10-05", "delivered", "2025-10-07", 15, "22 Koregaon Park, Pune"),
    ("ORD-5005", "CUST-005", "HOME-001", "Ceramic Vase - White", 1200.0, "2025-09-15", "delivered", "2025-09-17", 15, "22 Koregaon Park, Pune"),
    ("ORD-5006", "CUST-005", "ELEC-002", "USB-C Charging Cable", 499.0, "2025-08-20", "delivered", "2025-08-22", 15, "22 Koregaon Park, Pune"),
    ("ORD-1006", "CUST-001", "HOME-001", "Ceramic Vase - White", 1200.0, "2025-09-01", "delivered", "2025-09-03", 15, "12 Marine Drive, Mumbai"),
    ("ORD-1007", "CUST-001", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2025-08-15", "delivered", "2025-08-17", 15, "12 Marine Drive, Mumbai"),
    ("ORD-1008", "CUST-001", "FASH-002", "Running Shoes - Black", 2400.0, "2025-07-20", "delivered", "2025-07-22", 15, "12 Marine Drive, Mumbai"),
    ("ORD-3004", "CUST-003", "FASH-001", "Cotton Kurta - Blue", 800.0, "2025-11-01", "delivered", "2025-11-03", 15, "88 Indiranagar, Bangalore"),
    ("ORD-3005", "CUST-003", "FASH-002", "Running Shoes - Black", 2400.0, "2025-10-10", "delivered", "2025-10-12", 15, "88 Indiranagar, Bangalore"),
    ("ORD-3006", "CUST-003", "HOME-002", "Scented Candle Set", 650.0, "2025-09-05", "delivered", "2025-09-07", 15, "88 Indiranagar, Bangalore"),
    ("ORD-3007", "CUST-003", "HOME-001", "Ceramic Vase - White", 1200.0, "2025-08-12", "delivered", "2025-08-14", 15, "88 Indiranagar, Bangalore"),

    # ── Arjun (serial abuser: 6 orders, 5 refunds) ──
    ("ORD-6001", "CUST-006", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-03-02", "delivered", "2026-03-05", 15, "15 HSR Layout, Bangalore"),
    ("ORD-6002", "CUST-006", "FASH-002", "Running Shoes - Black", 2400.0, "2026-02-08", "delivered", "2026-02-11", 15, "15 HSR Layout, Bangalore"),
    ("ORD-6003", "CUST-006", "HOME-001", "Ceramic Vase - White", 1200.0, "2026-01-18", "delivered", "2026-01-21", 15, "15 HSR Layout, Bangalore"),

    # ── Neha (new customer: 1 order, 0 refunds) ──
    ("ORD-7001", "CUST-007", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-03-09", "delivered", "2026-03-11", 15, "7 T Nagar, Chennai"),

    # ── Deepak (fraud ring: shares Rohit's address "42 MG Road, Karol Bagh, Delhi") ──
    ("ORD-8001", "CUST-008", "FASH-001", "Cotton Kurta - Blue", 800.0, "2026-02-20", "delivered", "2026-02-23", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-8002", "CUST-008", "FASH-002", "Running Shoes - Black", 2400.0, "2026-03-01", "delivered", "2026-03-04", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-8003", "CUST-008", "ELEC-002", "USB-C Charging Cable", 499.0, "2026-03-06", "delivered", "2026-03-08", 15, "42 MG Road, Karol Bagh, Delhi"),

    # ── Sunita (fraud ring: shares Rohit's address "42 MG Road, Karol Bagh, Delhi") ──
    ("ORD-9001", "CUST-009", "ELEC-001", "Wireless Earbuds Pro", 3500.0, "2026-02-28", "delivered", "2026-03-03", 15, "42 MG Road, Karol Bagh, Delhi"),
    ("ORD-9002", "CUST-009", "HOME-001", "Ceramic Vase - White", 1200.0, "2026-03-05", "delivered", "2026-03-07", 15, "42 MG Road, Karol Bagh, Delhi"),
]

# Cross-merchant claims (simulated Pine Labs network intelligence)
CROSS_MERCHANT_CLAIMS = [
    # Rohit — 2 claims at other merchants (FashionHub, ShoeZone)
    ("CUST-002", "FashionHub", "damaged_in_transit", 1800.0, "2026-02-25"),
    ("CUST-002", "ShoeZone", "damaged_in_transit", 3200.0, "2026-03-05"),
    # Vikram — 1 claim at another merchant (ElectroBazaar)
    ("CUST-004", "ElectroBazaar", "not_as_described", 4500.0, "2026-02-20"),
    # Arjun — 1 claim at another merchant (GadgetMart)
    ("CUST-006", "GadgetMart", "not_delivered", 2800.0, "2026-02-28"),
]

# Historical refunds (already processed — for dashboard stats & fraud patterns)
HISTORICAL_REFUNDS = [
    # Priya — 1 past refund (genuine)
    ("REF-H001", "ORD-1003", "CUST-001", 650.0, "defective", "Candle wax was melted on arrival", "en",
     8, "AUTO_APPROVE", 0.95, "approved", 3800),

    # Rohit — 8 past refunds (abuser pattern: always "damaged_in_transit", high value)
    ("REF-H002", "ORD-2002", "CUST-002", 3500.0, "damaged_in_transit", "Box was crushed", "en",
     82, "ESCALATE", 0.88, "escalated", 4100),
    ("REF-H003", "ORD-2003", "CUST-002", 800.0, "damaged_in_transit", "Torn packaging", "en",
     75, "ESCALATE", 0.82, "escalated", 3900),
    ("REF-H004", "ORD-2004", "CUST-002", 1200.0, "damaged_in_transit", "Arrived broken", "en",
     78, "ESCALATE", 0.85, "escalated", 4200),
    ("REF-H005", "ORD-2005", "CUST-002", 2400.0, "damaged_in_transit", "Damaged in transit", "en",
     80, "ESCALATE", 0.87, "escalated", 4000),
    ("REF-H006", "ORD-2006", "CUST-002", 3500.0, "damaged_in_transit", "Product was broken", "en",
     83, "ESCALATE", 0.90, "escalated", 3700),
    ("REF-H007", "ORD-2003", "CUST-002", 800.0, "damaged_in_transit", "Damaged goods", "en",
     76, "ESCALATE", 0.83, "escalated", 4300),
    ("REF-H008", "ORD-2004", "CUST-002", 1200.0, "damaged_in_transit", "Completely destroyed", "en",
     79, "ESCALATE", 0.86, "escalated", 3800),
    ("REF-H009", "ORD-2005", "CUST-002", 2400.0, "damaged_in_transit", "Shoes were scuffed badly", "en",
     81, "ESCALATE", 0.89, "escalated", 4100),

    # Anita — 3 past refunds (genuine, low frequency)
    ("REF-H010", "ORD-3002", "CUST-003", 499.0, "defective", "Cable stopped working after 2 days", "en",
     12, "AUTO_APPROVE", 0.93, "approved", 3200),
    ("REF-H011", "ORD-3003", "CUST-003", 1200.0, "damaged_in_transit", "Vase had a crack", "en",
     22, "AUTO_APPROVE", 0.90, "approved", 3500),
    ("REF-H012", "ORD-3001", "CUST-003", 3500.0, "defective", "Left earbud not working", "en",
     18, "AUTO_APPROVE", 0.91, "approved", 3300),

    # Vikram — 4 past refunds (suspicious: only high-value, always near return window end)
    ("REF-H013", "ORD-4002", "CUST-004", 3500.0, "not_as_described", "Not what I expected", "en",
     55, "INVESTIGATE", 0.72, "investigating", 4500),
    ("REF-H014", "ORD-4001", "CUST-004", 2400.0, "damaged_in_transit", "Shoe sole was loose", "en",
     52, "INVESTIGATE", 0.70, "investigating", 4200),
    ("REF-H015", "ORD-4002", "CUST-004", 3500.0, "defective", "Sound quality terrible", "en",
     58, "INVESTIGATE", 0.68, "investigating", 4800),
    ("REF-H016", "ORD-4003", "CUST-004", 800.0, "changed_mind", "Did not like the color", "en",
     45, "INVESTIGATE", 0.65, "investigating", 4100),

    # Arjun — 5 past refunds (serial abuser: different addresses, always "not_delivered")
    ("REF-H017", "ORD-6001", "CUST-006", 3500.0, "not_delivered", "Never received it", "en",
     90, "ESCALATE", 0.92, "escalated", 3600),
    ("REF-H018", "ORD-6002", "CUST-006", 2400.0, "not_delivered", "Package not delivered", "en",
     88, "ESCALATE", 0.91, "escalated", 3800),
    ("REF-H019", "ORD-6003", "CUST-006", 1200.0, "not_delivered", "Did not receive order", "en",
     91, "ESCALATE", 0.93, "escalated", 3500),
    ("REF-H020", "ORD-6001", "CUST-006", 3500.0, "not_delivered", "Says delivered but I didnt get", "en",
     92, "ESCALATE", 0.94, "escalated", 3700),
    ("REF-H021", "ORD-6002", "CUST-006", 2400.0, "not_delivered", "Not at my door", "en",
     89, "ESCALATE", 0.92, "escalated", 3900),

    # Deepak (fraud ring) — 1 past refund
    ("REF-H022", "ORD-8001", "CUST-008", 800.0, "damaged_in_transit", "Kurta had a stain", "en",
     42, "INVESTIGATE", 0.70, "investigating", 4000),

    # Sunita (fraud ring) — 1 past refund
    ("REF-H023", "ORD-9001", "CUST-009", 3500.0, "defective", "Earbuds crackling sound", "en",
     48, "INVESTIGATE", 0.68, "investigating", 4200),
]


async def seed_database():
    """Insert all demo data into the database."""
    db = await aiosqlite.connect(DB_PATH)

    # Check if already seeded
    cursor = await db.execute("SELECT COUNT(*) FROM customers")
    count = (await cursor.fetchone())[0]
    if count > 0:
        await db.close()
        return

    # Insert customers
    await db.executemany(
        "INSERT INTO customers (id, name, email, phone, total_orders, total_refunds, refund_rate, customer_type, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        CUSTOMERS,
    )

    # Insert products
    await db.executemany(
        "INSERT INTO products (sku, name, category, price, expected_refund_rate) VALUES (?, ?, ?, ?, ?)",
        PRODUCTS,
    )

    # Insert orders
    await db.executemany(
        "INSERT INTO orders (id, customer_id, product_sku, product_name, amount, order_date, delivery_status, delivery_date, return_window_days, shipping_address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ORDERS,
    )

    # Insert historical refunds
    await db.executemany(
        """INSERT INTO refunds (id, order_id, customer_id, amount, reason, message, language,
           risk_score, decision, confidence, status, processing_time_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        HISTORICAL_REFUNDS,
    )

    # Insert cross-merchant claims (Pine Labs network intelligence)
    await db.executemany(
        """INSERT INTO cross_merchant_claims (customer_id, merchant_name, claim_reason, claim_amount, claim_date)
           VALUES (?, ?, ?, ?, ?)""",
        CROSS_MERCHANT_CLAIMS,
    )

    await db.commit()
    await db.close()
    print("✅ Database seeded with demo data")
