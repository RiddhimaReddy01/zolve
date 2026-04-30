#!/usr/bin/env python3
"""Integration test script - verifies backend and frontend are properly wired."""

import requests
import json
import sys
import os
from typing import Optional

# Fix encoding on Windows
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"
USER_ID = 1

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message: str, success: bool = True):
    """Print colored status message."""
    icon = f"{GREEN}[PASS]{RESET}" if success else f"{RED}[FAIL]{RESET}"
    print(f"{icon} {message}")


def print_header(title: str):
    """Print section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def test_health() -> bool:
    """Test backend health check."""
    print_header("1. Backend Health Check")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Backend is running: {data.get('service')}")
            return True
        else:
            print_status(f"Backend returned status {response.status_code}", False)
            return False
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to backend on localhost:8000", False)
        print(f"  Make sure backend is running: {YELLOW}cd backend && python main.py{RESET}")
        return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_user_data() -> bool:
    """Test getting user data."""
    print_header("2. Get User Data")
    try:
        response = requests.get(f"{API_BASE}/api/user/{USER_ID}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Retrieved user: {data['name']}")
            print(f"  - Email: {data['email']}")
            print(f"  - Balance: {data['balance']} coins")
            print(f"  - Tier: {data['tier']}")
            print(f"  - Credit Score: {data['credit_score']}")
            return True
        else:
            print_status(f"Failed to get user data: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_coin_balance() -> bool:
    """Test getting coin balance."""
    print_header("3. Get Coin Balance")
    try:
        response = requests.get(f"{API_BASE}/api/coins/balance/{USER_ID}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"User balance: {data['balance']} coins")
            print(f"  - Tier: {data['tier']}")
            return True
        else:
            print_status(f"Failed to get balance: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_products() -> bool:
    """Test getting products."""
    print_header("4. Get Marketplace Products")
    try:
        response = requests.get(f"{API_BASE}/api/zkart/products", timeout=5)
        if response.status_code == 200:
            products = response.json()
            print_status(f"Retrieved {len(products)} products")
            if products:
                first = products[0]
                print(f"  - Example: {first['name']}")
                print(f"    Category: {first['category']}")
                print(f"    Coins Required: {first['coins_required']}")
            return True
        else:
            print_status(f"Failed to get products: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_tier_progress() -> bool:
    """Test getting tier progress."""
    print_header("5. Get Tier Progress")
    try:
        response = requests.get(f"{API_BASE}/api/tier-progress/{USER_ID}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Current Tier: {data.get('current_tier', 'Unknown')}")
            if data.get('next_tier'):
                print(f"  - Next Tier: {data['next_tier']}")
                print(f"  - Progress: {data.get('progress_pct', 0)}%")
                print(f"  - Coins Needed: {data.get('coins_needed', 0)}")
                print(f"  - Behaviors Needed: {data.get('behaviors_needed', 0)}")
            else:
                print("  - Maximum tier reached!")
            return True
        else:
            print_status(f"Failed to get tier progress: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_coin_history() -> bool:
    """Test getting coin transaction history."""
    print_header("6. Get Coin Transaction History")
    try:
        response = requests.get(f"{API_BASE}/api/coins/history/{USER_ID}?limit=5", timeout=5)
        if response.status_code == 200:
            history = response.json()
            print_status(f"Retrieved {len(history)} transactions")
            for i, txn in enumerate(history[:3], 1):
                print(f"  {i}. {txn['event_type']}: {txn['amount']:+d} coins")
                print(f"     {txn['description']}")
            return True
        else:
            print_status(f"Failed to get history: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_verified_behaviors() -> bool:
    """Test getting verified behaviors."""
    print_header("7. Get Verified Behaviors")
    try:
        response = requests.get(f"{API_BASE}/api/verified-behaviors/{USER_ID}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('total_count', 0)
            print_status(f"User has {count} verified behaviors")
            if data.get('verified_behaviors'):
                for i, b in enumerate(data['verified_behaviors'][:2], 1):
                    print(f"  {i}. {b['behavior_type']}")
                    print(f"     Source: {b['verification_source']}")
            return True
        else:
            print_status(f"Failed to get behaviors: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_earn_coins() -> bool:
    """Test earning coins for an action."""
    print_header("8. Earn Coins (Test Action)")
    try:
        response = requests.post(
            f"{API_BASE}/api/coins/earn",
            json={"user_id": USER_ID, "action_type": "daily_checkin"},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_status(f"Earned {data['coins_earned']} coins")
                print(f"  - New Balance: {data['new_balance']} coins")
                print(f"  - New Tier: {data['new_tier']}")
                return True
            else:
                print_status(f"Failed: {data.get('detail', 'Unknown error')}", False)
                return False
        else:
            print_status(f"Failed with status {response.status_code}", False)
            if response.status_code == 429:
                print(f"  Note: Daily earning cap reached for this action")
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def test_games() -> bool:
    """Test game endpoints."""
    print_header("9. Test Games")
    try:
        # Test scratch card
        response = requests.post(
            f"{API_BASE}/api/games/scratch",
            json={"user_id": USER_ID},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            print_status(f"Played scratch card: {data['message']}")
            print(f"  - Result: {data['result']}")
            print(f"  - Coins Won: {data['coins_won']}")
            return True
        else:
            print_status(f"Scratch card failed: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False


def main():
    """Run all integration tests."""
    print(f"\n{BLUE}{'*'*60}")
    print(f"{'ZOLVE - Backend & Frontend Integration Test':^60}")
    print(f"{'*'*60}{RESET}\n")

    tests = [
        ("Health Check", test_health),
        ("User Data", test_user_data),
        ("Coin Balance", test_coin_balance),
        ("Products", test_products),
        ("Tier Progress", test_tier_progress),
        ("Coin History", test_coin_history),
        ("Verified Behaviors", test_verified_behaviors),
        ("Earn Coins", test_earn_coins),
        ("Games", test_games),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Tests interrupted by user{RESET}")
            break
        except Exception as e:
            print(f"{RED}Unexpected error in {test_name}: {e}{RESET}")
            results.append((test_name, False))

    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status_icon = f"{GREEN}[OK]{RESET}" if result else f"{RED}[NO]{RESET}"
        print(f"{status_icon} {test_name}")

    print(f"\n{BLUE}Results: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}All tests passed! Backend and frontend are properly wired.{RESET}")
        print(f"You can now start the frontend: {YELLOW}streamlit run frontend/app.py{RESET}\n")
        return 0
    else:
        print(f"\n{RED}❌ Some tests failed. Check the errors above.{RESET}")
        print(f"Make sure the backend is running: {YELLOW}cd backend && python main.py{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
