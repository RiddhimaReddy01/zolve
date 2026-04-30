"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import coins, marketplace, games, bank
from database import Database
from models import ErrorResponse

# Initialize app
app = FastAPI(
    title="Zolve MVP",
    description="Behavioral finance gamification platform",
    version="1.0.0",
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(coins.router)
app.include_router(marketplace.router)
app.include_router(games.router)
app.include_router(bank.router)

# Initialize database
db = Database()


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        dict with status
    """
    return {"status": "ok", "service": "zolve-backend"}


@app.get("/api/user/{user_id}")
async def get_user_dashboard(user_id: int) -> dict:
    """Get user dashboard data.

    Args:
        user_id: User ID

    Returns:
        User profile with balance, tier, activity feed
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Get transaction history
        history = db.get_transaction_history(user_id, limit=10)

        # Get verified behaviors
        verified = db.get_verified_behaviors(user_id)
        verified_count = len(verified)

        return {
            "user_id": user_id,
            "name": user["name"],
            "email": user["email"],
            "balance": user["coin_balance"],
            "tier": user["tier"],
            "credit_score": user["credit_score"],
            "verified_behaviors_count": verified_count,
            "activity_feed": [
                {
                    "id": t["id"],
                    "amount": t["amount"],
                    "event_type": t["event_type"],
                    "description": t["description"],
                    "created_at": t["created_at"],
                }
                for t in history
            ],
            "created_at": user["created_at"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/verified-behaviors/{user_id}")
async def get_verified_behaviors(user_id: int) -> dict:
    """Get all verified behaviors for a user.

    Args:
        user_id: User ID

    Returns:
        List of verified behaviors with coins awarded
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        verified = db.get_verified_behaviors(user_id)

        return {
            "user_id": user_id,
            "verified_behaviors": [
                {
                    "id": b["id"],
                    "behavior_type": b["behavior_type"],
                    "verified": b["verified"],
                    "verification_source": b["verification_source"],
                    "behavior_data": b["behavior_data"],
                    "completed_at": b["completed_at"],
                }
                for b in verified
            ],
            "total_count": len(verified),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/tier-progress/{user_id}")
async def get_tier_progress(user_id: int) -> dict:
    """Get user's progress toward next tier.

    Args:
        user_id: User ID

    Returns:
        Tier progress data
    """
    try:
        from game_engine import calculate_tier_progress

        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        verified_count = db.count_verified_behaviors(user_id)
        progress = calculate_tier_progress(user["coin_balance"], verified_count)

        return progress
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10) -> dict:
    """Get top users by coin balance (simulated).

    Args:
        limit: Number of top users to return

    Returns:
        Leaderboard data
    """
    # For MVP, return demo user
    user = db.get_user(1)
    if user:
        return {
            "leaderboard": [
                {
                    "rank": 1,
                    "user_id": user["id"],
                    "name": user["name"],
                    "balance": user["coin_balance"],
                    "tier": user["tier"],
                }
            ],
            "total_users": 1,
        }
    return {"leaderboard": [], "total_users": 0}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
    )
