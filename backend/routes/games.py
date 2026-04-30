"""Game endpoints (scratch card, spin wheel, easter eggs)."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from models import ScratchCardRequest, SpinWheelRequest, ScratchCardResponse, SpinWheelResponse
from database import Database
from game_engine import play_scratch_card, play_spin_wheel_for_user
from exceptions import UserNotFoundError

router = APIRouter(prefix="/api/games", tags=["games"])
db = Database()


@router.post("/scratch", response_model=ScratchCardResponse)
async def play_scratch(request: ScratchCardRequest) -> ScratchCardResponse:
    """Play scratch card game.

    Scratch card is free to play and returns coins based on luck.

    Args:
        request: ScratchCardRequest with user_id

    Returns:
        ScratchCardResponse with result and coins won
    """
    try:
        # Validate user exists
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Play game
        result = play_scratch_card()

        # Award coins
        if result["coins_won"] > 0:
            db.update_user_balance(request.user_id, result["coins_won"])
            db.add_coin_transaction(
                request.user_id,
                result["coins_won"],
                "scratch_card",
                f"Scratch card: {result['result']} - won {result['coins_won']} coins",
            )

        return ScratchCardResponse(
            result=result["result"],
            coins_won=result["coins_won"],
            message=result["message"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/spin", response_model=SpinWheelResponse)
async def play_spin(request: SpinWheelRequest) -> SpinWheelResponse:
    """Play spin wheel game with behavior-based probability boost.

    Spin wheel costs 100 coins and returns coins based on luck.
    Odds improve based on number of verified behaviors.

    Args:
        request: SpinWheelRequest with user_id

    Returns:
        SpinWheelResponse with result and coins won
    """
    try:
        # Validate user exists
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        earned_spin = db.consume_game_entitlement(request.user_id, "spin")

        # Check balance (100 coins required) only when no earned spin is available.
        SPIN_COST = 100
        cost_paid = 0
        if not earned_spin and user["coin_balance"] < SPIN_COST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Need {SPIN_COST}, have {user['coin_balance']}",
            )

        if not earned_spin:
            db.update_user_balance(request.user_id, -SPIN_COST)
            cost_paid = SPIN_COST

        # Get verified behavior count for behavior-based boost
        verified_behavior_count = db.get_verified_behavior_count(request.user_id)

        # Play game with behavior boost
        result = play_spin_wheel_for_user(verified_behavior_count)

        # Calculate net (cost - winnings)
        net_coins = result["coins_won"] - cost_paid

        # Award coins
        if result["coins_won"] > 0:
            db.update_user_balance(request.user_id, result["coins_won"])

        # Log transaction
        db.add_coin_transaction(
            request.user_id,
            net_coins,
            "spin_wheel",
            f"Spin wheel: Segment {result['segment_number']} - won {result['coins_won']} coins",
        )

        return SpinWheelResponse(
            segment_number=result["segment_number"],
            coins_won=result["coins_won"],
            message=result["message"],
            cost_paid=cost_paid,
            used_earned_spin=earned_spin is not None,
            spins_remaining=db.get_available_entitlement_count(request.user_id, "spin"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/scratch-cards/{user_id}", response_model=List[Dict[str, Any]])
async def get_pending_scratch_cards(user_id: int) -> List[Dict[str, Any]]:
    """Get all pending (unscratched) scratch cards for a user.

    Args:
        user_id: User ID

    Returns:
        List of pending scratch card triggers
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        cards = db.get_pending_scratch_cards(user_id)
        return [dict(card) for card in cards]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/easter-eggs/{user_id}", response_model=List[Dict[str, Any]])
async def get_easter_eggs(user_id: int) -> List[Dict[str, Any]]:
    """Get all easter eggs for a user.

    Args:
        user_id: User ID

    Returns:
        List of easter eggs with their status
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        eggs = db.get_easter_eggs(user_id)
        return [dict(egg) for egg in eggs]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/easter-eggs/claim", response_model=Dict[str, Any])
async def claim_easter_egg(user_id: int, egg_id: int) -> Dict[str, Any]:
    """Claim an easter egg and award coins.

    Args:
        user_id: User ID
        egg_id: Easter egg ID

    Returns:
        dict with success status and coins awarded
    """
    try:
        # Validate user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Get the easter egg
        egg = db.claim_easter_egg(egg_id, user_id)

        # Award coins
        from constants import EASTER_EGG_CONDITIONS
        egg_type = egg["egg_type"]
        coins = EASTER_EGG_CONDITIONS.get(egg_type, {}).get("coins", 200)

        db.update_user_balance(user_id, coins)
        db.add_coin_transaction(
            user_id,
            coins,
            "easter_egg",
            f"Claimed easter egg: {egg_type} - awarded {coins} coins",
        )

        return {
            "success": True,
            "egg_id": egg_id,
            "egg_type": egg_type,
            "coins_awarded": coins,
            "new_balance": user["coin_balance"] + coins,
            "message": f"Congratulations! You earned {coins} coins!",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
