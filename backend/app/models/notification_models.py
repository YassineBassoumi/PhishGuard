"""
Notification database models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Security alerts (cannot be disabled)
    dangerous_email_alerts = Column(Boolean, default=True, nullable=False)
    
    # Account activity alerts
    new_login_alerts = Column(Boolean, default=True, nullable=False)
    password_change_alerts = Column(Boolean, default=True, nullable=False)
    two_factor_change_alerts = Column(Boolean, default=True, nullable=False)
    
    # General settings
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    notification_email = Column(String(255), nullable=True)  # Optional: different email for notifications
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id}, enabled={self.email_notifications_enabled})>"


class NotificationHistory(Base):
    """History of sent notifications"""
    __tablename__ = "notification_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default='sent', nullable=False)  # sent, failed, pending
    error_message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<NotificationHistory(user_id={self.user_id}, type={self.notification_type}, status={self.status})>"
