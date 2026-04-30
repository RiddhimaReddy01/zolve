"""Ad-watching endpoints for earning ecosystem coins."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime

from models import AdStartRequest, AdCompleteRequest
from database import Database
from constants import EARNING_WEIGHTS, DAILY_EARNING_CAPS
from exceptions import UserNotFoundError

router = APIRouter(prefix="/api/ads", tags=["ads"])
db = Database()

# Mock ad catalog
MOCK_ADS = [
    {"id": "ad_001", "brand": "Swiggy", "title": "Order now, get 20% off", "duration_sec": 15},
    {"id": "ad_002", "brand": "Uber", "title": "Ride safe, ride Uber", "duration_sec": 30},
    {"id": "ad_003", "brand": "Zomato", "title": "Craving something?", "duration_sec": 15},
    {"id": "ad_004", "brand": "Paytm", "title": "Fast payments", "duration_sec": 20},
    {"id": "ad_005", "brand": "CRED", "title": "Pay bills, earn rewards", "duration_sec": 30},
]


@router.get("", response_model=Dict[str, Any])
async def list_ads() -> Dict[str, Any]:
    """List all available ads with reward info.

    Returns:
        dict with ads list including reward_coins per ad
    """
    reward_coins = EARNING_WEIGHTS["ad_watch"]
    ads_with_rewards = [
        {**ad, "reward_coins": reward_coins}
        for ad in MOCK_ADS
    ]
    return {
        "ads": ads_with_rewards,
        "total_count": len(ads_with_rewards),
        "daily_cap": DAILY_EARNING_CAPS["ad_watch"],
        "message": "Watch ads to earn ecosystem coins"
    }


@router.post("/start", response_model=Dict[str, Any])
async def start_ad(request: AdStartRequest) -> Dict[str, Any]:
    """Start watching an ad (create ad_view record).

    Args:
        request: AdStartRequest with user_id and ad_id

    Returns:
        dict with ad_view_id and message
    """
    try:
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Validate ad exists
        valid_ad_ids = {ad["id"] for ad in MOCK_ADS}
        if request.ad_id not in valid_ad_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ad_id")

        # Create ad_view record
        ad_view_id = db.add_ad_view(request.user_id, request.ad_id)

        return {
            "success": True,
            "ad_view_id": ad_view_id,
            "ad_id": request.ad_id,
            "message": "Ad started"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/complete", response_model=Dict[str, Any])
async def complete_ad(request: AdCompleteRequest) -> Dict[str, Any]:
    """Complete watching an ad and earn coins.

    Args:
        request: AdCompleteRequest with user_id and ad_view_id

    Returns:
        dict with success, coins_earned, new_balance

    Raises:
        429 if daily ad cap (3 ads/day) already reached
    """
    try:
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Validate ad_view exists and belongs to user
        ad_view = db.get_ad_view(request.ad_view_id)
        if not ad_view:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad view not found")

        if ad_view["user_id"] != request.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ad view does not belong to user")

        # Check if already completed
        if ad_view["completed_at"] is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This ad view was already completed"
            )

        # Check daily cap: max 3 ads per day = 30 coins
        today_count = db.get_today_ad_count(request.user_id)
        daily_cap = DAILY_EARNING_CAPS["ad_watch"] // EARNING_WEIGHTS["ad_watch"]  # 30 / 10 = 3 ads
        if today_count >= daily_cap:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily ad cap reached. Max {daily_cap} ads per day."
            )

        # Credit coins
        coins_earned = EARNING_WEIGHTS["ad_watch"]
        db.update_user_balance(request.user_id, coins_earned)

        # Log transaction
        db.add_coin_transaction(
            request.user_id,
            coins_earned,
            "ad_watch",
            f"Completed ad {ad_view['ad_id']}"
        )

        # Mark ad_view as completed
        db.complete_ad_view(request.ad_view_id, coins_earned)

        # Get updated user
        user = db.get_user(request.user_id)
        new_balance = user["coin_balance"]

        return {
            "success": True,
            "coins_earned": coins_earned,
            "new_balance": new_balance,
            "message": f"You earned {coins_earned} ecosystem coins!"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
