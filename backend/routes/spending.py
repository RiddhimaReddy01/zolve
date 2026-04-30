"""Spending sink endpoints for Z-Coin ecosystem usage."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from database import Database
from models import SpendingActionRequest

router = APIRouter(prefix="/api/spending", tags=["spending"])
db = Database()


def _build_sink_items(sink_type: str, count: int = 120) -> List[Dict[str, Any]]:
    """Generate deterministic, realistic mock items for spending tests."""
    catalogs = {
        "flash-deals": [
            ("Premium Headphones", "Electronics", 4999, 35, 1500),
            ("Wireless Charger", "Electronics", 1999, 25, 400),
            ("Smart Watch Band", "Accessories", 599, 40, 150),
            ("Airport Lounge Pass", "Travel", 2500, 30, 900),
            ("Grocery Mega Coupon", "Food", 1200, 18, 300),
        ],
        "club-deals": [
            ("Rent Rewards Club", "Housing", 0, 0, 250),
            ("Gold Savers Club", "Savings", 0, 0, 300),
            ("Credit Builders Circle", "Credit", 0, 0, 200),
            ("Travel Deal Squad", "Travel", 0, 0, 350),
            ("Student Essentials Pool", "Education", 0, 0, 180),
        ],
        "auctions": [
            ("iPhone Upgrade Auction", "Electronics", 79999, 0, 2200),
            ("Flight Voucher Auction", "Travel", 15000, 0, 950),
            ("MacBook Accessory Kit", "Electronics", 9999, 0, 700),
            ("Weekend Staycation", "Travel", 12000, 0, 850),
            ("Annual OTT Bundle", "Entertainment", 4999, 0, 450),
        ],
        "spin-wheel-entries": [
            ("Bonus Spin Entry", "Games", 0, 0, 100),
            ("Silver Wheel Entry", "Games", 0, 0, 150),
            ("Gold Wheel Entry", "Games", 0, 0, 250),
            ("Jackpot Wheel Entry", "Games", 0, 0, 500),
            ("Weekend Wheel Entry", "Games", 0, 0, 125),
        ],
    }
    if sink_type not in catalogs:
        raise ValueError(f"Unknown sink type: {sink_type}")

    base = catalogs[sink_type]
    now = datetime.now()
    items = []
    for i in range(count):
        title, category, original_price, discount_pct, coin_cost = base[i % len(base)]
        multiplier = 1 + (i % 6) * 0.1
        item = {
            "id": i + 1,
            "title": f"{title} #{i + 1}",
            "sink_type": sink_type,
            "category": category,
            "coin_cost": int(coin_cost * multiplier),
            "available": True,
            "quantity_left": 1 + (i % 12),
            "expires_at": (now + timedelta(minutes=15 + i)).isoformat(timespec="seconds"),
        }
        if original_price:
            item["original_price"] = round(original_price * multiplier, 2)
            item["discount_pct"] = min(60, discount_pct + (i % 10))
            item["final_price"] = round(item["original_price"] * (1 - item["discount_pct"] / 100), 2)
        if sink_type == "auctions":
            item["current_bid"] = item["coin_cost"]
            item["bids"] = 3 + (i % 35)
        if sink_type == "club-deals":
            item["members"] = 5 + (i % 80)
            item["club_pool"] = item["coin_cost"] * item["members"]
        items.append(item)
    return items


@router.get("/{sink_type}", response_model=List[Dict[str, Any]])
async def list_spending_sink(sink_type: str, limit: int = 120) -> List[Dict[str, Any]]:
    """List mock spending sink inventory."""
    try:
        return _build_sink_items(sink_type, count=max(1, min(limit, 200)))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{sink_type}/redeem", response_model=Dict[str, Any])
async def redeem_spending_sink(sink_type: str, request: SpendingActionRequest) -> Dict[str, Any]:
    """Spend ecosystem coins on a sink item."""
    try:
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        items = _build_sink_items(sink_type)
        item = next((entry for entry in items if entry["id"] == request.item_id), None)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spending item not found")

        coin_cost = item["coin_cost"]
        if user["coin_balance"] < coin_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Need {coin_cost}, have {user['coin_balance']}",
            )

        db.update_user_balance(request.user_id, -coin_cost)
        transaction_id = db.add_coin_transaction(
            request.user_id,
            -coin_cost,
            sink_type,
            f"Redeemed {item['title']} via {sink_type}",
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "sink_type": sink_type,
            "item_id": item["id"],
            "item_title": item["title"],
            "coins_spent": coin_cost,
            "new_balance": user["coin_balance"] - coin_cost,
            "withdrawable_balance": user.get("withdrawable_balance", 0),
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
