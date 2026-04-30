"""Club deal group-purchase endpoints."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database import Database

router = APIRouter(prefix="/api/club-deals", tags=["club-deals"])
db = Database()


class StartClubDealRequest(BaseModel):
    """Request to start a group purchase from a club pool."""

    user_id: int = Field(..., gt=0)
    club_id: str = Field(default="travel-squad", min_length=1)
    deal_id: str = Field(default="airport-lounge-bundle", min_length=1)
    invite_window_minutes: int = Field(default=30, ge=1, le=120)


class ClubDealResponseRequest(BaseModel):
    """Request for a club member response."""

    member_id: int = Field(..., gt=0)
    action: Literal["accept", "ignore"]


DEALS: Dict[str, Dict[str, Any]] = {
    "airport-lounge-bundle": {
        "id": "airport-lounge-bundle",
        "title": "Airport Lounge Bundle",
        "merchant": "Zolve Travel",
        "threshold": 3,
        "coins_required": 600,
        "cash_price": 2400,
        "member_price": 649,
    },
    "grocery-saver-pack": {
        "id": "grocery-saver-pack",
        "title": "Grocery Saver Pack",
        "merchant": "Zolve Essentials",
        "threshold": 4,
        "coins_required": 450,
        "cash_price": 1800,
        "member_price": 499,
    },
}


INITIAL_CLUBS: Dict[str, Dict[str, Any]] = {
    "travel-squad": {
        "id": "travel-squad",
        "name": "Travel Squad",
        "pool_balance": 2000,
        "members": [
            {"id": 1, "name": "Riddhima"},
            {"id": 2, "name": "Aarav"},
            {"id": 3, "name": "Maya"},
            {"id": 4, "name": "Kabir"},
            {"id": 5, "name": "Neha"},
        ],
    },
    "apartment-club": {
        "id": "apartment-club",
        "name": "Apartment Club",
        "pool_balance": 900,
        "members": [
            {"id": 1, "name": "Riddhima"},
            {"id": 6, "name": "Isha"},
            {"id": 7, "name": "Dev"},
            {"id": 8, "name": "Tara"},
        ],
    },
}

clubs: Dict[str, Dict[str, Any]] = {}
club_purchases: Dict[str, Dict[str, Any]] = {}
purchase_sequence = 1


def reset_demo_state() -> None:
    """Reset deterministic in-memory state for isolated tests."""
    global purchase_sequence
    clubs.clear()
    for club_id, club in INITIAL_CLUBS.items():
        clubs[club_id] = {
            **club,
            "members": [dict(member) for member in club["members"]],
        }
    club_purchases.clear()
    purchase_sequence = 1


reset_demo_state()


def _member_ids(club: Dict[str, Any]) -> List[int]:
    return [member["id"] for member in club["members"]]


def _public_purchase(purchase: Dict[str, Any]) -> Dict[str, Any]:
    club = clubs[purchase["club_id"]]
    accepted_count = sum(1 for action in purchase["responses"].values() if action == "accept")
    ignored_count = sum(1 for action in purchase["responses"].values() if action == "ignore")
    pending_count = len(purchase["responses"]) - accepted_count - ignored_count

    return {
        "purchase_id": purchase["id"],
        "status": purchase["status"],
        "club": {
            "id": club["id"],
            "name": club["name"],
            "pool_balance": club["pool_balance"],
        },
        "deal": purchase["deal"],
        "invite_window": {
            "started_at": purchase["started_at"],
            "expires_at": purchase["expires_at"],
            "window_minutes": purchase["window_minutes"],
            "channel": "push",
        },
        "responses": {
            "accepted_count": accepted_count,
            "ignored_count": ignored_count,
            "pending_count": pending_count,
            "threshold": purchase["deal"]["threshold"],
            "members": [
                {
                    "member_id": member_id,
                    "action": action,
                }
                for member_id, action in sorted(purchase["responses"].items())
            ],
        },
        "unlock": {
            "unlocked": purchase["status"] == "unlocked",
            "unlocked_at": purchase.get("unlocked_at"),
            "coins_deducted": purchase["coins_deducted"],
        },
    }


def _unlock_if_ready(purchase: Dict[str, Any]) -> None:
    if purchase["status"] == "unlocked":
        return

    accepted_count = sum(1 for action in purchase["responses"].values() if action == "accept")
    if accepted_count < purchase["deal"]["threshold"]:
        return

    club = clubs[purchase["club_id"]]
    coins_required = purchase["deal"]["coins_required"]
    if club["pool_balance"] < coins_required:
        purchase["status"] = "pool_insufficient"
        return

    club["pool_balance"] -= coins_required
    purchase["status"] = "unlocked"
    purchase["coins_deducted"] = coins_required
    purchase["unlocked_at"] = datetime.now().isoformat(timespec="seconds")
    db.add_coin_transaction(
        purchase["initiator_user_id"],
        -coins_required,
        "club_deal_unlock",
        f"Unlocked {purchase['deal']['title']} from {club['name']} shared pool",
    )


@router.get("/catalog", response_model=List[Dict[str, Any]])
async def list_club_deal_catalog() -> List[Dict[str, Any]]:
    """List deterministic club deal options."""
    return list(DEALS.values())


@router.get("/clubs", response_model=List[Dict[str, Any]])
async def list_clubs() -> List[Dict[str, Any]]:
    """List deterministic club pool state."""
    return list(clubs.values())


@router.post("/start", response_model=Dict[str, Any])
async def start_group_purchase(request: StartClubDealRequest) -> Dict[str, Any]:
    """Start a push-style group purchase invitation window."""
    global purchase_sequence

    user = db.get_user(request.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    club = clubs.get(request.club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    if request.user_id not in _member_ids(club):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a club member")

    deal = DEALS.get(request.deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club deal not found")

    now = datetime.now()
    purchase_id = f"cd-{purchase_sequence}"
    purchase_sequence += 1
    purchase = {
        "id": purchase_id,
        "club_id": club["id"],
        "initiator_user_id": request.user_id,
        "deal": dict(deal),
        "started_at": now.isoformat(timespec="seconds"),
        "expires_at": (now + timedelta(minutes=request.invite_window_minutes)).isoformat(timespec="seconds"),
        "window_minutes": request.invite_window_minutes,
        "status": "inviting",
        "coins_deducted": 0,
        "responses": {
            member["id"]: "accept" if member["id"] == request.user_id else "pending"
            for member in club["members"]
        },
    }
    club_purchases[purchase_id] = purchase
    _unlock_if_ready(purchase)

    return {
        "success": True,
        "message": "Group purchase started and push invites sent.",
        **_public_purchase(purchase),
    }


@router.get("/{purchase_id}", response_model=Dict[str, Any])
async def get_group_purchase(purchase_id: str) -> Dict[str, Any]:
    """Get current group purchase state."""
    purchase = club_purchases.get(purchase_id)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group purchase not found")
    return _public_purchase(purchase)


@router.post("/{purchase_id}/respond", response_model=Dict[str, Any])
async def respond_to_group_purchase(purchase_id: str, request: ClubDealResponseRequest) -> Dict[str, Any]:
    """Accept or ignore a club deal invitation."""
    purchase = club_purchases.get(purchase_id)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group purchase not found")
    if request.member_id not in purchase["responses"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member invite not found")

    expires_at = datetime.fromisoformat(purchase["expires_at"])
    if datetime.now() > expires_at and purchase["status"] != "unlocked":
        purchase["status"] = "expired"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite window expired")

    purchase["responses"][request.member_id] = request.action
    _unlock_if_ready(purchase)

    return {
        "success": True,
        "message": f"Member response recorded as {request.action}.",
        **_public_purchase(purchase),
    }
