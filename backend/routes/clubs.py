"""Club formation and social loop endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/clubs", tags=["clubs"])


class ClubCreateRequest(BaseModel):
    """Request to create a club."""

    user_id: int = Field(..., gt=0)
    club_name: str = Field(..., min_length=1, max_length=80)
    goal_name: str = Field(default="Build better money habits", min_length=1, max_length=120)


class ClubJoinRequest(BaseModel):
    """Request to join a club via invite."""

    user_id: int = Field(..., gt=0)
    invite_code: str = Field(..., min_length=4, max_length=32)


class ClubEventRequest(BaseModel):
    """Request to record a social progress event."""

    user_id: int = Field(..., gt=0)
    event_type: str = Field(..., min_length=1, max_length=60)
    amount: Optional[float] = Field(default=None, ge=0)


class QuestContributionRequest(BaseModel):
    """Request to contribute directly to a club quest."""

    user_id: int = Field(..., gt=0)
    progress: int = Field(..., gt=0, le=500)


USER_NAMES = {
    1: "Riddhima",
    2: "Aarav",
    3: "Maya",
    4: "Dev",
    5: "Nisha",
    6: "Kabir",
}

EVENT_PROGRESS = {
    "paid_bill": 75,
    "savings_deposit": 60,
    "credit_utilization_drop": 50,
    "rent_paid": 65,
    "quest_checkin": 25,
}

TIER_THRESHOLDS = [
    ("Bronze", 0),
    ("Silver", 200),
    ("Gold", 500),
    ("Platinum", 900),
]

DEFAULT_QUESTS = [
    {
        "id": "bill-streak",
        "title": "Pay 5 bills on time",
        "target": 5,
        "unit": "bill_payments",
        "reward": "Unlock 2% fee-back pool",
    },
    {
        "id": "savings-sprint",
        "title": "Make 4 savings deposits",
        "target": 4,
        "unit": "deposits",
        "reward": "Unlock group flash-deal boost",
    },
    {
        "id": "credit-builder",
        "title": "Log 3 credit-building wins",
        "target": 3,
        "unit": "credit_wins",
        "reward": "Upgrade club tier multiplier",
    },
]

_clubs: Dict[int, Dict[str, Any]] = {}
_invite_index: Dict[str, int] = {}
_next_club_id = 1
_next_event_id = 1


def reset_demo_state() -> None:
    """Reset in-module demo state for isolated tests."""
    global _next_club_id, _next_event_id

    _clubs.clear()
    _invite_index.clear()
    _next_club_id = 1
    _next_event_id = 1


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _user_name(user_id: int) -> str:
    return USER_NAMES.get(user_id, f"Member {user_id}")


def _make_invite_code(club_id: int, club_name: str) -> str:
    clean = "".join(ch for ch in club_name.upper() if ch.isalnum())[:6] or "CLUB"
    return f"{clean}-{club_id:03d}"


def _empty_quest(template: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **template,
        "progress": 0,
        "completed": False,
    }


def _tier_for_progress(progress: int) -> str:
    current = "Bronze"
    for tier, threshold in TIER_THRESHOLDS:
        if progress >= threshold:
            current = tier
    return current


def _next_tier(progress: int) -> Optional[Dict[str, Any]]:
    for tier, threshold in TIER_THRESHOLDS:
        if progress < threshold:
            return {
                "tier": tier,
                "points_needed": threshold - progress,
            }
    return None


def _club_or_404(club_id: int) -> Dict[str, Any]:
    club = _clubs.get(club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    return club


def _member_or_404(club: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    member = club["members"].get(user_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club member not found")
    return member


def _leaderboard(club: Dict[str, Any]) -> List[Dict[str, Any]]:
    members = sorted(
        club["members"].values(),
        key=lambda item: (-item["score"], item["joined_at"], item["user_id"]),
    )
    return [
        {
            "rank": index + 1,
            "user_id": member["user_id"],
            "name": member["name"],
            "score": member["score"],
            "contributions": member["contributions"],
        }
        for index, member in enumerate(members)
    ]


def _event_message(user_name: str, event_type: str, progress: int) -> str:
    labels = {
        "paid_bill": "paid a bill",
        "savings_deposit": "made a savings deposit",
        "credit_utilization_drop": "lowered credit utilization",
        "rent_paid": "paid rent on time",
        "quest_checkin": "checked in on a quest",
    }
    action = labels.get(event_type, event_type.replace("_", " "))
    return f"{user_name} {action} -> club progress increased by {progress}"


def _record_event(club: Dict[str, Any], user_id: int, event_type: str, progress: int, amount: Optional[float]) -> Dict[str, Any]:
    global _next_event_id

    member = _member_or_404(club, user_id)
    previous_tier = club["tier"]
    club["shared_progress"] += progress
    club["tier"] = _tier_for_progress(club["shared_progress"])
    member["score"] += progress
    member["contributions"] += 1

    if event_type == "paid_bill":
        _advance_quest(club, "bill-streak", 1)
    elif event_type == "savings_deposit":
        _advance_quest(club, "savings-sprint", 1)
    elif event_type in {"credit_utilization_drop", "quest_checkin"}:
        _advance_quest(club, "credit-builder", 1)

    event = {
        "id": _next_event_id,
        "club_id": club["id"],
        "user_id": user_id,
        "user_name": member["name"],
        "event_type": event_type,
        "amount": amount,
        "progress_delta": progress,
        "message": _event_message(member["name"], event_type, progress),
        "created_at": _now(),
    }
    _next_event_id += 1
    club["events"].insert(0, event)

    if club["tier"] != previous_tier:
        club["events"].insert(
            0,
            {
                "id": _next_event_id,
                "club_id": club["id"],
                "user_id": None,
                "user_name": "Club",
                "event_type": "tier_upgrade",
                "amount": None,
                "progress_delta": 0,
                "message": f"{club['name']} upgraded from {previous_tier} to {club['tier']}",
                "created_at": _now(),
            },
        )
        _next_event_id += 1

    return event


def _record_feed_item(
    club: Dict[str, Any],
    user_id: Optional[int],
    user_name: str,
    event_type: str,
    message: str,
    progress: int = 0,
    amount: Optional[float] = None,
) -> Dict[str, Any]:
    global _next_event_id

    event = {
        "id": _next_event_id,
        "club_id": club["id"],
        "user_id": user_id,
        "user_name": user_name,
        "event_type": event_type,
        "amount": amount,
        "progress_delta": progress,
        "message": message,
        "created_at": _now(),
    }
    _next_event_id += 1
    club["events"].insert(0, event)
    return event


def _advance_quest(club: Dict[str, Any], quest_id: str, progress: int) -> Dict[str, Any]:
    quest = next((item for item in club["quests"] if item["id"] == quest_id), None)
    if not quest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found")

    quest["progress"] = min(quest["target"], quest["progress"] + progress)
    quest["completed"] = quest["progress"] >= quest["target"]
    return quest


def _dashboard_payload(club: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "club_id": club["id"],
        "name": club["name"],
        "goal_name": club["goal_name"],
        "invite_code": club["invite_code"],
        "tier": club["tier"],
        "shared_progress": club["shared_progress"],
        "next_tier": _next_tier(club["shared_progress"]),
        "incentives": {
            "tier_multiplier": {
                "Bronze": 1.0,
                "Silver": 1.1,
                "Gold": 1.25,
                "Platinum": 1.5,
            }[club["tier"]],
            "active_rewards": [
                quest["reward"]
                for quest in club["quests"]
                if quest["completed"]
            ],
        },
        "members": list(club["members"].values()),
        "leaderboard": _leaderboard(club),
        "quests": club["quests"],
        "social_feed": club["events"][:20],
    }


@router.post("", response_model=Dict[str, Any])
async def create_club(request: ClubCreateRequest) -> Dict[str, Any]:
    """Create a club with the requesting user as the first member."""
    global _next_club_id

    club_id = _next_club_id
    _next_club_id += 1
    invite_code = _make_invite_code(club_id, request.club_name)
    member = {
        "user_id": request.user_id,
        "name": _user_name(request.user_id),
        "role": "owner",
        "score": 0,
        "contributions": 0,
        "joined_at": _now(),
    }
    club = {
        "id": club_id,
        "name": request.club_name,
        "goal_name": request.goal_name,
        "invite_code": invite_code,
        "tier": "Bronze",
        "shared_progress": 0,
        "members": {request.user_id: member},
        "quests": [_empty_quest(quest) for quest in DEFAULT_QUESTS],
        "events": [],
        "created_at": _now(),
    }
    _clubs[club_id] = club
    _invite_index[invite_code] = club_id

    return {
        "success": True,
        "club_id": club_id,
        "invite_code": invite_code,
        "dashboard": _dashboard_payload(club),
    }


@router.post("/join", response_model=Dict[str, Any])
async def join_club(request: ClubJoinRequest) -> Dict[str, Any]:
    """Join an existing club using its invite code."""
    club_id = _invite_index.get(request.invite_code)
    if not club_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")

    club = _club_or_404(club_id)
    if request.user_id in club["members"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already joined this club")

    club["members"][request.user_id] = {
        "user_id": request.user_id,
        "name": _user_name(request.user_id),
        "role": "member",
        "score": 0,
        "contributions": 0,
        "joined_at": _now(),
    }
    _record_feed_item(
        club,
        request.user_id,
        _user_name(request.user_id),
        "member_joined",
        f"{_user_name(request.user_id)} joined {club['name']} via invite",
    )

    return {
        "success": True,
        "club_id": club_id,
        "member_count": len(club["members"]),
        "dashboard": _dashboard_payload(club),
    }


@router.get("/{club_id}/dashboard", response_model=Dict[str, Any])
async def get_club_dashboard(club_id: int) -> Dict[str, Any]:
    """Return members, shared progress, quests, feed, and leaderboard."""
    return _dashboard_payload(_club_or_404(club_id))


@router.post("/{club_id}/events", response_model=Dict[str, Any])
async def record_social_event(club_id: int, request: ClubEventRequest) -> Dict[str, Any]:
    """Record a social trigger that increases club progress."""
    club = _club_or_404(club_id)
    progress = EVENT_PROGRESS.get(request.event_type)
    if progress is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported club event type")

    event = _record_event(club, request.user_id, request.event_type, progress, request.amount)
    return {
        "success": True,
        "event": event,
        "dashboard": _dashboard_payload(club),
    }


@router.post("/{club_id}/quests/{quest_id}/contribute", response_model=Dict[str, Any])
async def contribute_to_quest(club_id: int, quest_id: str, request: QuestContributionRequest) -> Dict[str, Any]:
    """Contribute directly to a collective club quest."""
    club = _club_or_404(club_id)
    member = _member_or_404(club, request.user_id)
    quest = _advance_quest(club, quest_id, request.progress)
    progress = request.progress * 25
    previous_tier = club["tier"]
    club["shared_progress"] += progress
    club["tier"] = _tier_for_progress(club["shared_progress"])
    member["score"] += progress
    member["contributions"] += 1
    _record_feed_item(
        club,
        request.user_id,
        member["name"],
        "quest_contribution",
        f"{member['name']} advanced {quest['title']} -> club progress increased by {progress}",
        progress,
    )
    if club["tier"] != previous_tier:
        _record_feed_item(
            club,
            None,
            "Club",
            "tier_upgrade",
            f"{club['name']} upgraded from {previous_tier} to {club['tier']}",
        )

    return {
        "success": True,
        "quest": quest,
        "dashboard": _dashboard_payload(club),
    }
