"""Pydantic models for request/response validation."""

from typing import Optional, Dict, Any, Literal
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
        v = v.replace(" Bank", "")
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


class ZWorldOnboardingRequest(BaseModel):
    """Request to complete the forced first-time Z-World onboarding."""
    user_id: int = Field(..., gt=0)
    club_action: Literal["create", "join"] = "create"
    club_name: Optional[str] = Field(default=None, max_length=80)
    invite_code: Optional[str] = Field(default=None, max_length=32)
    accepted_coin_rules: bool

    @model_validator(mode="after")
    def validate_club_choice(self) -> "ZWorldOnboardingRequest":
        if not self.accepted_coin_rules:
            raise ValueError("accepted_coin_rules must be true")
        if self.club_action == "create" and not self.club_name:
            raise ValueError("club_name is required when club_action is create")
        if self.club_action == "join" and not self.invite_code:
            raise ValueError("invite_code is required when club_action is join")
        return self


class FinancialEventRequest(BaseModel):
    """Request to process a financial behavior event through the reward engine."""
    user_id: int = Field(..., gt=0)
    event_type: str = Field(..., min_length=1, max_length=80)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AdStartRequest(BaseModel):
    """Request to start watching an ad."""
    user_id: int = Field(..., gt=0)
    ad_id: str = Field(..., min_length=1)


class AdCompleteRequest(BaseModel):
    """Request to complete watching an ad."""
    user_id: int = Field(..., gt=0)
    ad_view_id: int = Field(..., gt=0)


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
    withdrawable_balance: int = 0
    ecosystem_balance: int = 0
    tier: str


class SpendingActionRequest(BaseModel):
    """Request to spend coins on an ecosystem sink."""
    user_id: int = Field(..., gt=0)
    item_id: int = Field(..., gt=0)


class BankLinkResponse(BaseModel):
    """Response for bank linking."""
    success: bool = True
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
    cost_paid: int = 0
    used_earned_spin: bool = False
    spins_remaining: int = 0


class ErrorResponse(BaseModel):
    """Response for errors."""
    error: str
    detail: Optional[str] = None
    status_code: int
