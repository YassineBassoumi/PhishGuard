"""
Session Pydantic schemas
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionResponse(BaseModel):
    """Session response schema"""
    id: int
    device_info: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]
    is_current: bool
    last_activity: datetime
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """List of sessions response"""
    sessions: list[SessionResponse]
    total: int


class RevokeSessionRequest(BaseModel):
    """Request to revoke a session"""
    session_id: int
