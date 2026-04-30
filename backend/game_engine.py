"""Game engine: coin logic, tier calculation, behavior verification."""

import random
import json
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from constants import (
    EARNING_WEIGHTS,
    TIER_THRESHOLDS,
    DAILY_EARNING_CAPS,
    SCRATCH_CARD_PROBABILITIES,
    SCRATCH_CARD_REWARDS,
    SPIN_WHEEL_REWARDS,
    MIN_CREDIT_SCORE,
    MAX_CREDIT_SCORE,
)
from exceptions import InvalidActionError, InsufficientCoinsError, DailyCoinCapError


def calculate_coins_for_action(action_type: str) -> int:
    """Calculate coins earned for an action.

    Args:
        action_type: Type of earning action (e.g., 'on_time_payment')

    Returns:
        Number of coins earned

    Raises:
        InvalidActionError: If action type is invalid
    """
    if action_type not in EARNING_WEIGHTS:
        raise InvalidActionError(f"Unknown action type: {action_type}")
    return EARNING_WEIGHTS[action_type]


def calculate_user_tier(coin_balance: int, verified_behavior_count: int) -> str:
    """Calculate user tier based on coins and verified behaviors.

    Tier progression:
    - Basic: 0-999 coins
    - Silver: 1000+ coins AND 2+ verified behaviors
    - Gold: 3000+ coins AND 5+ verified behaviors

    Args:
        coin_balance: Current coin balance
        verified_behavior_count: Number of verified behaviors

    Returns:
        Tier name (Basic, Silver, or Gold)
    """
    thresholds = TIER_THRESHOLDS

    if (coin_balance >= thresholds["Gold"]["min_coins"] and
            verified_behavior_count >= thresholds["Gold"]["min_behaviors"]):
        return "Gold"

    if (coin_balance >= thresholds["Silver"]["min_coins"] and
            verified_behavior_count >= thresholds["Silver"]["min_behaviors"]):
        return "Silver"

    return "Basic"


def maybe_record_tier_change(db, user_id: int, old_tier: str, coin_balance: int, verified_count: int) -> str:
    """Check if user tier has changed and record the event if so.

    Args:
        db: Database instance
        user_id: User ID
        old_tier: Previous tier before any new coins/behaviors
        coin_balance: Current coin balance
        verified_count: Current verified behavior count

    Returns:
        New tier name (Basic, Silver, or Gold)
    """
    new_tier = calculate_user_tier(coin_balance, verified_count)
    if new_tier != old_tier:
        db.update_user_tier(user_id, new_tier)
        db.add_tier_event(user_id, old_tier, new_tier, coin_balance, verified_count)
    return new_tier


def play_scratch_card() -> Dict[str, Any]:
    """Play scratch card game.

    Probabilities:
    - 40% try_again (0 coins)
    - 35% small_win (50 coins)
    - 20% medium_win (150 coins)
    - 5% jackpot (500 coins)

    Returns:
        dict with result, coins_won, and message
    """
    rand = random.random()
    cumulative = 0.0

    for result_type, probability in SCRATCH_CARD_PROBABILITIES.items():
        cumulative += probability
        if rand < cumulative:
            coins = SCRATCH_CARD_REWARDS[result_type]
            return {
                "result": result_type,
                "coins_won": coins,
                "message": _get_scratch_card_message(result_type, coins),
            }

    return {
        "result": "try_again",
        "coins_won": 0,
        "message": "Better luck next time! 🍀",
    }


def play_spin_wheel_for_user(verified_behavior_count: int) -> Dict[str, Any]:
    """Play spin wheel game with behavior-based probability boost.

    Base weights: [30, 25, 20, 15, 7, 3] for segments [1-6]
    For each verified behavior (capped at 5), shift 3 weight from segments 1,2 to 5,6.
    Wheel rewards: [50, 100, 200, 300, 500, 1000]

    Args:
        verified_behavior_count: Number of verified behaviors for the user

    Returns:
        dict with segment_number, coins_won, and message
    """
    BASE_WEIGHTS = [30, 25, 20, 15, 7, 3]
    weights = BASE_WEIGHTS.copy()

    # Apply behavior-based boost: shift weight from low to high segments
    boosts = min(verified_behavior_count, 5)
    for _ in range(boosts):
        # Shift 3 weight from segments 1,2 (indices 0,1) to segments 5,6 (indices 4,5)
        shift = min(3, weights[0], weights[1])
        weights[0] -= shift
        weights[1] -= shift
        weights[4] += shift
        weights[5] += shift

    # Use random.choices to select segment based on adjusted weights
    segment = random.choices(range(1, 7), weights=weights, k=1)[0]
    coins_won = SPIN_WHEEL_REWARDS[segment - 1]
    return {
        "segment_number": segment,
        "coins_won": coins_won,
        "message": f"You landed on Segment {segment}! Won {coins_won} coins! 🎉",
    }


def play_spin_wheel() -> Dict[str, Any]:
    """Play spin wheel game (legacy, no behavior boost).

    Wheel has 6 segments with rewards: [50, 100, 200, 300, 500, 1000]

    Returns:
        dict with segment_number, coins_won, and message
    """
    return play_spin_wheel_for_user(0)


def _get_scratch_card_message(result_type: str, coins: int) -> str:
    """Get user-friendly message for scratch card result."""
    messages = {
        "try_again": "Better luck next time! 🍀",
        "small_win": f"Small win! {coins} coins 🎁",
        "medium_win": f"Nice hit! {coins} coins 🌟",
        "jackpot": f"🏆 JACKPOT! {coins} coins! 🏆",
    }
    return messages.get(result_type, "Try again!")


def verify_bank_behavior(bank_name: str, account_number: str) -> List[Dict[str, Any]]:
    """Simulate bank API call to fetch and verify behaviors.

    For demo purposes, returns mock transaction data that demonstrates:
    - On-time payments detected
    - Credit score changes detected
    - Direct deposits identified

    Args:
        bank_name: Name of bank (HDFC, ICICI, Axis)
        account_number: Account number (simulated)

    Returns:
        List of verified behaviors with coins awarded
    """
    verified_behaviors = []

    # Mock transaction data
    mock_data = _generate_mock_bank_data(bank_name, account_number)

    # Detect on-time payments
    for txn in mock_data["transactions"]:
        if txn["is_on_time"] and txn["status"] == "completed":
            verified_behaviors.append({
                "behavior_type": "on_time_payment",
                "coins": EARNING_WEIGHTS["on_time_payment"],
                "details": {
                    "date": txn["date"],
                    "amount": txn["amount"],
                    "due_date": txn["due_date"],
                },
                "source": "bank_api",
            })

    # Detect direct deposits
    for txn in mock_data["transactions"]:
        if "salary" in txn["description"].lower() or "deposit" in txn["description"].lower():
            verified_behaviors.append({
                "behavior_type": "direct_deposit",
                "coins": EARNING_WEIGHTS["direct_deposit"],
                "details": {
                    "date": txn["date"],
                    "amount": txn["amount"],
                },
                "source": "bank_api",
            })

    return verified_behaviors


def verify_credit_score(previous_score: int, current_score: int) -> Dict[str, Any]:
    """Verify credit score improvement.

    Args:
        previous_score: Previous credit score
        current_score: Current credit score

    Returns:
        dict with behavior data if improved, empty dict otherwise
    """
    if current_score > previous_score:
        return {
            "behavior_type": "credit_score_up",
            "coins": EARNING_WEIGHTS["credit_score_up"],
            "details": {
                "previous_score": previous_score,
                "current_score": current_score,
                "improvement": current_score - previous_score,
            },
            "source": "credit_bureau_api",
        }
    return {}


def check_daily_earning_cap(user_id: int, action_type: str, last_earned_today: List[Dict]) -> bool:
    """Check if user has exceeded daily earning cap for this action.

    Args:
        user_id: User ID
        action_type: Type of action (e.g., 'daily_checkin')
        last_earned_today: List of transactions from today

    Returns:
        True if user can earn, False if cap reached

    Raises:
        DailyCoinCapError: If cap is exceeded
    """
    if action_type not in DAILY_EARNING_CAPS:
        return True

    cap = DAILY_EARNING_CAPS[action_type]
    coins_earned_today = sum(t["amount"] for t in last_earned_today if t["event_type"] == action_type)

    if coins_earned_today >= cap:
        raise DailyCoinCapError(
            f"Daily earning cap of {cap} coins reached for {action_type}"
        )
    return True


def _generate_mock_bank_data(bank_name: str, account_number: str) -> Dict[str, Any]:
    """Generate mock bank transaction data for demo.

    Args:
        bank_name: Bank name (HDFC, ICICI, Axis)
        account_number: Account number

    Returns:
        Mock bank data with transactions
    """
    templates = [
        ("Credit Card Payment", 5200, True, True),
        ("Rent Payment", 18500, True, True),
        ("EMI Debit", 3100, True, True),
        ("Monthly Salary Deposit", 78000, False, True),
        ("Mutual Fund SIP", 5000, True, True),
        ("Grocery Spend", 2400, False, False),
        ("Utility Bill Payment", 1800, True, True),
        ("UPI Transfer", 900, False, False),
        ("Emergency Fund Deposit", 6000, False, True),
    ]
    transactions = []
    for i in range(150):
        description, amount, has_due_date, is_on_time = templates[i % len(templates)]
        month = 1 + (i // 28)
        day = 1 + (i % 28)
        due_day = min(day + 4, 28)
        transactions.append({
            "date": f"2026-{month:02d}-{day:02d}",
            "description": description,
            "amount": amount,
            "due_date": f"2026-{month:02d}-{due_day:02d}" if has_due_date else None,
            "is_on_time": is_on_time,
            "status": "completed",
        })

    return {
        "account_id": f"{bank_name}_{account_number}",
        "bank_name": bank_name,
        "account_number": account_number,
        "transactions": transactions,
    }


def generate_mock_credit_score() -> Tuple[int, int]:
    """Generate mock credit score data.

    Returns:
        Tuple of (previous_score, current_score)
    """
    previous_score = random.randint(MIN_CREDIT_SCORE + 100, MAX_CREDIT_SCORE - 100)
    improvement = random.randint(10, 50)
    current_score = min(previous_score + improvement, MAX_CREDIT_SCORE)
    return previous_score, current_score


def calculate_tier_progress(coin_balance: int, verified_count: int) -> Dict[str, Any]:
    """Calculate progress toward next tier.

    Args:
        coin_balance: Current coins
        verified_count: Number of verified behaviors

    Returns:
        dict with current tier, next tier, coins needed, behaviors needed
    """
    current_tier = calculate_user_tier(coin_balance, verified_count)
    thresholds = TIER_THRESHOLDS

    tier_order = ["Basic", "Silver", "Gold"]
    current_idx = tier_order.index(current_tier)

    if current_idx == 2:  # Already Gold
        return {
            "current_tier": "Gold",
            "next_tier": None,
            "coins_needed": 0,
            "behaviors_needed": 0,
            "progress_pct": 100,
        }

    next_tier = tier_order[current_idx + 1]
    next_threshold = thresholds[next_tier]

    coins_needed = max(0, next_threshold["min_coins"] - coin_balance)
    behaviors_needed = max(0, next_threshold["min_behaviors"] - verified_count)

    return {
        "current_tier": current_tier,
        "next_tier": next_tier,
        "coins_needed": coins_needed,
        "behaviors_needed": behaviors_needed,
        "progress_pct": int((coin_balance / next_threshold["min_coins"]) * 100)
        if next_threshold["min_coins"] > 0
        else 100,
    }
