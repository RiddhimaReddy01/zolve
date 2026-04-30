"""Game endpoints (scratch card, spin wheel)."""

from fastapi import APIRouter, HTTPException, status

from models import ScratchCardRequest, SpinWheelRequest, ScratchCardResponse, SpinWheelResponse
from database import Database
from game_engine import play_scratch_card, play_spin_wheel
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
    """Play spin wheel game.

    Spin wheel costs 100 coins and returns coins based on luck.

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

        # Check balance (100 coins required)
        SPIN_COST = 100
        if user["coin_balance"] < SPIN_COST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Need {SPIN_COST}, have {user['coin_balance']}",
            )

        # Deduct cost
        db.update_user_balance(request.user_id, -SPIN_COST)

        # Play game
        result = play_spin_wheel()

        # Calculate net (cost - winnings)
        net_coins = result["coins_won"] - SPIN_COST

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
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
