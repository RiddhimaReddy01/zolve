#!/usr/bin/env python3
"""Club formation and social loop test.

This script mounts the clubs router in isolation with FastAPI TestClient:
- create a club
- join via invite
- view members, shared progress, quests, leaderboard, and feed
- record social triggers that increase club progress
- complete collective quests and trigger tier upgrades
"""

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

os.environ["ZOLVE_DATABASE_PATH"] = str(ROOT / "zolve_clubs_isolated_test.db")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from routes.clubs import reset_demo_state, router  # noqa: E402


app = FastAPI(title="Club Formation Test App")
app.include_router(router)
client = TestClient(app)


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def post(path: str, payload: dict, expected_status: int = 200):
    response = client.post(path, json=payload)
    expect(
        response.status_code == expected_status,
        f"POST {path} returned {expected_status}",
    )
    return response.json()


def get(path: str, expected_status: int = 200):
    response = client.get(path)
    expect(
        response.status_code == expected_status,
        f"GET {path} returned {expected_status}",
    )
    return response.json()


def main() -> int:
    reset_demo_state()
    print("\n=== Club Formation + Social Loop Flow ===\n")

    created = post(
        "/api/clubs",
        {
            "user_id": 1,
            "club_name": "Rent Ready Circle",
            "goal_name": "Pay bills on time together",
        },
    )
    expect(created["success"] is True, "club creates successfully")
    expect(created["club_id"] == 1, "first club gets deterministic id")
    invite_code = created["invite_code"]
    expect(invite_code == "RENTRE-001", "invite code is deterministic")

    first_dashboard = created["dashboard"]
    expect(first_dashboard["tier"] == "Bronze", "new club starts at Bronze")
    expect(first_dashboard["shared_progress"] == 0, "shared progress starts at zero")
    expect(len(first_dashboard["members"]) == 1, "creator is first member")
    expect(first_dashboard["members"][0]["role"] == "owner", "creator is club owner")
    expect(len(first_dashboard["quests"]) == 3, "dashboard includes collective quests")

    joined = post(
        "/api/clubs/join",
        {
            "user_id": 2,
            "invite_code": invite_code,
        },
    )
    expect(joined["success"] is True, "member joins via invite")
    expect(joined["member_count"] == 2, "club has two members after invite join")
    expect(joined["dashboard"]["social_feed"][0]["event_type"] == "member_joined", "join appears in social feed")

    post(
        "/api/clubs/join",
        {
            "user_id": 2,
            "invite_code": invite_code,
        },
        expected_status=409,
    )
    post(
        "/api/clubs/join",
        {
            "user_id": 3,
            "invite_code": "NOPE-999",
        },
        expected_status=404,
    )

    bill_event = post(
        "/api/clubs/1/events",
        {
            "user_id": 1,
            "event_type": "paid_bill",
            "amount": 1250.0,
        },
    )
    expect(bill_event["event"]["progress_delta"] == 75, "paid bill event adds progress")
    expect("paid a bill -> club progress increased" in bill_event["event"]["message"], "social trigger message is clear")
    expect(
        bill_event["dashboard"]["quests"][0]["progress"] == 1,
        "paid bill advances bill-streak quest",
    )

    savings_event = post(
        "/api/clubs/1/events",
        {
            "user_id": 2,
            "event_type": "savings_deposit",
            "amount": 200.0,
        },
    )
    expect(savings_event["dashboard"]["shared_progress"] == 135, "shared progress sums social events")
    expect(
        savings_event["dashboard"]["leaderboard"][0]["user_id"] == 1,
        "leaderboard ranks highest contribution first",
    )
    expect(
        savings_event["dashboard"]["leaderboard"][1]["user_id"] == 2,
        "second member appears on leaderboard",
    )

    post(
        "/api/clubs/1/events",
        {
            "user_id": 2,
            "event_type": "unsupported_action",
        },
        expected_status=400,
    )
    post(
        "/api/clubs/1/events",
        {
            "user_id": 99,
            "event_type": "paid_bill",
        },
        expected_status=404,
    )

    post(
        "/api/clubs/1/quests/bill-streak/contribute",
        {
            "user_id": 2,
            "progress": 4,
        },
    )
    dashboard = get("/api/clubs/1/dashboard")
    bill_quest = next(quest for quest in dashboard["quests"] if quest["id"] == "bill-streak")
    expect(bill_quest["completed"] is True, "direct quest contribution completes bill-streak")
    expect(dashboard["tier"] == "Silver", "club upgrades to Silver after 200 progress")
    expect(dashboard["next_tier"]["tier"] == "Gold", "dashboard shows next tier target")
    expect(dashboard["incentives"]["tier_multiplier"] == 1.1, "Silver tier incentive multiplier is exposed")
    expect(
        "Unlock 2% fee-back pool" in dashboard["incentives"]["active_rewards"],
        "completed quest exposes collective reward",
    )
    expect(
        any(event["event_type"] == "tier_upgrade" for event in dashboard["social_feed"]),
        "tier upgrade appears in social feed",
    )
    expect(
        dashboard["leaderboard"][0]["user_id"] == 2,
        "quest contribution can move member to top of leaderboard",
    )

    post(
        "/api/clubs/999/quests/bill-streak/contribute",
        {
            "user_id": 1,
            "progress": 1,
        },
        expected_status=404,
    )

    print("\nAll club formation/social loop checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
