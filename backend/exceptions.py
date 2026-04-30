"""Custom exceptions for Zolve backend."""


class ZolveError(Exception):
    """Base exception for all Zolve-specific errors."""
    pass


class InsufficientCoinsError(ZolveError):
    """User does not have enough coins for the requested action."""
    pass


class DailyCoinCapError(ZolveError):
    """User has reached daily coin earning cap for this action."""
    pass


class BankVerificationError(ZolveError):
    """Error during bank account linking or verification."""
    pass


class TierError(ZolveError):
    """Error calculating or updating user tier."""
    pass


class ProductError(ZolveError):
    """Error with marketplace product."""
    pass


class UserNotFoundError(ZolveError):
    """User does not exist in database."""
    pass


class InvalidActionError(ZolveError):
    """Invalid earning action type."""
    pass
