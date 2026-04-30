"""Database initialization and core operations."""

import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime

from constants import DATABASE_PATH, DEMO_USER_ID, DEMO_USER_NAME, DEMO_USER_EMAIL, DEFAULT_CREDIT_SCORE
from exceptions import UserNotFoundError


class Database:
    """Database connection and core operations."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.initialize_schema()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Create all tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    coin_balance INTEGER DEFAULT 0,
                    tier TEXT DEFAULT 'Basic',
                    credit_score INTEGER DEFAULT {DEFAULT_CREDIT_SCORE},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Coin transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coin_transactions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Behaviors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS behaviors (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    behavior_type TEXT NOT NULL,
                    verified BOOLEAN DEFAULT 0,
                    verification_source TEXT,
                    behavior_data TEXT,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Linked bank accounts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS linked_accounts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    bank_name TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_synced TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Bank transactions (mock data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_transactions (
                    id INTEGER PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    transaction_date DATE NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    due_date DATE,
                    is_on_time BOOLEAN,
                    status TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES linked_accounts(account_id)
                )
            """)

            # Credit score history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credit_score_history (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    score_date DATE NOT NULL,
                    bureau TEXT NOT NULL,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Savings goals
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS savings_goals (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    goal_name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Products (Z-Kart)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    base_price REAL NOT NULL,
                    coin_discount_pct INTEGER DEFAULT 5,
                    coins_required INTEGER NOT NULL,
                    stock INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Purchases
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    coins_spent INTEGER NOT NULL,
                    price_paid REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON coin_transactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_behaviors_user ON behaviors(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_linked_accounts_user ON linked_accounts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchases(user_id)")

            self._seed_demo_data(cursor)

    def _seed_demo_data(self, cursor: sqlite3.Cursor) -> None:
        """Seed initial demo data if database is empty."""
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Create demo user
            cursor.execute("""
                INSERT INTO users (id, name, email, coin_balance, tier, credit_score)
                VALUES (?, ?, ?, 0, 'Basic', ?)
            """, (DEMO_USER_ID, DEMO_USER_NAME, DEMO_USER_EMAIL, DEFAULT_CREDIT_SCORE))

            # Add 8 sample products
            products = [
                ("Starbucks Gift Card", "Food", 500, 10, 250, 50),
                ("Swiggy Voucher ₹500", "Food", 500, 10, 250, 50),
                ("Amazon Gift Card ₹1000", "Retail", 1000, 8, 500, 30),
                ("Make My Trip Voucher", "Travel", 1500, 7, 750, 20),
                ("Netflix Subscription (1 month)", "Entertainment", 199, 12, 100, 100),
                ("Spotify Premium (1 month)", "Entertainment", 119, 15, 60, 100),
                ("Decathlon Voucher ₹2000", "Retail", 2000, 5, 1000, 15),
                ("Blinkit Coupon ₹500", "Food", 500, 10, 250, 50),
            ]

            for name, category, price, discount, coins_req, stock in products:
                cursor.execute("""
                    INSERT INTO products (name, category, base_price, coin_discount_pct, coins_required, stock)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, category, price, discount, coins_req, stock))

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_balance(self, user_id: int) -> int:
        """Get user coin balance."""
        user = self.get_user(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user["coin_balance"]

    def get_user_tier(self, user_id: int) -> str:
        """Get user tier."""
        user = self.get_user(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user["tier"]

    def update_user_balance(self, user_id: int, amount: int) -> None:
        """Update user coin balance."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET coin_balance = coin_balance + ? WHERE id = ?
            """, (amount, user_id))

    def update_user_tier(self, user_id: int, tier: str) -> None:
        """Update user tier."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET tier = ? WHERE id = ?", (tier, user_id))

    def add_coin_transaction(self, user_id: int, amount: int, event_type: str, description: str) -> int:
        """Log a coin transaction."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO coin_transactions (user_id, amount, event_type, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, amount, event_type, description))
            return cursor.lastrowid

    def add_behavior(self, user_id: int, behavior_type: str, verified: bool, source: str, data: str) -> int:
        """Log a behavior."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO behaviors (user_id, behavior_type, verified, verification_source, behavior_data)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, behavior_type, verified, source, data))
            return cursor.lastrowid

    def get_user_behaviors(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all behaviors for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM behaviors WHERE user_id = ? ORDER BY completed_at DESC", (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_verified_behaviors(self, user_id: int) -> List[Dict[str, Any]]:
        """Get only verified behaviors for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM behaviors WHERE user_id = ? AND verified = 1 ORDER BY completed_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def count_verified_behaviors(self, user_id: int) -> int:
        """Count verified behaviors for user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM behaviors WHERE user_id = ? AND verified = 1", (user_id,))
            return cursor.fetchone()[0]

    def get_transaction_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user transaction history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM coin_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY category, name")
            return [dict(row) for row in cursor.fetchall()]

    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_purchase(self, user_id: int, product_id: int, coins_spent: int, price_paid: float) -> int:
        """Record a purchase."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO purchases (user_id, product_id, coins_spent, price_paid)
                VALUES (?, ?, ?, ?)
            """, (user_id, product_id, coins_spent, price_paid))
            return cursor.lastrowid

    def link_bank_account(self, user_id: int, bank_name: str, account_number: str, account_id: str) -> int:
        """Link a bank account for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO linked_accounts (user_id, bank_name, account_number, account_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, bank_name, account_number, account_id))
            return cursor.lastrowid

    def get_linked_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all linked accounts for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM linked_accounts WHERE user_id = ? ORDER BY linked_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
