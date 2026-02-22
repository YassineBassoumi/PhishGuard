"""
Audit log models for tracking admin actions
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AuditAction(str, enum.Enum):
    """Audit action types"""
    # User management
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    USER_BANNED = "USER_BANNED"
    USER_UNBANNED = "USER_UNBANNED"
    
    # Admin actions
    ADMIN_LOGIN = "ADMIN_LOGIN"
    ADMIN_VIEWED_USERS = "ADMIN_VIEWED_USERS"
    ADMIN_VIEWED_USER_DETAILS = "ADMIN_VIEWED_USER_DETAILS"
    ADMIN_VIEWED_USER_ACTIVITY = "ADMIN_VIEWED_USER_ACTIVITY"
    ADMIN_VIEWED_STATS = "ADMIN_VIEWED_STATS"
    ADMIN_VIEWED_AUDIT_LOGS = "ADMIN_VIEWED_AUDIT_LOGS"
    
    # Email provider management
    EMAIL_CONNECTION_REVOKED = "EMAIL_CONNECTION_REVOKED"
    
    # System actions
    SYSTEM_CONFIG_CHANGED = "SYSTEM_CONFIG_CHANGED"


class AuditLog(Base):
    """Audit log for tracking admin actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    details = Column(JSON, nullable=True)  # Additional context (old/new values, reason, etc.)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    actor = relationship("User", foreign_keys=[actor_id], backref="actions_performed")
    target_user = relationship("User", foreign_keys=[target_user_id], backref="actions_received")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor_id={self.actor_id})>"
