"""
Email verification Pydantic schemas
"""

from pydantic import BaseModel, EmailStr


class EmailVerificationRequest(BaseModel):
    """Request to resend verification email"""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Confirm email verification with token"""
    token: str


class EmailVerificationResponse(BaseModel):
    """Response for email verification operations"""
    message: str
