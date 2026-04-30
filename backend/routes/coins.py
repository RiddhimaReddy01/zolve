"""Coin earning and balance endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime

from models import EarnRequest, BalanceResponse, CoinTransactionResponse, ErrorResponse
from database import Database
from game_engine import calculate_coins_for_action, calculate_user_tier, check_daily_earning_cap, maybe_record_tier_change
from exceptions import InvalidActionError, DailyCoinCapError, UserNotFoundError

router = APIRouter(prefix="/api/coins", tags=["coins"])
db = Database()


@router.post("/earn", response_model=Dict[str, Any])
async def earn_coins(request: EarnRequest) -> Dict[str, Any]:
    """Earn coins for an action.

    Args:
        request: EarnRequest with user_id and action_type

    Returns:
        dict with coins_earned, new_balance, tier
    """
    try:
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Calculate ecosystem coins for action. Bank-verified coins are handled
        # separately by /api/bank/verify-behaviors and can become withdrawable.
        coins = calculate_coins_for_action(request.action_type)

        # Get transaction history for today
        history = db.get_transaction_history(request.user_id, limit=100)
        today = datetime.now().strftime("%Y-%m-%d")
        today_transactions = [
            h for h in history
            if h["created_at"].startswith(today)
        ]

        # Check daily cap
        check_daily_earning_cap(request.user_id, request.action_type, today_transactions)

        # Update balance
        db.update_user_balance(request.user_id, coins)

        # Log transaction
        transaction_id = db.add_coin_transaction(
            request.user_id,
            coins,
            request.action_type,
            f"Earned {coins} coins for {request.action_type}",
        )

        # Get updated user data and check for tier change
        user = db.get_user(request.user_id)
        verified_count = db.count_verified_behaviors(request.user_id)
        new_tier = maybe_record_tier_change(
            db,
            request.user_id,
            user["tier"],
            user["coin_balance"],
            verified_count,
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "coins_earned": coins,
            "new_balance": user["coin_balance"] + coins,
            "withdrawable_balance": user.get("withdrawable_balance", 0),
            "earning_type": "ecosystem",
            "new_tier": new_tier,
            "message": f"You earned {coins} coins!",
        }

    except InvalidActionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DailyCoinCapError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/balance/{user_id}", response_model=BalanceResponse)
async def get_balance(user_id: int) -> BalanceResponse:
    """Get user coin balance and tier.

    Args:
        user_id: User ID

    Returns:
        BalanceResponse with balance and tier
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return BalanceResponse(
            user_id=user_id,
            balance=user["coin_balance"],
            withdrawable_balance=user.get("withdrawable_balance", 0),
            ecosystem_balance=user["coin_balance"] - user.get("withdrawable_balance", 0),
            tier=user["tier"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history/{user_id}", response_model=List[CoinTransactionResponse])
async def get_coin_history(user_id: int, limit: int = 50) -> List[CoinTransactionResponse]:
    """Get user coin transaction history.

    Args:
        user_id: User ID
        limit: Max number of transactions to return

    Returns:
        List of CoinTransactionResponse
    """
    try:
        transactions = db.get_transaction_history(user_id, limit=limit)
        return [
            CoinTransactionResponse(
                transaction_id=t["id"],
                user_id=t["user_id"],
                amount=t["amount"],
                event_type=t["event_type"],
                description=t["description"],
                created_at=t["created_at"],
            )
            for t in transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
