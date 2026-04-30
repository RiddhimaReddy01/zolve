"""Bank linking and behavior verification endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from models import BankLinkRequest, BankLinkResponse, VerificationResponse
from database import Database
from game_engine import verify_bank_behavior, verify_credit_score, generate_mock_credit_score, calculate_user_tier, maybe_record_tier_change
from exceptions import BankVerificationError, UserNotFoundError

router = APIRouter(prefix="/api/bank", tags=["bank"])
db = Database()


@router.post("/link", response_model=BankLinkResponse)
async def link_bank_account(request: BankLinkRequest) -> BankLinkResponse:
    """Link a bank account for a user.

    Simulates OAuth flow and returns authorization link.

    Args:
        request: BankLinkRequest with user_id, bank_name, account_number

    Returns:
        BankLinkResponse with account_id and status
    """
    try:
        # Validate user exists
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Generate account ID (simulated)
        account_id = f"{request.bank_name}_{request.account_number}_{request.user_id}"

        # Link account in database
        db.link_bank_account(
            request.user_id,
            request.bank_name,
            request.account_number,
            account_id,
        )

        return BankLinkResponse(
            user_id=request.user_id,
            account_id=account_id,
            bank_name=request.bank_name,
            status="linked",
            linked_at=str(__import__("datetime").datetime.now()),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/transactions/{user_id}", response_model=List[Dict[str, Any]])
async def get_bank_transactions(user_id: int) -> List[Dict[str, Any]]:
    """Get bank transactions for a user.

    Returns simulated transaction data from linked accounts.

    Args:
        user_id: User ID

    Returns:
        List of bank transactions
    """
    try:
        # Get linked accounts
        accounts = db.get_linked_accounts(user_id)
        if not accounts:
            return []

        # Return mock transactions
        all_transactions = []
        for account in accounts:
            mock_data = _get_mock_transactions(account["bank_name"], account["account_number"])
            all_transactions.extend(mock_data)

        return all_transactions

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/verify-behaviors/{user_id}", response_model=List[VerificationResponse])
async def verify_behaviors(user_id: int) -> List[VerificationResponse]:
    """Verify and award coins for financial behaviors.

    Fetches bank data and credit score, detects verified behaviors, awards coins.

    Args:
        user_id: User ID

    Returns:
        List of verified behaviors with coins awarded
    """
    try:
        # Validate user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        verified_behaviors = []

        # Get linked accounts
        accounts = db.get_linked_accounts(user_id)

        # For each account, verify behaviors
        for account in accounts:
            bank_behaviors = verify_bank_behavior(account["bank_name"], account["account_number"])

            for behavior in bank_behaviors:
                # Check if already awarded (avoid duplicates)
                existing = db.get_verified_behaviors(user_id)
                if not _is_duplicate_behavior(behavior, existing):
                    # Award coins
                    db.update_user_balance(user_id, behavior["coins"])
                    db.update_withdrawable_balance(user_id, behavior["coins"])

                    # Log behavior
                    import json
                    db.add_behavior(
                        user_id,
                        behavior["behavior_type"],
                        verified=True,
                        source=behavior["source"],
                        data=json.dumps(behavior["details"]),
                    )

                    # Log transaction
                    db.add_coin_transaction(
                        user_id,
                        behavior["coins"],
                        behavior["behavior_type"],
                        f"Verified {behavior['behavior_type']} - awarded {behavior['coins']} coins",
                    )

                    verified_behaviors.append(
                        VerificationResponse(
                            behavior_type=behavior["behavior_type"],
                            verified=True,
                            verification_source=behavior["source"],
                            coins_awarded=behavior["coins"],
                            details=behavior["details"],
                        )
                    )

        # Check credit score improvement
        prev_score, curr_score = generate_mock_credit_score()
        credit_behavior = verify_credit_score(user["credit_score"], curr_score)

        if credit_behavior:
            # Update credit score
            db.update_user_balance(user_id, credit_behavior["coins"])
            db.update_withdrawable_balance(user_id, credit_behavior["coins"])

            import json
            db.add_behavior(
                user_id,
                credit_behavior["behavior_type"],
                verified=True,
                source=credit_behavior["source"],
                data=json.dumps(credit_behavior["details"]),
            )

            db.add_coin_transaction(
                user_id,
                credit_behavior["coins"],
                credit_behavior["behavior_type"],
                f"Credit score improved - awarded {credit_behavior['coins']} coins",
            )

            verified_behaviors.append(
                VerificationResponse(
                    behavior_type=credit_behavior["behavior_type"],
                    verified=True,
                    verification_source=credit_behavior["source"],
                    coins_awarded=credit_behavior["coins"],
                    details=credit_behavior["details"],
                )
            )

        updated_user = db.get_user(user_id)
        verified_count = db.count_verified_behaviors(user_id)
        maybe_record_tier_change(
            db,
            user_id,
            updated_user["tier"],
            updated_user["coin_balance"],
            verified_count,
        )

        return verified_behaviors

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/credit-score/{user_id}", response_model=Dict[str, Any])
async def get_credit_score(user_id: int) -> Dict[str, Any]:
    """Get current and previous credit score for a user.

    Args:
        user_id: User ID

    Returns:
        dict with current_score, previous_score, improvement
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Generate simulated score
        prev_score, curr_score = generate_mock_credit_score()
        improvement = curr_score - user["credit_score"]

        return {
            "user_id": user_id,
            "previous_score": user["credit_score"],
            "current_score": curr_score,
            "improvement": improvement,
            "improved": improvement > 0,
            "coins_available": 400 if improvement > 0 else 0,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def _get_mock_transactions(bank_name: str, account_number: str) -> List[Dict[str, Any]]:
    """Get mock bank transactions."""
    descriptions = [
        ("Credit Card Payment", -5200, True),
        ("Rent Payment", -18500, True),
        ("EMI Debit", -3100, True),
        ("Monthly Salary Deposit", 78000, True),
        ("Mutual Fund SIP", -5000, True),
        ("Grocery Spend", -2400, False),
        ("Utility Bill Payment", -1800, True),
        ("UPI Transfer", -900, False),
        ("Emergency Fund Transfer", -6000, True),
    ]
    transactions = []
    for i in range(150):
        description, amount, is_behavior = descriptions[i % len(descriptions)]
        month = 1 + (i // 28)
        day = 1 + (i % 28)
        due_day = min(day + 4, 28)
        transactions.append({
            "date": f"2026-{month:02d}-{day:02d}",
            "description": description,
            "amount": abs(amount),
            "due_date": f"2026-{month:02d}-{due_day:02d}" if amount < 0 else None,
            "is_on_time": is_behavior,
            "status": "completed",
            "bank_name": bank_name,
            "account_number_last4": account_number[-4:],
        })
    return transactions


def _is_duplicate_behavior(behavior: Dict[str, Any], existing: List[Dict[str, Any]]) -> bool:
    """Check if behavior already exists (avoid double-awarding)."""
    import json

    behavior_data = json.dumps(behavior["details"], sort_keys=True)
    for existing_b in existing:
        if (
            existing_b["behavior_type"] == behavior["behavior_type"]
            and existing_b["behavior_data"] == behavior_data
        ):
            return True
    return False
