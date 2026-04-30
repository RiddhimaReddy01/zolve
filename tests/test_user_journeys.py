"""
Comprehensive user journey tests for Zolve backend.

Tests full real-world flows: earn coins → apply coin boost → checkout.
Uses mock data from public sources and simulated bank/credit data.

TWO-TIER COIN SYSTEM:
  1. WITHDRAWABLE COINS (from bank verification)
     - Earned by: On-time payments, credit score improvement, verified behaviors
     - Can be: Spent in Z-Kart (with extra discount) OR redeemed to cash
     - Example: Bank verifies $50 credit boost → 400 withdrawable coins earned

  2. ECOSYSTEM COINS (from engagement)
     - Earned by: Daily check-in (50), ads (10), education (150), referrals (300)
     - Can be: Spent in spending sinks (flash deals, clubs, auctions)
     - Cannot be: Redeemed to cash
     - Example: Daily check-in → 50 ecosystem coins

TOTAL BALANCE = Withdrawable + Ecosystem
Example: Total 1000 coins = 900 withdrawable (can cash out) + 100 ecosystem (engagement)
"""

import requests
import time
import json
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime


BASE_URL = "http://localhost:8000/api"
DEMO_USER_ID = 1


@dataclass
class TestResult:
    """Test result tracking."""
    name: str
    passed: bool
    message: str
    timestamp: str = ""
    response: Dict[str, Any] = None

    def __post_init__(self):
        self.timestamp = datetime.now().isoformat()


class TestSuite:
    """End-to-end user journey test suite."""

    def __init__(self):
        self.user_id = DEMO_USER_ID
        self.results: List[TestResult] = []
        self.state = {
            "initial_balance": 0,
            "linked_account": None,
            "verified_behaviors": [],
            "products_purchased": [],
        }

    def log_result(self, name: str, passed: bool, message: str, response: Dict[str, Any] = None):
        """Log test result."""
        result = TestResult(name=name, passed=passed, message=message, response=response)
        self.results.append(result)
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {name}")
        print(f"  {message}")
        if response and not passed:
            print(f"  Response: {response}")

    # ===== PHASE 1: Setup & Discovery =====

    def test_health_check(self):
        """Verify backend is running."""
        try:
            resp = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=5)
            self.log_result(
                "Health Check",
                resp.status_code == 200,
                f"Backend health status: {resp.json()}",
                resp.json() if resp.status_code != 200 else None,
            )
        except Exception as e:
            self.log_result("Health Check", False, f"Cannot connect to backend: {e}")

    def test_get_user_dashboard(self):
        """Get user dashboard data."""
        try:
            resp = requests.get(f"{BASE_URL}/user/{self.user_id}")
            if resp.status_code == 200:
                data = resp.json()
                self.state["initial_balance"] = data.get("balance", 0)
                self.log_result(
                    "Get User Dashboard",
                    True,
                    f"User: {data.get('name')}, Initial balance: {data.get('balance')} coins",
                    data,
                )
            else:
                self.log_result(
                    "Get User Dashboard",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get User Dashboard", False, str(e))

    def test_list_zmart_products(self):
        """Discover Z-Kart products (where coins apply for extra discounts)."""
        try:
            resp = requests.get(f"{BASE_URL}/zkart/products")
            if resp.status_code == 200:
                products = resp.json()
                if products:
                    sample = products[0]
                    self.log_result(
                        "List Z-Kart Products",
                        True,
                        f"Found {len(products)} products. Sample: {sample.get('name')} - ${sample.get('base_price')}, requires {sample.get('coins_required')} coins for {sample.get('coin_discount_pct')}% extra discount",
                        {"total_products": len(products), "sample": sample},
                    )
                else:
                    self.log_result("List Z-Kart Products", False, "No products found")
            else:
                self.log_result(
                    "List Z-Kart Products",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("List Z-Kart Products", False, str(e))

    def test_get_categories(self):
        """Get product categories."""
        try:
            resp = requests.get(f"{BASE_URL}/zkart/categories")
            if resp.status_code == 200:
                categories = resp.json()
                self.log_result(
                    "Get Product Categories",
                    len(categories) > 0,
                    f"Found {len(categories)} categories: {', '.join(categories[:5])}{'...' if len(categories) > 5 else ''}",
                    {"categories": categories},
                )
            else:
                self.log_result(
                    "Get Product Categories",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Product Categories", False, str(e))

    # ===== PHASE 2: Bank Linking & Verification =====

    def test_link_bank_account(self):
        """Link bank account for behavior verification."""
        try:
            payload = {
                "user_id": self.user_id,
                "bank_name": "HDFC",
                "account_number": "1234567890",
            }
            resp = requests.post(f"{BASE_URL}/bank/link", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                self.state["linked_account"] = data.get("account_id")
                self.log_result(
                    "Link Bank Account",
                    True,
                    f"Bank linked: {data.get('bank_name')}, Status: {data.get('status')}",
                    data,
                )
            else:
                self.log_result(
                    "Link Bank Account",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Link Bank Account", False, str(e))

    def test_get_bank_transactions(self):
        """Retrieve mock bank transactions."""
        try:
            resp = requests.get(f"{BASE_URL}/bank/transactions/{self.user_id}")
            if resp.status_code == 200:
                transactions = resp.json()
                if transactions:
                    self.log_result(
                        "Get Bank Transactions",
                        True,
                        f"Retrieved {len(transactions)} transactions",
                        {"total": len(transactions), "sample": transactions[0]},
                    )
                else:
                    self.log_result("Get Bank Transactions", False, "No transactions found")
            else:
                self.log_result(
                    "Get Bank Transactions",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Bank Transactions", False, str(e))

    def test_verify_behaviors(self):
        """Verify financial behaviors and earn WITHDRAWABLE coins.

        WITHDRAWABLE COIN SOURCES:
        - On-Time Payment: 500 coins (verified from bank transactions)
        - Credit Score Improvement: 400 coins (verified from credit bureau)
        - Savings Milestone: 350 coins (verified from bank data)
        - Direct Deposit: 200 coins (verified salary deposits)

        These coins can be:
        1. Redeemed to cash (withdraw to bank account)
        2. Spent in Z-Kart for extra discount (5-10% off)
        3. Spent in spending sinks (flash deals, clubs, auctions)
        """
        try:
            resp = requests.post(f"{BASE_URL}/bank/verify-behaviors/{self.user_id}")
            if resp.status_code == 200:
                behaviors = resp.json()
                self.state["verified_behaviors"] = behaviors
                coins_awarded = sum(b.get("coins_awarded", 0) for b in behaviors)
                self.log_result(
                    "Verify Behaviors",
                    True,
                    f"Verified {len(behaviors)} financial behaviors, awarded {coins_awarded} WITHDRAWABLE coins (can cash out or spend)",
                    {
                        "behaviors_count": len(behaviors),
                        "coins_awarded": coins_awarded,
                        "coin_type": "withdrawable",
                        "details": behaviors,
                    },
                )
            else:
                self.log_result(
                    "Verify Behaviors",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Verify Behaviors", False, str(e))

    def test_get_credit_score(self):
        """Check credit score and improvement potential."""
        try:
            resp = requests.get(f"{BASE_URL}/bank/credit-score/{self.user_id}")
            if resp.status_code == 200:
                data = resp.json()
                self.log_result(
                    "Get Credit Score",
                    True,
                    f"Score: {data.get('current_score')}, Improvement: {data.get('improvement')}, Coins available: {data.get('coins_available')}",
                    data,
                )
            else:
                self.log_result(
                    "Get Credit Score",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Credit Score", False, str(e))

    # ===== PHASE 3: Coin Earning & Management =====

    def test_earn_coins_action(self):
        """Earn coins from action (e.g., daily check-in)."""
        try:
            payload = {
                "user_id": self.user_id,
                "action_type": "daily_checkin",
            }
            resp = requests.post(f"{BASE_URL}/coins/earn", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                self.log_result(
                    "Earn Coins (Daily Check-in)",
                    True,
                    f"Earned {data.get('coins_earned')} coins, New balance: {data.get('new_balance')}",
                    data,
                )
            else:
                self.log_result(
                    "Earn Coins (Daily Check-in)",
                    False,
                    f"Failed with status {resp.status_code}: {resp.json().get('detail', '')}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Earn Coins (Daily Check-in)", False, str(e))

    def test_get_balance(self):
        """Check current coin balance - two-tier system.

        BALANCE BREAKDOWN:
        - WITHDRAWABLE: Coins from verified bank behaviors (on-time payment, credit improvement)
          → Can redeem to cash OR spend in Z-Kart for extra discount
        - ECOSYSTEM: Coins from engagement (daily check-in, ads, referrals)
          → Can only spend in spending sinks or Z-Kart
        - TOTAL: Withdrawable + Ecosystem
        """
        try:
            resp = requests.get(f"{BASE_URL}/coins/balance/{self.user_id}")
            if resp.status_code == 200:
                data = resp.json()
                total = data.get('balance', 0)
                withdrawable = data.get('withdrawable_balance', 0)
                ecosystem = data.get('ecosystem_balance', 0)
                self.log_result(
                    "Get Coin Balance",
                    True,
                    f"Total: {total} coins | Withdrawable (can cash out): {withdrawable} coins | Ecosystem (engagement): {ecosystem} coins | Tier: {data.get('tier')}",
                    data,
                )
            else:
                self.log_result(
                    "Get Coin Balance",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Coin Balance", False, str(e))

    def test_get_coin_history(self):
        """Get coin transaction history."""
        try:
            resp = requests.get(f"{BASE_URL}/coins/history/{self.user_id}?limit=20")
            if resp.status_code == 200:
                transactions = resp.json()
                if transactions:
                    self.log_result(
                        "Get Coin History",
                        True,
                        f"Retrieved {len(transactions)} transactions",
                        {
                            "total": len(transactions),
                            "sample": transactions[0],
                        },
                    )
                else:
                    self.log_result("Get Coin History", False, "No transactions found")
            else:
                self.log_result(
                    "Get Coin History",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Coin History", False, str(e))

    # ===== PHASE 4: Z-Kart Purchase (with coin boost) =====

    def test_list_products_by_category(self):
        """Browse products by category."""
        try:
            resp = requests.get(f"{BASE_URL}/zkart/products?category=Food")
            if resp.status_code == 200:
                products = resp.json()
                if products:
                    self.log_result(
                        "List Products by Category",
                        True,
                        f"Found {len(products)} Food products",
                        {
                            "category": "Food",
                            "products": len(products),
                            "sample": products[0],
                        },
                    )
                else:
                    self.log_result("List Products by Category", False, "No products in category")
            else:
                self.log_result(
                    "List Products by Category",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("List Products by Category", False, str(e))

    def test_get_product_details(self):
        """Get details of a specific product in Z-Kart.

        COIN BOOST IN Z-KART:
        Product can be purchased in two ways:
        1. Regular price: Full $X cost
        2. With coins: Spend coins to get 5-10% extra discount

        Example:
        Product: Starbucks Gift Card
        Regular price: $50
        With 250 coins: 10% discount = $5 savings → pay $45 + spend 250 coins
        """
        try:
            resp = requests.get(f"{BASE_URL}/zkart/products/1")
            if resp.status_code == 200:
                product = resp.json()
                base_price = product.get("base_price", 0)
                discount = product.get("coin_discount_pct", 0)
                coins_req = product.get("coins_required", 0)
                savings = base_price * (discount / 100)
                final_price = base_price - savings
                self.log_result(
                    "Get Product Details",
                    True,
                    f"Product: {product.get('name')} | Regular: ${base_price:.2f} | With {coins_req} coins: {discount}% off = ${savings:.2f} savings | Final price: ${final_price:.2f}",
                    product,
                )
            else:
                self.log_result(
                    "Get Product Details",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Product Details", False, str(e))

    def test_purchase_with_coin_boost(self):
        """Purchase product with coin boost - spend coins for extra discount.

        FEATURE: User can spend withdrawable or ecosystem coins in Z-Kart
        to get 5-10% extra discount on products.

        Example:
          Product: Starbucks Gift Card $50
          Coin Boost: 10% extra discount
          Coins Cost: 250 coins (either withdrawable or ecosystem)
          Savings: $5 ($50 × 10%)
          Final Price: $45
          User gives: 250 coins
          User saves: $5 in cash
        """
        try:
            # Get first product
            resp = requests.get(f"{BASE_URL}/zkart/products")
            if resp.status_code != 200 or not resp.json():
                self.log_result(
                    "Purchase with Coin Boost",
                    False,
                    "Could not fetch products",
                )
                return

            product = resp.json()[0]
            product_id = product.get("id")
            product_name = product.get("name")
            base_price = product.get("base_price")
            coins_required = product.get("coins_required")
            coin_discount_pct = product.get("coin_discount_pct", 5)

            # Calculate savings in dollars
            discount_dollars = base_price * (coin_discount_pct / 100)
            final_price = base_price - discount_dollars

            # Try purchase
            payload = {
                "user_id": self.user_id,
                "product_id": product_id,
                "coins_to_spend": coins_required,
            }
            resp = requests.post(f"{BASE_URL}/zkart/purchase", json=payload)

            if resp.status_code == 200:
                data = resp.json()
                self.state["products_purchased"].append({
                    "product_id": product_id,
                    "product_name": data.get("product_name"),
                    "coins_spent": data.get("coins_spent"),
                })
                self.log_result(
                    "Purchase with Coin Boost",
                    True,
                    f"Purchased: {product_name} | Original: ${base_price:.2f} | Coins cost: {coins_required} | Extra discount: {coin_discount_pct}% = ${discount_dollars:.2f} savings | Final price: ${final_price:.2f} | New coin balance: {data.get('new_balance')} coins",
                    data,
                )
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "")
                if "Insufficient coins" in detail:
                    self.log_result(
                        "Purchase with Coin Boost",
                        False,
                        f"Insufficient coins: {detail}. Need {coins_required} coins to get {coin_discount_pct}% discount (save ${discount_dollars:.2f})",
                        resp.json(),
                    )
                else:
                    self.log_result(
                        "Purchase with Coin Boost",
                        False,
                        f"Validation error: {detail}",
                        resp.json(),
                    )
            else:
                self.log_result(
                    "Purchase with Coin Boost",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Purchase with Coin Boost", False, str(e))

    # ===== PHASE 5: Spending Sinks (Ecosystem Engagement) =====

    def test_list_flash_deals(self):
        """Discover flash deals - spend coins for premium items.

        FLASH DEALS: Time-limited electronics, food, and travel items
        - Original price: $100-$2500
        - Discounts: 25-60% off
        - Coin cost: 150-1500 coins
        - Expiration: 15+ minutes

        Can spend: Any coins (withdrawable or ecosystem)
        """
        try:
            resp = requests.get(f"{BASE_URL}/spending/flash-deals?limit=10")
            if resp.status_code == 200:
                items = resp.json()
                if items:
                    sample = items[0]
                    self.log_result(
                        "List Flash Deals",
                        True,
                        f"Found {len(items)} flash deals. Sample: {sample.get('title')} - Original: ${sample.get('original_price')}, Discount: {sample.get('discount_pct')}%, Final: ${sample.get('final_price')}, Costs: {sample.get('coin_cost')} coins",
                        {
                            "total": len(items),
                            "sample": sample,
                        },
                    )
                else:
                    self.log_result("List Flash Deals", False, "No flash deals available")
            else:
                self.log_result(
                    "List Flash Deals",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("List Flash Deals", False, str(e))

    def test_list_club_deals(self):
        """Discover club deals - group purchasing to unlock benefits.

        CLUB DEALS: Group-based purchasing (need minimum members)
        - Rent Rewards Club: 250 coins/member (housing)
        - Gold Savers Club: 300 coins/member (savings)
        - Credit Builders Circle: 200 coins/member (credit)
        - Travel Deal Squad: 350 coins/member (travel)

        How it works:
        1. User joins club with coins
        2. Pool grows as more members join
        3. Higher pool = better deals unlocked
        4. All members get benefit when pool hits target

        Can spend: Any coins (withdrawable or ecosystem)
        """
        try:
            resp = requests.get(f"{BASE_URL}/spending/club-deals?limit=10")
            if resp.status_code == 200:
                items = resp.json()
                if items:
                    sample = items[0]
                    self.log_result(
                        "List Club Deals",
                        True,
                        f"Found {len(items)} club deals. Sample: {sample.get('title')} - Members: {sample.get('members')}, Pool: {sample.get('club_pool')} coins, Your cost: {sample.get('coin_cost')} coins",
                        {
                            "total": len(items),
                            "sample": sample,
                        },
                    )
                else:
                    self.log_result("List Club Deals", False, "No club deals available")
            else:
                self.log_result(
                    "List Club Deals",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("List Club Deals", False, str(e))

    def test_list_auctions(self):
        """Discover auctions."""
        try:
            resp = requests.get(f"{BASE_URL}/spending/auctions?limit=10")
            if resp.status_code == 200:
                items = resp.json()
                if items:
                    self.log_result(
                        "List Auctions",
                        True,
                        f"Found {len(items)} auctions",
                        {
                            "total": len(items),
                            "sample": items[0] if items else None,
                        },
                    )
                else:
                    self.log_result("List Auctions", False, "No auctions available")
            else:
                self.log_result(
                    "List Auctions",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("List Auctions", False, str(e))

    def test_redeem_flash_deal(self):
        """Spend coins on a flash deal."""
        try:
            # Get flash deals
            resp = requests.get(f"{BASE_URL}/spending/flash-deals")
            if resp.status_code != 200 or not resp.json():
                self.log_result(
                    "Redeem Flash Deal",
                    False,
                    "Could not fetch flash deals",
                )
                return

            item = resp.json()[0]
            item_id = item.get("id")
            coin_cost = item.get("coin_cost")

            # Try redeem
            payload = {
                "user_id": self.user_id,
                "item_id": item_id,
            }
            resp = requests.post(f"{BASE_URL}/spending/flash-deals/redeem", json=payload)

            if resp.status_code == 200:
                data = resp.json()
                self.log_result(
                    "Redeem Flash Deal",
                    True,
                    f"Redeemed: {data.get('item_title')}, Coins spent: {data.get('coins_spent')}, New balance: {data.get('new_balance')}",
                    data,
                )
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "")
                if "Insufficient coins" in detail:
                    self.log_result(
                        "Redeem Flash Deal",
                        False,
                        f"Insufficient coins: {detail}",
                        resp.json(),
                    )
                else:
                    self.log_result(
                        "Redeem Flash Deal",
                        False,
                        f"Validation error: {detail}",
                        resp.json(),
                    )
            else:
                self.log_result(
                    "Redeem Flash Deal",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Redeem Flash Deal", False, str(e))

    def test_join_club_deal(self):
        """Join a club deal (group purchase)."""
        try:
            resp = requests.get(f"{BASE_URL}/spending/club-deals")
            if resp.status_code != 200 or not resp.json():
                self.log_result(
                    "Join Club Deal",
                    False,
                    "Could not fetch club deals",
                )
                return

            item = resp.json()[0]
            item_id = item.get("id")

            payload = {
                "user_id": self.user_id,
                "item_id": item_id,
            }
            resp = requests.post(f"{BASE_URL}/spending/club-deals/redeem", json=payload)

            if resp.status_code == 200:
                data = resp.json()
                self.log_result(
                    "Join Club Deal",
                    True,
                    f"Joined: {data.get('item_title')}, Coins contributed: {data.get('coins_spent')}, New balance: {data.get('new_balance')}",
                    data,
                )
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "")
                if "Insufficient coins" in detail:
                    self.log_result(
                        "Join Club Deal",
                        False,
                        f"Insufficient coins: {detail}",
                        resp.json(),
                    )
                else:
                    self.log_result(
                        "Join Club Deal",
                        False,
                        f"Validation error: {detail}",
                        resp.json(),
                    )
            else:
                self.log_result(
                    "Join Club Deal",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Join Club Deal", False, str(e))

    # ===== PHASE 6: Summary & Reporting =====

    def test_get_tier_progress(self):
        """Check progress toward next tier."""
        try:
            resp = requests.get(f"{BASE_URL}/tier-progress/{self.user_id}")
            if resp.status_code == 200:
                data = resp.json()
                self.log_result(
                    "Get Tier Progress",
                    True,
                    f"Current tier: {data.get('current_tier')}, Progress to next: {data.get('progress_to_next_tier')}%",
                    data,
                )
            else:
                self.log_result(
                    "Get Tier Progress",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Tier Progress", False, str(e))

    def test_get_verified_behaviors(self):
        """Get all verified behaviors for user."""
        try:
            resp = requests.get(f"{BASE_URL}/verified-behaviors/{self.user_id}")
            if resp.status_code == 200:
                data = resp.json()
                behaviors = data.get("verified_behaviors", [])
                self.log_result(
                    "Get Verified Behaviors",
                    True,
                    f"User has {data.get('total_count')} verified behaviors",
                    {
                        "total_count": data.get("total_count"),
                        "sample": behaviors[0] if behaviors else None,
                    },
                )
            else:
                self.log_result(
                    "Get Verified Behaviors",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Get Verified Behaviors", False, str(e))

    def test_final_balance_check(self):
        """Final balance check - verify coin economy.

        COIN USAGE SUMMARY:
        - Withdrawable coins spent in Z-Kart: Get 5-10% extra discount
        - Withdrawable coins redeemed: Convert to cash via bank transfer
        - Ecosystem coins spent in sinks: Flash deals, clubs, auctions
        - Total coins: Determines tier progression

        Example journey:
        1. Bank verifies $50 credit improvement → 400 withdrawable coins
        2. Daily check-in → 50 ecosystem coins
        3. Total: 450 coins (400 withdrawable + 50 ecosystem)
        4. User spends 200 withdrawable in Z-Kart (saves $5 on $50 item)
        5. Remaining: 250 withdrawable (can cash out ~$250) + 50 ecosystem
        """
        try:
            resp = requests.get(f"{BASE_URL}/coins/balance/{self.user_id}")
            if resp.status_code == 200:
                data = resp.json()
                balance_change = data.get("balance", 0) - self.state["initial_balance"]
                withdrawable = data.get("withdrawable_balance", 0)
                ecosystem = data.get("ecosystem_balance", 0)
                total = data.get("balance", 0)
                self.log_result(
                    "Final Balance Check",
                    True,
                    f"Final: {total} total coins (change: {balance_change:+d}) | Withdrawable: {withdrawable} coins (can redeem to cash) | Ecosystem: {ecosystem} coins (spend in sinks) | Tier: {data.get('tier')}",
                    data,
                )
            else:
                self.log_result(
                    "Final Balance Check",
                    False,
                    f"Failed with status {resp.status_code}",
                    resp.json(),
                )
        except Exception as e:
            self.log_result("Final Balance Check", False, str(e))

    # ===== Test Execution =====

    def run_all_tests(self):
        """Execute all tests in sequence."""
        print("\n" + "=" * 80)
        print("ZOLVE BACKEND: COMPREHENSIVE USER JOURNEY TEST SUITE")
        print("=" * 80)
        print(f"Start time: {datetime.now().isoformat()}")
        print(f"Testing user ID: {self.user_id}")
        print("=" * 80)

        # Phase 1: Setup & Discovery
        print("\n[PHASE 1] Setup & Discovery")
        print("-" * 80)
        self.test_health_check()
        time.sleep(0.5)
        self.test_get_user_dashboard()
        time.sleep(0.5)
        self.test_list_zmart_products()
        time.sleep(0.5)
        self.test_get_categories()

        # Phase 2: Bank Linking & Verification
        print("\n[PHASE 2] Bank Linking & Verification")
        print("-" * 80)
        self.test_link_bank_account()
        time.sleep(0.5)
        self.test_get_bank_transactions()
        time.sleep(0.5)
        self.test_verify_behaviors()
        time.sleep(0.5)
        self.test_get_credit_score()

        # Phase 3: Coin Earning & Management
        print("\n[PHASE 3] Coin Earning & Management")
        print("-" * 80)
        self.test_earn_coins_action()
        time.sleep(0.5)
        self.test_get_balance()
        time.sleep(0.5)
        self.test_get_coin_history()

        # Phase 4: Z-Kart Purchase (with coin boost)
        print("\n[PHASE 4] Z-Kart Purchase (with Coin Boost)")
        print("-" * 80)
        self.test_list_products_by_category()
        time.sleep(0.5)
        self.test_get_product_details()
        time.sleep(0.5)
        self.test_purchase_with_coin_boost()

        # Phase 5: Spending Sinks (Ecosystem Engagement)
        print("\n[PHASE 5] Spending Sinks (Ecosystem Engagement)")
        print("-" * 80)
        self.test_list_flash_deals()
        time.sleep(0.5)
        self.test_list_club_deals()
        time.sleep(0.5)
        self.test_list_auctions()
        time.sleep(0.5)
        self.test_redeem_flash_deal()
        time.sleep(0.5)
        self.test_join_club_deal()

        # Phase 6: Summary & Reporting
        print("\n[PHASE 6] Summary & Reporting")
        print("-" * 80)
        self.test_get_tier_progress()
        time.sleep(0.5)
        self.test_get_verified_behaviors()
        time.sleep(0.5)
        self.test_final_balance_check()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary and results."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\nTotal tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\n[FAILED TESTS]")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")

        print("\n[JOURNEY SUMMARY]")
        print(f"Products purchased: {len(self.state['products_purchased'])}")
        if self.state["products_purchased"]:
            for purchase in self.state["products_purchased"]:
                print(f"  - {purchase['product_name']}: {purchase['coins_spent']} coins")

        print(f"Verified behaviors: {len(self.state['verified_behaviors'])}")
        if self.state["verified_behaviors"]:
            total_coins = sum(b.get("coins_awarded", 0) for b in self.state["verified_behaviors"])
            print(f"  Total coins from behaviors: {total_coins}")

        print(f"\nEnd time: {datetime.now().isoformat()}")
        print("=" * 80)


def main():
    """Run the test suite."""
    suite = TestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()
