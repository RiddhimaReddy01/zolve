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
                    withdrawable_balance INTEGER DEFAULT 0,
                    tier TEXT DEFAULT 'Basic',
                    credit_score INTEGER DEFAULT {DEFAULT_CREDIT_SCORE},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._ensure_column(cursor, "users", "withdrawable_balance", "INTEGER DEFAULT 0")

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
                    image_url TEXT,
                    description TEXT,
                    rating REAL DEFAULT 4.5,
                    review_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._ensure_column(cursor, "products", "image_url", "TEXT")
            self._ensure_column(cursor, "products", "description", "TEXT")
            self._ensure_column(cursor, "products", "rating", "REAL DEFAULT 4.5")
            self._ensure_column(cursor, "products", "review_count", "INTEGER DEFAULT 0")

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

            # Ad views (for ad-watching rewards)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ad_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    ad_id TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    coins_credited INTEGER DEFAULT 0
                )
            """)

            # Scratch card triggers (purchase-based)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scratch_card_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    purchase_id INTEGER NOT NULL REFERENCES purchases(id),
                    purchase_amount REAL NOT NULL,
                    result TEXT,
                    coins_won INTEGER DEFAULT 0,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scratched_at TIMESTAMP
                )
            """)

            # Easter eggs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS easter_eggs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    egg_type TEXT NOT NULL,
                    condition_met_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    unlocked_at TIMESTAMP,
                    coins_awarded INTEGER DEFAULT 200
                )
            """)

            # Tier events (for tracking tier progression)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tier_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    old_tier TEXT NOT NULL,
                    new_tier TEXT NOT NULL,
                    coins_at_change INTEGER NOT NULL,
                    behaviors_at_change INTEGER NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Z-World onboarding state
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS z_world_onboarding (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id),
                    intro_seen BOOLEAN DEFAULT 0,
                    club_action TEXT,
                    club_name TEXT,
                    club_id INTEGER,
                    invite_code TEXT,
                    accepted_coin_rules BOOLEAN DEFAULT 0,
                    signup_bonus_granted BOOLEAN DEFAULT 0,
                    first_scratch_card_id INTEGER,
                    completed_at TIMESTAMP
                )
            """)
            self._ensure_column(cursor, "z_world_onboarding", "club_id", "INTEGER")

            # Spin entitlements earned by actions, separate from coin-paid spins
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_entitlements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    entitlement_type TEXT NOT NULL,
                    source_event TEXT NOT NULL,
                    remaining_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)

            # Notification outbox for push-equivalent user messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    channel TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    deep_link TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP
                )
            """)

            # Financial events processed through the reward rule engine
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reward_coins INTEGER DEFAULT 0,
                    spins_unlocked INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON coin_transactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_behaviors_user ON behaviors(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_linked_accounts_user ON linked_accounts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchases(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ad_views_user ON ad_views(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scratch_cards_user ON scratch_card_triggers(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_easter_eggs_user ON easter_eggs(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tier_events_user ON tier_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entitlements_user ON game_entitlements(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_events_user ON financial_events(user_id)")

            self._seed_demo_data(cursor)

    def _ensure_column(self, cursor: sqlite3.Cursor, table_name: str, column_name: str, definition: str) -> None:
        """Add a column to existing SQLite databases created before a schema change."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row[1] for row in cursor.fetchall()}
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def _seed_demo_data(self, cursor: sqlite3.Cursor) -> None:
        """Seed initial demo data if database is empty."""
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (DEMO_USER_ID,))
        if cursor.fetchone()[0] == 0:
            # Create Riddhima as the primary demo user.
            cursor.execute("""
                INSERT INTO users (id, name, email, coin_balance, withdrawable_balance, tier, credit_score)
                VALUES (?, ?, ?, 0, 0, 'Basic', ?)
            """, (DEMO_USER_ID, DEMO_USER_NAME, DEMO_USER_EMAIL, DEFAULT_CREDIT_SCORE))
        else:
            cursor.execute("""
                UPDATE users SET name = ?, email = ? WHERE id = ?
            """, (DEMO_USER_NAME, DEMO_USER_EMAIL, DEMO_USER_ID))

        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] < 100:
            self._seed_products(cursor)

        # Seed mock ad_views for Riddhima (user_id=1) to show near-cap state
        cursor.execute("SELECT COUNT(*) FROM ad_views WHERE user_id = ?", (DEMO_USER_ID,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO ad_views (user_id, ad_id, started_at, completed_at, coins_credited)
                VALUES (?, ?, DATETIME('now', '-1 hour'), DATETIME('now', '-55 minutes'), 10)
            """, (DEMO_USER_ID, "ad_001"))
            cursor.execute("""
                INSERT INTO ad_views (user_id, ad_id, started_at, completed_at, coins_credited)
                VALUES (?, ?, DATETIME('now', '-30 minutes'), DATETIME('now', '-25 minutes'), 10)
            """, (DEMO_USER_ID, "ad_002"))

        # Seed unclaimed easter egg for Riddhima
        cursor.execute("SELECT COUNT(*) FROM easter_eggs WHERE user_id = ? AND egg_type = ?", (DEMO_USER_ID, "bank_verified"))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO easter_eggs (user_id, egg_type, condition_met_at, coins_awarded)
                VALUES (?, ?, CURRENT_TIMESTAMP, 200)
            """, (DEMO_USER_ID, "bank_verified"))

        # Seed tier event for Riddhima showing Basic -> Silver progression
        cursor.execute("SELECT COUNT(*) FROM tier_events WHERE user_id = ?", (DEMO_USER_ID,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO tier_events (user_id, old_tier, new_tier, coins_at_change, behaviors_at_change, changed_at)
                VALUES (?, ?, ?, ?, ?, datetime('now', '-1 day'))
            """, (DEMO_USER_ID, 'Basic', 'Silver', 1000, 2))

        if False:

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

    def _seed_products(self, cursor: sqlite3.Cursor) -> None:
        """Seed Z-Kart products with images and descriptions."""
        cursor.execute("DELETE FROM products")
        products = [
            # Food & Delivery (4 items, 100-200 coins)
            ("Starbucks $50 Gift Card", "Food", 50, 15, 200, "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=300&fit=crop", "Premium coffee and fresh pastries. Perfect daily treat with Z-Coin savings."),
            ("Swiggy ₹500 Voucher", "Food", 50, 12, 220, "https://images.unsplash.com/photo-1504674900874-dde2893a9915?w=300&h=300&fit=crop", "Order your favorite meals with fast delivery. Z-Coin discount saves you cash."),
            ("Domino's Pizza ₹1000", "Food", 30, 15, 120, "https://images.unsplash.com/photo-1628840042765-356cda07f857?w=300&h=300&fit=crop", "Two medium pizzas coupon. Enjoy pizza night savings with Z-Coins."),
            ("McDonald's Breakfast Pass", "Food", 25, 18, 100, "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=300&fit=crop", "5 breakfast vouchers included. Great value when purchased with coins."),

            # Shopping & Retail (4 items, 400-500 coins)
            ("Amazon ₹5000 Gift Card", "Retail", 100, 10, 450, "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?w=300&h=300&fit=crop", "Shop millions of products from electronics to fashion. Maximize savings with Z-Coins."),
            ("Flipkart ₹5000 Voucher", "Retail", 100, 12, 480, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop", "Electronics, fashion, home goods. Z-Coin users save extra on checkout."),
            ("H&M Fashion Gift Card", "Retail", 75, 15, 350, "https://images.unsplash.com/photo-1595526014635-fef45624d26f?w=300&h=300&fit=crop", "Latest trendy clothing and accessories. Double your savings with coins."),
            ("Nike Store Credit ₹4500", "Retail", 100, 12, 460, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop", "Sports shoes, apparel, and gear. Top picks for athletes using Z-Coins."),

            # Travel & Experiences (3 items, 200-480 coins)
            ("Uber Ride Credits $50", "Travel", 50, 10, 220, "https://images.unsplash.com/photo-1449965408869-efd32723dfa5?w=300&h=300&fit=crop", "Safe rides to anywhere in the city. Cheaper with Z-Coin redemptions."),
            ("MakeMyTrip Travel Voucher", "Travel", 100, 8, 480, "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=300&h=300&fit=crop", "Book flights, hotels, and vacation packages. Z-Coin discount unlocks best deals."),
            ("Airbnb Travel Credit $50", "Travel", 50, 12, 230, "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=300&h=300&fit=crop", "Unique stays worldwide. Z-Coin users get exclusive discounts."),

            # Entertainment & Streaming (4 items, 50-70 coins)
            ("Netflix Premium 1M", "Entertainment", 16, 20, 70, "https://images.unsplash.com/photo-1522869635100-ce306162e6f9?w=300&h=300&fit=crop", "Unlimited movies and shows in HD. Pay even less with Z-Coins."),
            ("Spotify Premium 1M", "Entertainment", 13, 25, 55, "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&h=300&fit=crop", "Ad-free music with offline downloads. Best value with coin discount."),
            ("Disney+ Subscription", "Entertainment", 12, 22, 52, "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?w=300&h=300&fit=crop", "Disney, Marvel, Pixar, and more. Huge savings when you use coins."),
            ("YouTube Premium 1M", "Entertainment", 15, 18, 68, "https://images.unsplash.com/photo-1634438253634-5a34bd7e3f6f?w=300&h=300&fit=crop", "Ad-free videos, downloads, and YouTube Music. Coin redemption saves money."),

            # Fitness & Wellness (3 items, 200-450 coins)
            ("Cult.Fit Premium 3M", "Fitness", 100, 15, 450, "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&h=300&fit=crop", "Gym classes, yoga, and meditation. Great fitness value with Z-Coin savings."),
            ("Decathlon Shopping Card", "Fitness", 75, 12, 350, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop", "Sports equipment, apparel, and gear. Z-Coin buyers love the savings."),
            ("Apple Fitness+ 3M", "Fitness", 45, 20, 200, "https://images.unsplash.com/photo-1524594917303-827c4d8dc422?w=300&h=300&fit=crop", "Premium fitness classes on Apple devices. Discount unlocked with coins."),

            # Tech & Gadgets (3 items, 220-1100 coins)
            ("Apple AirPods Pro", "Tech", 249, 8, 1100, "https://images.unsplash.com/photo-1606841837239-c5a1a3a07af7?w=300&h=300&fit=crop", "Premium wireless earbuds with noise cancellation. Save $20+ with Z-Coins."),
            ("Samsung Galaxy Buds", "Tech", 149, 10, 680, "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?w=300&h=300&fit=crop", "High-quality sound and comfort. Z-Coin redemption gives extra value."),
            ("Anker Power Bank 25000mAh", "Tech", 50, 15, 220, "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=300&h=300&fit=crop", "Fast charging and portable. Smart purchase with coin discount."),
        ]

        rows = []
        for name, category, price, discount, coins, image, description in products:
            rows.append((
                name,
                category,
                price,
                discount,
                coins,
                image,
                description,
            ))

        cursor.executemany("""
            INSERT INTO products (name, category, base_price, coin_discount_pct, coins_required, image_url, description, rating, review_count, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [(*row, 4.5 + (hash(row[0]) % 10) / 10, 100 + (hash(row[0]) % 200), 50) for row in rows])

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

    def update_withdrawable_balance(self, user_id: int, amount: int) -> None:
        """Update verified, withdrawable coin balance."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET withdrawable_balance = withdrawable_balance + ? WHERE id = ?
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

    def add_ad_view(self, user_id: int, ad_id: str) -> int:
        """Create a new ad_view record when user starts watching an ad.

        Args:
            user_id: User ID
            ad_id: Advertisement ID

        Returns:
            ad_view_id of the created record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ad_views (user_id, ad_id)
                VALUES (?, ?)
            """, (user_id, ad_id))
            return cursor.lastrowid

    def get_ad_view(self, ad_view_id: int) -> Optional[Dict[str, Any]]:
        """Get an ad_view record by ID.

        Args:
            ad_view_id: Ad view ID

        Returns:
            dict with ad_view data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ad_views WHERE id = ?", (ad_view_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def complete_ad_view(self, ad_view_id: int, coins_credited: int) -> None:
        """Mark an ad_view as completed and credit coins.

        Args:
            ad_view_id: Ad view ID
            coins_credited: Number of coins to credit
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ad_views SET completed_at = CURRENT_TIMESTAMP, coins_credited = ? WHERE id = ?
            """, (coins_credited, ad_view_id))

    def get_today_ad_count(self, user_id: int) -> int:
        """Count completed ad views for user today.

        Args:
            user_id: User ID

        Returns:
            Number of ads completed today
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ad_views
                WHERE user_id = ? AND completed_at IS NOT NULL
                AND DATE(completed_at) = DATE('now')
            """, (user_id,))
            return cursor.fetchone()[0]

    def add_tier_event(self, user_id: int, old_tier: str, new_tier: str, coins: int, behaviors: int) -> int:
        """Log a tier progression event.

        Args:
            user_id: User ID
            old_tier: Previous tier (Basic, Silver, Gold)
            new_tier: New tier (Basic, Silver, Gold)
            coins: Coin balance at time of change
            behaviors: Verified behavior count at time of change

        Returns:
            tier_event_id of the created record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tier_events (user_id, old_tier, new_tier, coins_at_change, behaviors_at_change)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, old_tier, new_tier, coins, behaviors))
            return cursor.lastrowid

    def get_tier_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get tier progression history for a user.

        Args:
            user_id: User ID

        Returns:
            List of tier events ordered by date (newest first)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, old_tier, new_tier, coins_at_change, behaviors_at_change, changed_at
                FROM tier_events
                WHERE user_id = ?
                ORDER BY changed_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_z_world_onboarding(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get Z-World onboarding state for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM z_world_onboarding WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def upsert_z_world_onboarding(
        self,
        user_id: int,
        club_action: str,
        club_name: Optional[str],
        invite_code: Optional[str],
        first_scratch_card_id: int,
        club_id: Optional[int] = None,
    ) -> None:
        """Mark forced Z-World onboarding complete."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO z_world_onboarding (
                    user_id, intro_seen, club_action, club_name, club_id, invite_code,
                    accepted_coin_rules, signup_bonus_granted, first_scratch_card_id, completed_at
                )
                VALUES (?, 1, ?, ?, ?, ?, 1, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    intro_seen = 1,
                    club_action = excluded.club_action,
                    club_name = excluded.club_name,
                    club_id = excluded.club_id,
                    invite_code = excluded.invite_code,
                    accepted_coin_rules = 1,
                    first_scratch_card_id = excluded.first_scratch_card_id,
                    completed_at = COALESCE(z_world_onboarding.completed_at, CURRENT_TIMESTAMP)
            """, (user_id, club_action, club_name, club_id, invite_code, first_scratch_card_id))

    def grant_game_entitlement(self, user_id: int, entitlement_type: str, source_event: str, count: int) -> int:
        """Grant game plays earned through behavior."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO game_entitlements (user_id, entitlement_type, source_event, remaining_count)
                VALUES (?, ?, ?, ?)
            """, (user_id, entitlement_type, source_event, count))
            return cursor.lastrowid

    def get_available_entitlement_count(self, user_id: int, entitlement_type: str) -> int:
        """Return total unconsumed entitlements of a type."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(remaining_count), 0) FROM game_entitlements
                WHERE user_id = ? AND entitlement_type = ? AND remaining_count > 0
            """, (user_id, entitlement_type))
            return cursor.fetchone()[0]

    def consume_game_entitlement(self, user_id: int, entitlement_type: str) -> Optional[Dict[str, Any]]:
        """Consume one earned game entitlement if available."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM game_entitlements
                WHERE user_id = ? AND entitlement_type = ? AND remaining_count > 0
                ORDER BY created_at ASC, id ASC
                LIMIT 1
            """, (user_id, entitlement_type))
            row = cursor.fetchone()
            if not row:
                return None
            cursor.execute("""
                UPDATE game_entitlements
                SET remaining_count = remaining_count - 1
                WHERE id = ?
            """, (row["id"],))
            consumed = dict(row)
            consumed["remaining_count"] -= 1
            return consumed

    def add_notification(self, user_id: int, channel: str, title: str, message: str, deep_link: str) -> int:
        """Add a push-equivalent notification to the outbox."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (user_id, channel, title, message, deep_link)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, channel, title, message, deep_link))
            return cursor.lastrowid

    def get_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notifications for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def add_financial_event(
        self,
        user_id: int,
        event_type: str,
        status: str,
        reward_coins: int,
        spins_unlocked: int,
        metadata: str,
    ) -> int:
        """Record a processed financial event."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO financial_events (
                    user_id, event_type, status, reward_coins, spins_unlocked, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, event_type, status, reward_coins, spins_unlocked, metadata))
            return cursor.lastrowid

    def get_financial_events(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent financial reward events for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM financial_events
                WHERE user_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def has_payment_reward_today(self, user_id: int) -> bool:
        """Check if user already claimed payment reward today.

        Prevents double-claiming of on_time_payment rewards on the same day.

        Args:
            user_id: User ID

        Returns:
            True if a payment reward already exists today, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM financial_events
                WHERE user_id = ? AND event_type = ? AND status = ?
                AND DATE(created_at) = DATE('now')
            """, (user_id, 'payment_completed_on_time', 'rewarded'))
            count = cursor.fetchone()[0]
            return count > 0

    def get_verified_behavior_count(self, user_id: int) -> int:
        """Get count of verified behaviors for a user (same as count_verified_behaviors).

        Args:
            user_id: User ID

        Returns:
            Number of verified behaviors
        """
        return self.count_verified_behaviors(user_id)

    def add_scratch_card_trigger(self, user_id: int, purchase_id: int, purchase_amount: float) -> int:
        """Create a scratch card trigger on purchase.

        Args:
            user_id: User ID
            purchase_id: Purchase ID that triggered the card
            purchase_amount: Amount paid for the purchase

        Returns:
            trigger_id of the created scratch card
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scratch_card_triggers (user_id, purchase_id, purchase_amount)
                VALUES (?, ?, ?)
            """, (user_id, purchase_id, purchase_amount))
            return cursor.lastrowid

    def get_pending_scratch_cards(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all unscratched (pending) scratch cards for a user.

        Args:
            user_id: User ID

        Returns:
            List of pending scratch card triggers
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scratch_card_triggers
                WHERE user_id = ? AND scratched_at IS NULL
                ORDER BY triggered_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_scratch_card(self, trigger_id: int) -> Optional[Dict[str, Any]]:
        """Get a scratch card trigger by ID.

        Args:
            trigger_id: Scratch card trigger ID

        Returns:
            dict with scratch card data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scratch_card_triggers WHERE id = ?", (trigger_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def complete_scratch_card(self, trigger_id: int, result: str, coins_won: int) -> None:
        """Mark a scratch card as scratched and record the result.

        Args:
            trigger_id: Scratch card trigger ID
            result: Result type (e.g., 'small_win', 'medium_win', 'jackpot', 'try_again')
            coins_won: Number of coins won
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scratch_card_triggers
                SET scratched_at = CURRENT_TIMESTAMP, result = ?, coins_won = ?
                WHERE id = ?
            """, (result, coins_won, trigger_id))

    def mark_scratch_card_scratched(self, trigger_id: int, result: str, coins_won: int) -> None:
        """Alias for complete_scratch_card for consistency.

        Args:
            trigger_id: Scratch card trigger ID
            result: Result type (e.g., 'small_win', 'medium_win', 'jackpot', 'try_again')
            coins_won: Number of coins won
        """
        self.complete_scratch_card(trigger_id, result, coins_won)

    def add_easter_egg(self, user_id: int, egg_type: str) -> int:
        """Create an easter egg for a user when a condition is met.

        Args:
            user_id: User ID
            egg_type: Type of easter egg (e.g., 'bank_verified', 'first_purchase')

        Returns:
            easter_egg_id of the created record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO easter_eggs (user_id, egg_type)
                VALUES (?, ?)
            """, (user_id, egg_type))
            return cursor.lastrowid

    def has_easter_egg(self, user_id: int, egg_type: str) -> bool:
        """Check if user already has a specific easter egg type.

        Args:
            user_id: User ID
            egg_type: Easter egg type

        Returns:
            True if user already has this egg type
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM easter_eggs WHERE user_id = ? AND egg_type = ?",
                (user_id, egg_type),
            )
            return cursor.fetchone()[0] > 0

    def get_easter_eggs(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all easter eggs for a user.

        Args:
            user_id: User ID

        Returns:
            List of easter eggs
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM easter_eggs WHERE user_id = ? ORDER BY condition_met_at DESC",
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_easter_egg(self, egg_id: int) -> Optional[Dict[str, Any]]:
        """Get a single easter egg by ID.

        Args:
            egg_id: Easter egg ID

        Returns:
            dict with easter egg data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM easter_eggs WHERE id = ?", (egg_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def claim_easter_egg(self, egg_id: int, user_id: int) -> Dict[str, Any]:
        """Claim an easter egg and mark it as unlocked.

        Args:
            egg_id: Easter egg ID
            user_id: User ID (for validation)

        Returns:
            dict with updated easter egg data

        Raises:
            UserNotFoundError: If egg not found or doesn't belong to user
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM easter_eggs WHERE id = ? AND user_id = ?",
                (egg_id, user_id),
            )
            row = cursor.fetchone()
            if not row:
                raise UserNotFoundError(f"Easter egg {egg_id} not found for user {user_id}")

            cursor.execute(
                "UPDATE easter_eggs SET unlocked_at = CURRENT_TIMESTAMP WHERE id = ?",
                (egg_id,),
            )
            cursor.execute(
                "SELECT * FROM easter_eggs WHERE id = ?",
                (egg_id,),
            )
            return dict(cursor.fetchone())

    def reset_onboarding(self, user_id: int) -> None:
        """Reset onboarding state for a clean demo run.

        Args:
            user_id: User ID to reset
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM z_world_onboarding WHERE user_id = ?", (user_id,))

    def reset_user_balance(self, user_id: int) -> None:
        """Reset user balance and tier for a fresh demo.

        Args:
            user_id: User ID to reset
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET coin_balance = 0, tier = 'Basic' WHERE id = ?",
                (user_id,),
            )

    def reset_demo_state(self, user_id: int) -> None:
        """Complete reset of all demo state for a user, enabling a fresh start.

        Clears all game progress, notifications, and financial events while preserving
        user identity. This is idempotent and safe to call multiple times.

        Args:
            user_id: User ID to reset (typically 1 for demo)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM z_world_onboarding WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM game_entitlements WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM scratch_card_triggers WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM financial_events WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM easter_eggs WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM coin_transactions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM behaviors WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM ad_views WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM tier_events WHERE user_id = ?", (user_id,))
            cursor.execute(
                "UPDATE users SET coin_balance = 0, tier = 'Basic', withdrawable_balance = 0 WHERE id = ?",
                (user_id,),
            )
