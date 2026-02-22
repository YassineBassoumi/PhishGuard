"""
Audit log schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    action: str
    actor_id: Optional[int] = None
    actor_username: Optional[str] = None
    target_user_id: Optional[int] = None
    target_username: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogCreate(BaseModel):
    """Schema for creating audit log"""
    action: str
    actor_id: Optional[int] = None
    target_user_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
