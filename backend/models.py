"""Pydantic models for request/response validation."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from constants import BEHAVIOR_TYPES, MOCK_BANKS, MIN_CREDIT_SCORE, MAX_CREDIT_SCORE


class EarnRequest(BaseModel):
    """Request to earn coins via an action."""
    user_id: int = Field(..., gt=0, description="User ID")
    action_type: str = Field(..., description="Type of earning action")

    @field_validator("action_type")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in BEHAVIOR_TYPES:
            raise ValueError(f"Invalid action_type. Must be one of {BEHAVIOR_TYPES}")
        return v


class BankLinkRequest(BaseModel):
    """Request to link a bank account."""
    user_id: int = Field(..., gt=0)
    bank_name: str = Field(..., min_length=1)
    account_number: str = Field(..., min_length=1)

    @field_validator("bank_name")
    @classmethod
    def validate_bank(cls, v: str) -> str:
        if v not in MOCK_BANKS:
            raise ValueError(f"Bank must be one of {MOCK_BANKS}")
        return v


class PurchaseRequest(BaseModel):
    """Request to purchase a product with coins."""
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    coins_to_spend: int = Field(..., gt=0)


class ScratchCardRequest(BaseModel):
    """Request to play scratch card."""
    user_id: int = Field(..., gt=0)


class SpinWheelRequest(BaseModel):
    """Request to spin wheel."""
    user_id: int = Field(..., gt=0)


class CreditScoreUpdateRequest(BaseModel):
    """Request to update credit score."""
    user_id: int = Field(..., gt=0)
    new_score: int = Field(..., ge=MIN_CREDIT_SCORE, le=MAX_CREDIT_SCORE)


class SavingsGoalRequest(BaseModel):
    """Request to create or update a savings goal."""
    user_id: int = Field(..., gt=0)
    goal_name: str = Field(..., min_length=1, max_length=100)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_amounts(self) -> "SavingsGoalRequest":
        if self.current_amount > self.target_amount:
            raise ValueError("current_amount cannot exceed target_amount")
        return self


# Response models (not validated, for consistency)

class CoinTransactionResponse(BaseModel):
    """Response for a coin transaction."""
    transaction_id: int
    user_id: int
    amount: int
    event_type: str
    description: str
    created_at: str


class UserResponse(BaseModel):
    """Response with user profile."""
    user_id: int
    name: str
    email: str
    coin_balance: int
    tier: str
    credit_score: int
    created_at: str


class BalanceResponse(BaseModel):
    """Response with user balance."""
    user_id: int
    balance: int
    tier: str


class BankLinkResponse(BaseModel):
    """Response for bank linking."""
    user_id: int
    account_id: str
    bank_name: str
    status: str
    linked_at: str


class BankTransactionResponse(BaseModel):
    """Response with bank transaction data."""
    date: str
    description: str
    amount: float
    due_date: str
    is_on_time: bool
    status: str


class VerificationResponse(BaseModel):
    """Response with verified behavior."""
    behavior_type: str
    verified: bool
    verification_source: str
    coins_awarded: int
    details: Dict[str, Any]


class ScratchCardResponse(BaseModel):
    """Response from scratch card play."""
    result: str  # try_again, small_win, medium_win, jackpot
    coins_won: int
    message: str


class SpinWheelResponse(BaseModel):
    """Response from spin wheel."""
    segment_number: int
    coins_won: int
    message: str


class ErrorResponse(BaseModel):
    """Response for errors."""
    error: str
    detail: Optional[str] = None
    status_code: int
