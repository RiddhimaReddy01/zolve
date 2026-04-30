"""Customer-flow tests for Z-World activation, daily engagement, and rewards."""

import os
import sys

import pytest
import requests


BASE_URL = "http://localhost:8000/api"
TEST_USER_ID = 1


@pytest.fixture(autouse=True)
def reset_z_world_state():
    """Reset Z-World tables so flow tests are deterministic."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
    from database import Database

    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "zolve.db"))
    db = Database(db_path)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for table in [
            "z_world_onboarding",
            "game_entitlements",
            "notifications",
            "financial_events",
        ]:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (TEST_USER_ID,))
        cursor.execute(
            "DELETE FROM scratch_card_triggers WHERE user_id = ? AND purchase_id = 0",
            (TEST_USER_ID,),
        )
        cursor.execute(
            "DELETE FROM coin_transactions WHERE user_id = ? AND event_type IN (?, ?)",
            (TEST_USER_ID, "z_world_signup_bonus", "on_time_payment"),
        )
        cursor.execute(
            "DELETE FROM behaviors WHERE user_id = ? AND verification_source = ?",
            (TEST_USER_ID, "event_rule_engine"),
        )
    yield


def test_first_time_user_onboarding_activation_flow():
    intro_resp = requests.get(f"{BASE_URL}/z-world/intro")
    assert intro_resp.status_code == 200
    intro = intro_resp.json()
    assert intro["value_proposition"] == "Earn rewards for financial behavior"
    assert "Join or create a Z-Club" in intro["forced_steps"]

    before = requests.get(f"{BASE_URL}/coins/balance/{TEST_USER_ID}").json()["balance"]
    payload = {
        "user_id": TEST_USER_ID,
        "club_action": "create",
        "club_name": "Credit Builders",
        "accepted_coin_rules": True,
    }
    onboard_resp = requests.post(f"{BASE_URL}/z-world/onboarding/complete", json=payload)
    assert onboard_resp.status_code == 200
    data = onboard_resp.json()

    assert data["onboarding_complete"] is True
    assert data["accepted_coin_rules"] is True
    assert data["rewards"]["signup_bonus_zcoins"] == 250
    assert data["rewards"]["first_scratch_card_unlocked"] is True
    assert data["landing"] == "z_world_dashboard"
    assert data["dashboard"]["balance"] >= before + 250
    assert data["dashboard"]["daily_loop"]["scratch_cards_available"] >= 1


def test_daily_engagement_loop_grants_spin_and_prompts_next_actions():
    requests.post(
        f"{BASE_URL}/z-world/onboarding/complete",
        json={
            "user_id": TEST_USER_ID,
            "club_action": "create",
            "club_name": "Daily Builders",
            "accepted_coin_rules": True,
        },
    )

    grant_resp = requests.post(f"{BASE_URL}/z-world/daily-engagement/{TEST_USER_ID}")
    assert grant_resp.status_code == 200
    granted = grant_resp.json()
    assert granted["spins_granted"] == 1
    assert granted["notification"]["title"] == "You earned a spin today"
    assert granted["dashboard"]["daily_loop"]["spins_available"] >= 1

    spin_resp = requests.post(f"{BASE_URL}/games/spin", json={"user_id": TEST_USER_ID})
    assert spin_resp.status_code == 200
    spin = spin_resp.json()
    assert spin["used_earned_spin"] is True
    assert spin["cost_paid"] == 0
    assert spin["coins_won"] >= 50

    dashboard = requests.get(f"{BASE_URL}/z-world/dashboard/{TEST_USER_ID}").json()
    actions = {item["action"] for item in dashboard["daily_loop"]["next_actions"]}
    closures = {item["label"] for item in dashboard["daily_loop"]["loop_closure"]}
    assert "daily_checkin" in actions
    assert "check_club_activity" in actions
    assert {"Check Z-Kart", "Check Club activity"}.issubset(closures)


def test_financial_behavior_reward_flow_unlocks_coins_spins_and_notification():
    before = requests.get(f"{BASE_URL}/coins/balance/{TEST_USER_ID}").json()["balance"]
    payload = {
        "user_id": TEST_USER_ID,
        "event_type": "payment_completed_on_time",
        "metadata": {
            "payment_id": "pay-test-001",
            "amount": 1200,
            "paid_at": "2026-04-30T01:00:00",
        },
    }

    reward_resp = requests.post(f"{BASE_URL}/z-world/financial-events", json=payload)
    assert reward_resp.status_code == 200
    reward = reward_resp.json()

    assert reward["eligible"] is True
    assert reward["coins_awarded"] == 500
    assert reward["spins_unlocked"] == 2
    assert reward["new_balance"] >= before + 500
    assert reward["notification"]["title"] == "You earned 2 spins for paying on time"
    assert reward["dashboard"]["daily_loop"]["spins_available"] >= 2

    spin_resp = requests.post(f"{BASE_URL}/games/spin", json={"user_id": TEST_USER_ID})
    assert spin_resp.status_code == 200
    assert spin_resp.json()["used_earned_spin"] is True
