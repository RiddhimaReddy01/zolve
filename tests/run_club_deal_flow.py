#!/usr/bin/env python3
"""Club deal group-purchase flow test."""

import os
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

temp_dir = ROOT / "tests" / ".tmp"
temp_dir.mkdir(exist_ok=True)
db_path = temp_dir / f"club_deal_test_{uuid.uuid4().hex}.db"
os.environ["ZOLVE_DATABASE_PATH"] = str(db_path)

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from routes import club_deals  # noqa: E402


app = FastAPI(title="Club Deal Flow Test")
app.include_router(club_deals.router)
client = TestClient(app)


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def post(path: str, payload: dict, expected_status: int = 200):
    response = client.post(path, json=payload)
    expect(response.status_code == expected_status, f"POST {path} returned {expected_status}")
    return response.json()


def get(path: str, expected_status: int = 200):
    response = client.get(path)
    expect(response.status_code == expected_status, f"GET {path} returned {expected_status}")
    return response.json()


def main() -> int:
    print("\n=== Club Deal Flow: Group Purchase ===\n")
    club_deals.reset_demo_state()

    clubs = get("/api/club-deals/clubs")
    travel_club = next(club for club in clubs if club["id"] == "travel-squad")
    starting_pool = travel_club["pool_balance"]
    expect(starting_pool == 2000, "travel club starts with deterministic shared pool")

    catalog = get("/api/club-deals/catalog")
    deal = next(item for item in catalog if item["id"] == "airport-lounge-bundle")
    expect(deal["threshold"] == 3, "selected deal requires three accepts")

    started = post(
        "/api/club-deals/start",
        {
            "user_id": 1,
            "club_id": "travel-squad",
            "deal_id": "airport-lounge-bundle",
            "invite_window_minutes": 25,
        },
    )
    purchase_id = started["purchase_id"]
    expect(started["status"] == "inviting", "starting a group purchase opens invite state")
    expect(started["invite_window"]["channel"] == "push", "response represents push-style invites")
    expect(started["invite_window"]["expires_at"] > started["invite_window"]["started_at"], "invite has expiry window")
    expect(started["responses"]["accepted_count"] == 1, "initiator is counted as accepted")
    expect(started["club"]["pool_balance"] == starting_pool, "pool is not charged before threshold")

    ignored = post(f"/api/club-deals/{purchase_id}/respond", {"member_id": 2, "action": "ignore"})
    expect(ignored["status"] == "inviting", "ignored invite does not unlock the deal")
    expect(ignored["responses"]["ignored_count"] == 1, "ignored response is tracked")
    expect(ignored["club"]["pool_balance"] == starting_pool, "pool remains unchanged after ignore")

    accepted = post(f"/api/club-deals/{purchase_id}/respond", {"member_id": 3, "action": "accept"})
    expect(accepted["status"] == "inviting", "second accept is still below threshold")
    expect(accepted["responses"]["accepted_count"] == 2, "accepted response is tracked")

    unlocked = post(f"/api/club-deals/{purchase_id}/respond", {"member_id": 4, "action": "accept"})
    expect(unlocked["status"] == "unlocked", "deal unlocks when threshold is met")
    expect(unlocked["unlock"]["unlocked"] is True, "unlock flag is true")
    expect(unlocked["unlock"]["coins_deducted"] == deal["coins_required"], "unlock records coins deducted")
    expect(
        unlocked["club"]["pool_balance"] == starting_pool - deal["coins_required"],
        "coins are deducted from shared club pool",
    )

    status = get(f"/api/club-deals/{purchase_id}")
    expect(status["status"] == "unlocked", "status endpoint returns unlocked purchase")
    expect(status["responses"]["pending_count"] == 1, "remaining invited members stay pending")

    history = club_deals.db.get_transaction_history(1, limit=10)
    expect(
        any(entry["event_type"] == "club_deal_unlock" for entry in history),
        "coin ledger records club deal unlock event",
    )

    print("\nAll club deal group-purchase checks passed.\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        if db_path.exists():
            db_path.unlink()
