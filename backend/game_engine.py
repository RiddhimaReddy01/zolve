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


def play_spin_wheel() -> Dict[str, Any]:
    """Play spin wheel game.

    Wheel has 6 segments with rewards: [50, 100, 200, 300, 500, 1000]

    Returns:
        dict with segment_number, coins_won, and message
    """
    segment = random.randint(1, 6)
    coins = SPIN_WHEEL_REWARDS[segment - 1]
    return {
        "segment_number": segment,
        "coins_won": coins,
        "message": f"You landed on Segment {segment}! Won {coins} coins! 🎉",
    }


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
    transactions = [
        {
            "date": "2024-01-15",
            "description": "Credit Card Payment",
            "amount": 5000,
            "due_date": "2024-01-20",
            "is_on_time": True,
            "status": "completed",
        },
        {
            "date": "2024-01-10",
            "description": "EMI Debit",
            "amount": 2000,
            "due_date": "2024-01-12",
            "is_on_time": True,
            "status": "completed",
        },
        {
            "date": "2024-01-05",
            "description": "Monthly Salary",
            "amount": 50000,
            "due_date": None,
            "is_on_time": True,
            "status": "completed",
        },
    ]

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
