"""Tests for tier progression system."""

import pytest
import requests


BASE_URL = "http://localhost:8000/api"
TEST_USER_ID = 1


class TestTierProgression:
    """Tests for tier progression and benefits."""

    def test_tier_progress_endpoint(self):
        """Test GET /api/tier-progress/{user_id} returns tier data."""
        resp = requests.get(f"{BASE_URL}/tier-progress/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert "current_tier" in data
        assert "next_tier" in data
        assert "coins_needed" in data
        assert "behaviors_needed" in data
        assert "progress_pct" in data

    def test_tier_benefits_in_response(self):
        """Test that tier progress includes benefits."""
        resp = requests.get(f"{BASE_URL}/tier-progress/{TEST_USER_ID}")
        if resp.status_code == 200:
            data = resp.json()
            assert "benefits" in data
            benefits = data["benefits"]
            assert "spin_boost" in benefits
            assert "scratch_card_bonus" in benefits
            assert "ad_cap_multiplier" in benefits

    def test_tier_history_endpoint(self):
        """Test GET /api/tier-history/{user_id} returns history."""
        resp = requests.get(f"{BASE_URL}/tier-history/{TEST_USER_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data
        assert "current_tier" in data
        assert "tier_history" in data
        assert isinstance(data["tier_history"], list)

    def test_tier_history_structure(self):
        """Test tier history events have correct structure."""
        resp = requests.get(f"{BASE_URL}/tier-history/{TEST_USER_ID}")
        if resp.status_code == 200:
            data = resp.json()
            if data["tier_history"]:
                event = data["tier_history"][0]
                assert "old_tier" in event
                assert "new_tier" in event
                assert "coins_at_change" in event
                assert "behaviors_at_change" in event
                assert "changed_at" in event

    def test_basic_tier_defaults(self):
        """Test Basic tier has default benefits."""
        resp = requests.get(f"{BASE_URL}/tier-progress/{TEST_USER_ID}")
        if resp.status_code == 200:
            data = resp.json()
            if data["current_tier"] == "Basic":
                benefits = data["benefits"]
                assert benefits["spin_boost"] == 0
                assert benefits["scratch_card_bonus"] is False
                assert benefits["ad_cap_multiplier"] == 1
