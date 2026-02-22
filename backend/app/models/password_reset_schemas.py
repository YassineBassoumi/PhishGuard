"""
Password reset Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=72)
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "new_password": "newSecurePassword123"
            }
        }


class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password reset email sent successfully"
            }
        }
