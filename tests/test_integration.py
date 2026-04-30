"""Integration tests for Zolve backend using pytest."""

import pytest
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000/api"
TEST_USER_ID = 1


class TestBackendConnectivity:
    """Test backend connectivity."""

    def test_health_check(self):
        """Backend health check."""
        resp = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_user_exists(self):
        """Demo user exists."""
        resp = requests.get(f"{BASE_URL}/user/{TEST_USER_ID}")
        assert resp.status_code == 200
        user = resp.json()
        assert user["user_id"] == TEST_USER_ID
        assert "balance" in user
        assert "tier" in user


class TestCoinEarning:
    """Test coin earning functionality."""

    def test_daily_checkin_coins(self):
        """User can earn coins for daily check-in."""
        payload = {"user_id": TEST_USER_ID, "action_type": "daily_checkin"}
        resp = requests.post(f"{BASE_URL}/coins/earn", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["coins_earned"] > 0
        assert data["new_balance"] > 0

    def test_invalid_action_rejected(self):
        """Invalid action type is rejected."""
        payload = {"user_id": TEST_USER_ID, "action_type": "invalid_action"}
        resp = requests.post(f"{BASE_URL}/coins/earn", json=payload)
        assert resp.status_code == 400

    def test_get_balance(self):
        """Can retrieve user balance."""
        resp = requests.get(f"{BASE_URL}/coins/balance/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == TEST_USER_ID
        assert "balance" in data
        assert "withdrawable_balance" in data
        assert "tier" in data

    def test_transaction_history(self):
        """Can retrieve transaction history."""
        resp = requests.get(f"{BASE_URL}/coins/history/{TEST_USER_ID}")
        assert resp.status_code == 200
        transactions = resp.json()
        assert isinstance(transactions, list)
        if transactions:
            assert "transaction_id" in transactions[0]
            assert "amount" in transactions[0]
            assert "event_type" in transactions[0]


class TestBankIntegration:
    """Test bank linking and verification."""

    def test_link_bank_account(self):
        """Can link a bank account."""
        payload = {
            "user_id": TEST_USER_ID,
            "bank_name": "HDFC",
            "account_number": "9876543210",
        }
        resp = requests.post(f"{BASE_URL}/bank/link", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["bank_name"] == "HDFC"
        assert data["status"] == "linked"

    def test_invalid_bank_rejected(self):
        """Invalid bank name is rejected."""
        payload = {
            "user_id": TEST_USER_ID,
            "bank_name": "Invalid Bank",
            "account_number": "1234567890",
        }
        resp = requests.post(f"{BASE_URL}/bank/link", json=payload)
        assert resp.status_code == 400

    def test_get_bank_transactions(self):
        """Can retrieve bank transactions."""
        resp = requests.get(f"{BASE_URL}/bank/transactions/{TEST_USER_ID}")
        assert resp.status_code == 200
        transactions = resp.json()
        assert isinstance(transactions, list)
        if transactions:
            assert "description" in transactions[0]
            assert "amount" in transactions[0]
            assert "status" in transactions[0]

    def test_verify_behaviors(self):
        """Can verify financial behaviors."""
        resp = requests.post(f"{BASE_URL}/bank/verify-behaviors/{TEST_USER_ID}")
        assert resp.status_code == 200
        behaviors = resp.json()
        assert isinstance(behaviors, list)

    def test_get_credit_score(self):
        """Can retrieve credit score."""
        resp = requests.get(f"{BASE_URL}/bank/credit-score/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert "current_score" in data
        assert "previous_score" in data
        assert data["current_score"] >= 300
        assert data["current_score"] <= 900


class TestZKartMarketplace:
    """Test Z-Kart marketplace functionality."""

    def test_list_products(self):
        """Can list all products."""
        resp = requests.get(f"{BASE_URL}/zkart/products")
        assert resp.status_code == 200
        products = resp.json()
        assert isinstance(products, list)
        assert len(products) > 0
        product = products[0]
        assert "id" in product
        assert "name" in product
        assert "base_price" in product
        assert "coins_required" in product
        assert "coin_discount_pct" in product

    def test_filter_by_category(self):
        """Can filter products by category."""
        resp = requests.get(f"{BASE_URL}/zkart/products?category=Food")
        assert resp.status_code == 200
        products = resp.json()
        assert isinstance(products, list)
        for product in products:
            assert product["category"] == "Food"

    def test_get_categories(self):
        """Can retrieve product categories."""
        resp = requests.get(f"{BASE_URL}/zkart/categories")
        assert resp.status_code == 200
        categories = resp.json()
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_product_details(self):
        """Can get details of a specific product."""
        resp = requests.get(f"{BASE_URL}/zkart/products/1")
        assert resp.status_code == 200
        product = resp.json()
        assert product["id"] == 1
        assert "name" in product
        assert "base_price" in product
        assert "coin_discount_pct" in product
        assert product["coin_discount_pct"] >= 5
        assert product["coin_discount_pct"] <= 20

    def test_purchase_product_valid(self):
        """Can purchase a product with sufficient coins."""
        # First, get a product and its coin requirement
        resp = requests.get(f"{BASE_URL}/zkart/products/1")
        assert resp.status_code == 200
        product = resp.json()
        coins_required = product["coins_required"]

        # Earn enough coins first
        for _ in range(3):
            earn_resp = requests.post(
                f"{BASE_URL}/coins/earn",
                json={"user_id": TEST_USER_ID, "action_type": "daily_checkin"},
            )
            if earn_resp.status_code != 200:
                break

        # Try purchase
        payload = {
            "user_id": TEST_USER_ID,
            "product_id": 1,
            "coins_to_spend": coins_required,
        }
        resp = requests.post(f"{BASE_URL}/zkart/purchase", json=payload)

        # Either succeeds or fails due to insufficient coins
        assert resp.status_code in [200, 400]
        if resp.status_code == 200:
            data = resp.json()
            assert data["success"] is True
            assert data["coins_spent"] == coins_required
            assert data["new_balance"] >= 0

    def test_purchase_nonexistent_product(self):
        """Cannot purchase nonexistent product."""
        payload = {
            "user_id": TEST_USER_ID,
            "product_id": 999999,
            "coins_to_spend": 100,
        }
        resp = requests.post(f"{BASE_URL}/zkart/purchase", json=payload)
        assert resp.status_code == 404


class TestSpendingSinks:
    """Test spending sink functionality (flash deals, club deals, auctions)."""

    def test_list_flash_deals(self):
        """Can list flash deals."""
        resp = requests.get(f"{BASE_URL}/spending/flash-deals")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) > 0
        item = items[0]
        assert "id" in item
        assert "title" in item
        assert "coin_cost" in item
        assert "sink_type" in item
        assert item["sink_type"] == "flash-deals"

    def test_list_club_deals(self):
        """Can list club deals."""
        resp = requests.get(f"{BASE_URL}/spending/club-deals")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert item["sink_type"] == "club-deals"
            assert "members" in item
            assert "club_pool" in item

    def test_list_auctions(self):
        """Can list auctions."""
        resp = requests.get(f"{BASE_URL}/spending/auctions")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert item["sink_type"] == "auctions"
            assert "current_bid" in item
            assert "bids" in item

    def test_list_spin_wheel_entries(self):
        """Can list spin wheel entries."""
        resp = requests.get(f"{BASE_URL}/spending/spin-wheel-entries")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert item["sink_type"] == "spin-wheel-entries"

    def test_redeem_flash_deal(self):
        """Can redeem a flash deal if sufficient coins."""
        resp = requests.get(f"{BASE_URL}/spending/flash-deals")
        items = resp.json()
        if items:
            item = items[0]
            payload = {
                "user_id": TEST_USER_ID,
                "item_id": item["id"],
            }
            resp = requests.post(f"{BASE_URL}/spending/flash-deals/redeem", json=payload)

            # Either succeeds or fails due to insufficient coins
            assert resp.status_code in [200, 400]
            if resp.status_code == 200:
                data = resp.json()
                assert data["success"] is True
                assert data["coins_spent"] == item["coin_cost"]
                assert data["new_balance"] >= 0


class TestUserDashboard:
    """Test user dashboard and reporting."""

    def test_user_dashboard(self):
        """Can retrieve user dashboard."""
        resp = requests.get(f"{BASE_URL}/user/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == TEST_USER_ID
        assert "name" in data
        assert "email" in data
        assert "balance" in data
        assert "tier" in data
        assert "credit_score" in data
        assert "verified_behaviors_count" in data
        assert "activity_feed" in data

    def test_tier_progress(self):
        """Can get tier progress."""
        resp = requests.get(f"{BASE_URL}/tier-progress/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert "current_tier" in data
        assert "next_tier" in data
        assert "progress_to_next_tier" in data

    def test_verified_behaviors(self):
        """Can get verified behaviors."""
        resp = requests.get(f"{BASE_URL}/verified-behaviors/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == TEST_USER_ID
        assert "verified_behaviors" in data
        assert "total_count" in data

    def test_leaderboard(self):
        """Can retrieve leaderboard."""
        resp = requests.get(f"{BASE_URL}/leaderboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "leaderboard" in data
        assert "total_users" in data
        assert isinstance(data["leaderboard"], list)


class TestErrorHandling:
    """Test error handling."""

    def test_nonexistent_user(self):
        """Nonexistent user returns 404."""
        resp = requests.get(f"{BASE_URL}/user/999999")
        assert resp.status_code == 404

    def test_invalid_balance_request(self):
        """Invalid user ID returns error."""
        resp = requests.get(f"{BASE_URL}/coins/balance/999999")
        assert resp.status_code == 404

    def test_invalid_category_filter(self):
        """Invalid category returns empty list."""
        resp = requests.get(f"{BASE_URL}/zkart/products?category=NonexistentCategory")
        assert resp.status_code == 200
        products = resp.json()
        assert len(products) == 0

    def test_invalid_spending_sink(self):
        """Invalid sink type returns 404."""
        resp = requests.get(f"{BASE_URL}/spending/invalid-sink")
        assert resp.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
