"""
Email Provider Management Schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmailProviderConnectionResponse(BaseModel):
    """Schema for email provider connection response"""
    id: int
    user_id: int
    username: str
    email: str
    provider: str
    email_address: Optional[str] = None
    token_expiry: Optional[datetime] = None
    is_expired: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmailProviderStatsResponse(BaseModel):
    """Schema for email provider statistics"""
    total_connections: int
    connections_by_provider: dict
    active_connections: int
    expired_connections: int
    users_with_connections: int
    recent_connections_24h: int
