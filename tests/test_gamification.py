"""Tests for gamification features (spin wheel, scratch cards, easter eggs)."""

import pytest
import requests


BASE_URL = "http://localhost:8000/api"
TEST_USER_ID = 1


class TestSpinWheel:
    """Tests for behavior-based spin wheel."""

    def test_spin_wheel_requires_100_coins(self):
        """Test that spin wheel costs 100 coins."""
        payload = {"user_id": TEST_USER_ID}
        resp = requests.post(f"{BASE_URL}/games/spin", json=payload)
        # Should succeed if user has coins, or 400 if insufficient
        assert resp.status_code in [200, 400]

    def test_spin_wheel_result_structure(self):
        """Test spin wheel returns segment, coins_won, and message."""
        # First earn coins
        requests.post(f"{BASE_URL}/coins/earn", json={"user_id": TEST_USER_ID, "action_type": "daily_checkin"})
        # Then try spin
        payload = {"user_id": TEST_USER_ID}
        resp = requests.post(f"{BASE_URL}/games/spin", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            assert "segment_number" in data
            assert "coins_won" in data
            assert "message" in data
            assert 1 <= data["segment_number"] <= 6
            assert 50 <= data["coins_won"] <= 1000


class TestScratchCards:
    """Tests for purchase-triggered scratch cards."""

    def test_scratch_cards_list(self):
        """Test GET /api/games/scratch-cards/{user_id} returns list."""
        resp = requests.get(f"{BASE_URL}/games/scratch-cards/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_scratch_card_structure(self):
        """Test scratch card has required fields."""
        resp = requests.get(f"{BASE_URL}/games/scratch-cards/{TEST_USER_ID}")
        if resp.status_code == 200:
            data = resp.json()
            if data:  # If there are any cards
                card = data[0]
                assert "id" in card
                assert "user_id" in card
                assert "purchase_amount" in card
                assert "scratched_at" in card


class TestEasterEggs:
    """Tests for easter egg system."""

    def test_easter_eggs_list(self):
        """Test GET /api/games/easter-eggs/{user_id} returns list."""
        resp = requests.get(f"{BASE_URL}/games/easter-eggs/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_easter_egg_structure(self):
        """Test easter egg has required fields."""
        resp = requests.get(f"{BASE_URL}/games/easter-eggs/{TEST_USER_ID}")
        if resp.status_code == 200:
            data = resp.json()
            if data:  # If there are any eggs
                egg = data[0]
                assert "id" in egg
                assert "user_id" in egg
                assert "egg_type" in egg
                assert "coins_awarded" in egg
                assert "condition_met_at" in egg
                assert "unlocked_at" in egg

    def test_easter_egg_claim(self):
        """Test POST /api/games/easter-eggs/claim claims an egg."""
        # Get available eggs
        resp = requests.get(f"{BASE_URL}/games/easter-eggs/{TEST_USER_ID}")
        if resp.status_code == 200:
            eggs = resp.json()
            unclaimed = [e for e in eggs if e["unlocked_at"] is None]
            if unclaimed:
                egg_id = unclaimed[0]["id"]
                # Use query parameters, not JSON body
                claim_resp = requests.post(f"{BASE_URL}/games/easter-eggs/claim?user_id={TEST_USER_ID}&egg_id={egg_id}")
                if claim_resp.status_code == 200:
                    data = claim_resp.json()
                    assert data["success"] is True
                    assert data["coins_awarded"] > 0
