import aiosqlite
import os
from config import DATABASE_PATH

DB_PATH = DATABASE_PATH


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA busy_timeout=5000")
    return db


async def init_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA busy_timeout=5000")

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            total_orders INTEGER DEFAULT 0,
            total_refunds INTEGER DEFAULT 0,
            refund_rate REAL DEFAULT 0.0,
            customer_type TEXT DEFAULT 'regular',
            city TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            expected_refund_rate REAL DEFAULT 0.05
        );

        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT NOT NULL,
            amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            delivery_status TEXT DEFAULT 'delivered',
            delivery_date TEXT,
            return_window_days INTEGER DEFAULT 15,
            shipping_address TEXT DEFAULT '',
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_sku) REFERENCES products(sku)
        );

        CREATE TABLE IF NOT EXISTS refunds (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT NOT NULL,
            message TEXT DEFAULT '',
            language TEXT DEFAULT 'en',
            risk_score INTEGER,
            decision TEXT,
            confidence REAL,
            reasoning_json TEXT,
            action_type TEXT,
            pine_labs_ref TEXT,
            processing_time_ms INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            refund_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            detail TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (refund_id) REFERENCES refunds(id)
        );

        CREATE TABLE IF NOT EXISTS cross_merchant_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            merchant_name TEXT NOT NULL,
            claim_reason TEXT NOT NULL,
            claim_amount REAL NOT NULL,
            claim_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    """)

    await db.commit()
    await db.close()
