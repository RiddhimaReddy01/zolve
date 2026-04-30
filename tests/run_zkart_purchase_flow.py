#!/usr/bin/env python3
"""Focused Z-Kart purchase flow checks.

This script uses FastAPI TestClient with an isolated SQLite database under
tests/ so it can verify purchase behavior without touching a developer DB.
"""

import os
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DB_PATH = ROOT / "tests" / ".tmp_zkart_purchase_flow.db"

if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["ZOLVE_DATABASE_PATH"] = str(DB_PATH)
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402


client = TestClient(app)
USER_ID = 1


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def get(path: str, expected_status: int = 200) -> dict | list:
    response = client.get(path)
    expect(response.status_code == expected_status, f"GET {path} returned {expected_status}")
    return response.json()


def post(path: str, payload: dict, expected_status: int = 200) -> dict:
    response = client.post(path, json=payload)
    expect(response.status_code == expected_status, f"POST {path} returned {expected_status}")
    return response.json()


def set_user_balance(balance: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET coin_balance = ? WHERE id = ?", (balance, USER_ID))


def set_product_stock(product_id: int, stock: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))


def fetch_one(query: str, params: tuple = ()) -> sqlite3.Row:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(query, params).fetchone()
        if row is None:
            raise AssertionError(f"No row returned for query: {query}")
        return row


def expected_final_price(product: dict) -> float:
    return round(product["base_price"] * (1 - product["coin_discount_pct"] / 100), 2)


def main() -> int:
    print("\n=== Z-Kart Purchase Flow ===\n")

    health = get("/health")
    expect(health["status"] == "ok", "backend health is ok")

    products = get("/api/zkart/products")
    expect(len(products) >= 100, "user can browse a realistic Z-Kart catalog")

    product = next(item for item in products if item["stock"] > 0)
    expected_fields = {
        "base_price",
        "coin_discount",
        "coin_discount_pct",
        "coins_required",
        "stock",
        "final_price",
        "discounted_price",
    }
    expect(expected_fields.issubset(product.keys()), "browse response includes pricing, discount, coins, and stock")
    expect(product["final_price"] == expected_final_price(product), "browse response calculates discounted price")

    detail = get(f"/api/zkart/products/{product['id']}")
    expect(detail["id"] == product["id"], "user can view product details")
    expect(expected_fields.issubset(detail.keys()), "detail response includes full purchase pricing fields")
    expect(detail["final_price"] == expected_final_price(detail), "detail response calculates final price")

    wrong_spend = detail["coins_required"] + 1
    set_user_balance(wrong_spend)
    bad_spend = post(
        "/api/zkart/purchase",
        {"user_id": USER_ID, "product_id": detail["id"], "coins_to_spend": wrong_spend},
        expected_status=400,
    )
    expect("exactly" in bad_spend["error"], "purchase rejects non-exact coin spend")

    set_user_balance(detail["coins_required"] - 1)
    insufficient = post(
        "/api/zkart/purchase",
        {"user_id": USER_ID, "product_id": detail["id"], "coins_to_spend": detail["coins_required"]},
        expected_status=400,
    )
    expect("Insufficient coins" in insufficient["error"], "purchase validates user coin balance")

    out_of_stock_product = next(item for item in products if item["id"] != detail["id"])
    set_product_stock(out_of_stock_product["id"], 0)
    set_user_balance(out_of_stock_product["coins_required"])
    out_of_stock = post(
        "/api/zkart/purchase",
        {
            "user_id": USER_ID,
            "product_id": out_of_stock_product["id"],
            "coins_to_spend": out_of_stock_product["coins_required"],
        },
        expected_status=400,
    )
    expect("out of stock" in out_of_stock["error"], "purchase validates product stock")

    starting_balance = detail["coins_required"] + 125
    starting_stock = detail["stock"]
    set_user_balance(starting_balance)
    purchase = post(
        "/api/zkart/purchase",
        {"user_id": USER_ID, "product_id": detail["id"], "coins_to_spend": detail["coins_required"]},
    )

    final_price = expected_final_price(detail)
    expect(purchase["success"] is True, "purchase succeeds with exact spend, balance, and stock")
    expect(purchase["purchase_id"] > 0, "purchase response includes purchase_id")
    expect(purchase["product_name"] == detail["name"], "purchase response includes product name")
    expect(purchase["coins_spent"] == detail["coins_required"], "purchase response includes coins spent")
    expect(purchase["price_paid"] == final_price, "purchase response includes discounted price_paid")
    expect(purchase["final_price"] == final_price, "purchase response includes final_price")
    expect(purchase["new_balance"] == starting_balance - detail["coins_required"], "purchase returns new balance")
    expect("Successfully purchased" in purchase["message"], "purchase returns a clear success message")

    updated_user = fetch_one("SELECT coin_balance FROM users WHERE id = ?", (USER_ID,))
    expect(updated_user["coin_balance"] == purchase["new_balance"], "database deducts user coins")

    updated_product = fetch_one("SELECT stock FROM products WHERE id = ?", (detail["id"],))
    expect(updated_product["stock"] == starting_stock - 1, "database decrements product stock")

    purchase_row = fetch_one("SELECT * FROM purchases WHERE id = ?", (purchase["purchase_id"],))
    expect(purchase_row["coins_spent"] == detail["coins_required"], "database records purchase coins")
    expect(purchase_row["price_paid"] == final_price, "database records discounted price paid")

    transaction = fetch_one(
        """
        SELECT * FROM coin_transactions
        WHERE user_id = ? AND event_type = 'purchase'
        ORDER BY id DESC
        LIMIT 1
        """,
        (USER_ID,),
    )
    expect(transaction["amount"] == -detail["coins_required"], "coin ledger records purchase spend")
    expect(detail["name"] in transaction["description"], "coin ledger description names the product")

    print("\nAll Z-Kart purchase flow checks passed.\n")
    return 0


if __name__ == "__main__":
    exit_code = main()
    client.close()
    try:
        DB_PATH.unlink()
    except PermissionError:
        pass
    raise SystemExit(exit_code)
