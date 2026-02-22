"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=72)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str
    totp_code: Optional[str] = None  # 2FA code if enabled
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123",
                "totp_code": "123456"
            }
        }


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    is_superuser: bool
    is_banned: bool
    banned_at: Optional[datetime] = None
    ban_reason: Optional[str] = None
    last_login: Optional[datetime] = None
    two_factor_enabled: bool = False
    profile_picture: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_first_login: bool = False
    suggested_provider: Optional[str] = None  # gmail, outlook, etc.


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for user update"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    old_password: Optional[str] = None  # Required when changing password
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "John Updated Doe",
                "old_password": "currentpassword123",
                "password": "newsecurepassword123"
            }
        }


class UserRoleUpdate(BaseModel):
    """Schema for updating user role (SuperAdmin only)"""
    role: UserRole
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "admin"
            }
        }


class UserBanRequest(BaseModel):
    """Schema for banning a user"""
    reason: str = Field(..., min_length=1, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Violation of terms of service"
            }
        }



class TwoFactorSetupResponse(BaseModel):
    """Schema for 2FA setup response"""
    secret: str
    qr_code: str
    backup_codes: list[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KG...",
                "backup_codes": ["ABCD-1234", "EFGH-5678"]
            }
        }


class TwoFactorVerifyRequest(BaseModel):
    """Schema for verifying 2FA token"""
    token: str = Field(..., min_length=6, max_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class TwoFactorDisableRequest(BaseModel):
    """Schema for disabling 2FA"""
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "your_current_password"
            }
        }


class TwoFactorStatusResponse(BaseModel):
    """Schema for 2FA status"""
    enabled: bool
    backup_codes_remaining: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "backup_codes_remaining": 6
            }
        }


class AccountDeleteRequest(BaseModel):
    """Schema for account deletion request"""
    password: str
    confirmation: str = Field(..., pattern="^DELETE MY ACCOUNT$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "your_current_password",
                "confirmation": "DELETE MY ACCOUNT"
            }
        }


class RegistrationResponse(BaseModel):
    """Schema for registration response"""
    message: str
    email: str
    username: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Inscription réussie! Veuillez vérifier votre email pour activer votre compte.",
                "email": "user@example.com",
                "username": "johndoe"
            }
        }
