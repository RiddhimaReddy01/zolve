"""Z-World activation, engagement, and financial reward flows."""

import json
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from constants import (
    DAILY_SPIN_GRANT,
    FIRST_SCRATCH_CARD_PURCHASE_AMOUNT,
    ON_TIME_PAYMENT_SPIN_GRANT,
    SIGNUP_BONUS_ZCOINS,
    EARNING_WEIGHTS,
)
from database import Database
from game_engine import maybe_record_tier_change
from models import FinancialEventRequest, ZWorldOnboardingRequest


router = APIRouter(prefix="/api/z-world", tags=["z-world"])
db = Database()


def _require_user(user_id: int) -> Dict[str, Any]:
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _latest_notification(user_id: int) -> Dict[str, Any] | None:
    notifications = db.get_notifications(user_id, limit=1)
    return notifications[0] if notifications else None


def _reward_feed(user_id: int) -> List[Dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "amount": item["amount"],
            "event_type": item["event_type"],
            "description": item["description"],
            "created_at": item["created_at"],
        }
        for item in db.get_transaction_history(user_id, limit=8)
    ]


def _next_actions(user_id: int) -> List[Dict[str, str]]:
    user = db.get_user(user_id)
    verified_count = db.count_verified_behaviors(user_id)
    actions = []

    if verified_count == 0:
        actions.append({
            "action": "link_bank",
            "label": "Link a bank account to earn verified coins",
            "deep_link": "/link-bank",
        })
    actions.append({
        "action": "daily_checkin",
        "label": "Complete today's check-in to earn more coins",
        "deep_link": "/earn",
    })
    if user and user["coin_balance"] >= 100:
        actions.append({
            "action": "check_zkart",
            "label": "Check Z-Kart for coin-boosted offers",
            "deep_link": "/zkart",
        })
    actions.append({
        "action": "check_club_activity",
        "label": "Check Z-Club activity",
        "deep_link": "/clubs",
    })
    return actions


@router.get("/intro", response_model=Dict[str, Any])
async def get_z_world_intro() -> Dict[str, Any]:
    """Return the first Z-World value proposition and forced steps."""
    return {
        "title": "Z-World",
        "value_proposition": "Earn rewards for financial behavior",
        "forced_steps": [
            "Join or create a Z-Club",
            "Accept coin system rules",
        ],
        "initial_rewards": {
            "signup_bonus_zcoins": SIGNUP_BONUS_ZCOINS,
            "first_scratch_card_unlocked": True,
        },
        "landing": "z_world_dashboard",
    }


@router.post("/onboarding/complete", response_model=Dict[str, Any])
async def complete_z_world_onboarding(request: ZWorldOnboardingRequest) -> Dict[str, Any]:
    """Complete first-time onboarding and grant activation rewards once."""
    user = _require_user(request.user_id)
    existing = db.get_z_world_onboarding(request.user_id)
    already_bonus = bool(existing and existing["signup_bonus_granted"])

    scratch_card_id = existing["first_scratch_card_id"] if existing else None
    rewards = {
        "signup_bonus_zcoins": 0,
        "first_scratch_card_unlocked": False,
    }

    if not already_bonus:
        db.update_user_balance(request.user_id, SIGNUP_BONUS_ZCOINS)
        db.add_coin_transaction(
            request.user_id,
            SIGNUP_BONUS_ZCOINS,
            "z_world_signup_bonus",
            "Z-World signup bonus",
        )
        scratch_card_id = db.add_scratch_card_trigger(
            request.user_id,
            purchase_id=0,
            purchase_amount=FIRST_SCRATCH_CARD_PURCHASE_AMOUNT,
        )
        db.add_notification(
            request.user_id,
            "push",
            "Welcome to Z-World",
            "Your signup bonus and first scratch card are ready.",
            "/z-world",
        )
        rewards = {
            "signup_bonus_zcoins": SIGNUP_BONUS_ZCOINS,
            "first_scratch_card_unlocked": True,
        }

    db.upsert_z_world_onboarding(
        request.user_id,
        request.club_action,
        request.club_name,
        request.invite_code,
        int(scratch_card_id or 0),
    )

    updated_user = db.get_user(request.user_id)
    verified_count = db.count_verified_behaviors(request.user_id)
    maybe_record_tier_change(
        db,
        request.user_id,
        user["tier"],
        updated_user["coin_balance"],
        verified_count,
    )

    return {
        "success": True,
        "onboarding_complete": True,
        "club": {
            "action": request.club_action,
            "name": request.club_name,
            "invite_code": request.invite_code,
        },
        "accepted_coin_rules": True,
        "rewards": rewards,
        "landing": "z_world_dashboard",
        "dashboard": await get_z_world_dashboard(request.user_id),
    }


@router.post("/daily-engagement/{user_id}", response_model=Dict[str, Any])
async def grant_daily_engagement(user_id: int) -> Dict[str, Any]:
    """Grant today's daily spin and return dashboard landing state."""
    _require_user(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    notifications = db.get_notifications(user_id, limit=50)
    already_granted = any(
        item["title"] == "You earned a spin today" and item["created_at"].startswith(today)
        for item in notifications
    )

    spins_granted = 0
    if not already_granted:
        db.grant_game_entitlement(user_id, "spin", "daily_engagement", DAILY_SPIN_GRANT)
        db.add_notification(
            user_id,
            "push",
            "You earned a spin today",
            "Open Z-World to spin the wheel.",
            "/z-world",
        )
        spins_granted = DAILY_SPIN_GRANT

    return {
        "success": True,
        "spins_granted": spins_granted,
        "notification": _latest_notification(user_id),
        "landing": "z_world_dashboard",
        "dashboard": await get_z_world_dashboard(user_id),
    }


@router.get("/dashboard/{user_id}", response_model=Dict[str, Any])
async def get_z_world_dashboard(user_id: int) -> Dict[str, Any]:
    """Return the Z-World dashboard state for activation and daily loops."""
    user = _require_user(user_id)
    onboarding = db.get_z_world_onboarding(user_id)
    scratch_cards = db.get_pending_scratch_cards(user_id)
    spins_available = db.get_available_entitlement_count(user_id, "spin")

    return {
        "user_id": user_id,
        "name": user["name"],
        "balance": user["coin_balance"],
        "tier": user["tier"],
        "onboarding": {
            "required": onboarding is None,
            "completed": onboarding is not None and onboarding["completed_at"] is not None,
            "accepted_coin_rules": bool(onboarding and onboarding["accepted_coin_rules"]),
            "club_name": onboarding["club_name"] if onboarding else None,
        },
        "daily_loop": {
            "spins_available": spins_available,
            "scratch_cards_available": len(scratch_cards),
            "latest_notification": _latest_notification(user_id),
            "next_actions": _next_actions(user_id),
            "loop_closure": [
                {"label": "Check Z-Kart", "deep_link": "/zkart"},
                {"label": "Check Club activity", "deep_link": "/clubs"},
            ],
        },
        "reward_feed": _reward_feed(user_id),
    }


@router.post("/financial-events", response_model=Dict[str, Any])
async def process_financial_event(request: FinancialEventRequest) -> Dict[str, Any]:
    """Evaluate a financial event and assign behavior-linked rewards."""
    user = _require_user(request.user_id)

    if request.event_type != "payment_completed_on_time":
        event_id = db.add_financial_event(
            request.user_id,
            request.event_type,
            "not_eligible",
            0,
            0,
            json.dumps(request.metadata, sort_keys=True),
        )
        return {
            "success": True,
            "event_id": event_id,
            "eligible": False,
            "coins_awarded": 0,
            "spins_unlocked": 0,
            "message": "No Z-World reward rule matched this event.",
        }

    coins = EARNING_WEIGHTS["on_time_payment"]
    spins = ON_TIME_PAYMENT_SPIN_GRANT
    metadata = dict(request.metadata)
    metadata.setdefault("detected_behavior", "on_time_payment")

    db.update_user_balance(request.user_id, coins)
    db.update_withdrawable_balance(request.user_id, coins)
    db.add_behavior(
        request.user_id,
        "on_time_payment",
        verified=True,
        source="event_rule_engine",
        data=json.dumps(metadata, sort_keys=True),
    )
    transaction_id = db.add_coin_transaction(
        request.user_id,
        coins,
        "on_time_payment",
        f"Verified on-time payment - awarded {coins} coins and {spins} spins",
    )
    db.grant_game_entitlement(request.user_id, "spin", request.event_type, spins)
    event_id = db.add_financial_event(
        request.user_id,
        request.event_type,
        "rewarded",
        coins,
        spins,
        json.dumps(metadata, sort_keys=True),
    )
    db.add_notification(
        request.user_id,
        "push",
        "You earned 2 spins for paying on time",
        "Your on-time payment unlocked coins and 2 spins.",
        "/z-world",
    )

    updated_user = db.get_user(request.user_id)
    verified_count = db.count_verified_behaviors(request.user_id)
    new_tier = maybe_record_tier_change(
        db,
        request.user_id,
        user["tier"],
        updated_user["coin_balance"],
        verified_count,
    )

    return {
        "success": True,
        "event_id": event_id,
        "transaction_id": transaction_id,
        "eligible": True,
        "coins_awarded": coins,
        "spins_unlocked": spins,
        "new_balance": updated_user["coin_balance"],
        "new_tier": new_tier,
        "notification": _latest_notification(request.user_id),
        "dashboard": await get_z_world_dashboard(request.user_id),
    }
