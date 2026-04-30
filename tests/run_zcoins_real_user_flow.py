#!/usr/bin/env python3
"""Real-user Z-Coins journey test for Riddhima.

This script exercises the backend in-process with FastAPI TestClient:
- bank linking and behavior verification
- withdrawable coins from verified financial behavior
- ecosystem coins from app engagement
- spending sinks: Z-Kart, club deals, auctions, flash deals, spin entries
"""

import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

temp_dir = tempfile.TemporaryDirectory(dir=str(ROOT))
os.environ["ZOLVE_DATABASE_PATH"] = str(Path(temp_dir.name) / "zolve_test.db")

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402


client = TestClient(app)
USER_ID = 1


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
    print("\n=== Z-Coins Real User Flow: Riddhima ===\n")

    health = get("/health")
    expect(health["status"] == "ok", "backend health is ok")

    user = get(f"/api/user/{USER_ID}")
    expect(user["name"] == "Riddhima", "demo user is Riddhima")
    expect(user["withdrawable_balance"] == 0, "withdrawable balance starts at 0")

    link = post(
        "/api/bank/link",
        {"user_id": USER_ID, "bank_name": "HDFC Bank", "account_number": "4321"},
    )
    expect(link["success"] is True, "bank account links successfully")

    transactions = get(f"/api/bank/transactions/{USER_ID}")
    expect(len(transactions) >= 100, "bank page has 100+ mock transactions")
    expect(
        any("Salary" in txn["description"] for txn in transactions),
        "bank data includes salary/direct deposit behavior",
    )

    verified = client.post(f"/api/bank/verify-behaviors/{USER_ID}")
    expect(verified.status_code == 200, "behavior verification returns 200")
    verified_items = verified.json()
    expect(len(verified_items) >= 100, "verification awards many real bank behaviors")

    balance = get(f"/api/coins/balance/{USER_ID}")
    expect(balance["withdrawable_balance"] > 0, "verified behavior creates withdrawable coins")
    expect(balance["balance"] >= balance["withdrawable_balance"], "total coins cover withdrawable coins")

    daily = post("/api/coins/earn", {"user_id": USER_ID, "action_type": "daily_checkin"})
    expect(daily["earning_type"] == "ecosystem", "daily check-in earns ecosystem coins")
    post("/api/coins/earn", {"user_id": USER_ID, "action_type": "daily_checkin"}, expected_status=429)

    post("/api/coins/earn", {"user_id": USER_ID, "action_type": "education_module"})
    for _ in range(3):
        post("/api/coins/earn", {"user_id": USER_ID, "action_type": "ad_watch"})
    post("/api/coins/earn", {"user_id": USER_ID, "action_type": "ad_watch"}, expected_status=429)

    products = get("/api/zkart/products")
    expect(len(products) >= 100, "Z-Kart has 100+ products")
    product = products[0]
    purchase = post(
        "/api/zkart/purchase",
        {
            "user_id": USER_ID,
            "product_id": product["id"],
            "coins_to_spend": product["coins_required"],
        },
    )
    expect(purchase["success"] is True, "Z-Kart purchase spends coins")

    for sink_type in ["flash-deals", "club-deals", "auctions", "spin-wheel-entries"]:
        items = get(f"/api/spending/{sink_type}")
        expect(len(items) >= 100, f"{sink_type} has 100+ mock items")
        redeem = post(
            f"/api/spending/{sink_type}/redeem",
            {"user_id": USER_ID, "item_id": items[0]["id"]},
        )
        expect(redeem["success"] is True, f"{sink_type} redemption spends coins")

    spin = post("/api/games/spin", {"user_id": USER_ID})
    expect(spin["coins_won"] in [50, 100, 200, 300, 500, 1000], "spin wheel returns valid reward")

    history = get(f"/api/coins/history/{USER_ID}?limit=200")
    event_types = {entry["event_type"] for entry in history}
    expected_events = {
        "purchase",
        "flash-deals",
        "club-deals",
        "auctions",
        "spin-wheel-entries",
        "spin_wheel",
        "daily_checkin",
        "ad_watch",
        "education_module",
    }
    expect(expected_events.issubset(event_types), "coin ledger shows earns and spending sinks")

    final_user = get(f"/api/user/{USER_ID}")
    expect(final_user["tier"] == "Gold", "Riddhima reaches Gold after verified behaviors")

    print("\nAll Z-Coins real-user checks passed.\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        temp_dir.cleanup()
