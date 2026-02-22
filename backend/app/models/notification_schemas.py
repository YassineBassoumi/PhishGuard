"""
Notification Pydantic schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class NotificationPreferenceBase(BaseModel):
    """Base notification preference schema"""
    dangerous_email_alerts: bool = True
    new_login_alerts: bool = True
    password_change_alerts: bool = True
    two_factor_change_alerts: bool = True
    email_notifications_enabled: bool = True
    notification_email: Optional[EmailStr] = None


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences"""
    user_id: int


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences"""
    new_login_alerts: Optional[bool] = None
    password_change_alerts: Optional[bool] = None
    two_factor_change_alerts: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    notification_email: Optional[EmailStr] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for notification preference response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationHistoryResponse(BaseModel):
    """Schema for notification history response"""
    id: int
    user_id: int
    notification_type: str
    subject: str
    sent_at: datetime
    status: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
