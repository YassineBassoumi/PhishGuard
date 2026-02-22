"""
Email Provider Models
Database models for multi-provider email support
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class EmailProvider(Base):
    """Email provider configuration"""
    __tablename__ = "email_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    oauth_authorize_url = Column(Text, nullable=False)
    oauth_token_url = Column(Text, nullable=False)
    api_base_url = Column(Text, nullable=False)
    scopes = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserEmailCredential(Base):
    """User email provider credentials"""
    __tablename__ = "user_email_credentials"
    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)
    email_address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
