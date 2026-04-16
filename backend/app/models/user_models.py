"""
User database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)  # Kept for backward compatibility
    is_banned = Column(Boolean, default=False, nullable=False)
    banned_at = Column(DateTime(timezone=True), nullable=True)
    banned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    ban_reason = Column(String(500), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Two-Factor Authentication fields
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(32), nullable=True)
    backup_codes = Column(String, nullable=True)  # JSON string of backup codes
    
    # First login tracking
    is_first_login = Column(Boolean, default=True, nullable=False)
    
    # Profile picture
    profile_picture = Column(String, nullable=True)  # Stores filename or URL
    
    # Relationship
    analyses = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username}, role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin or superadmin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    @property
    def is_super_admin(self) -> bool:
        """Check if user is superadmin"""
        return self.role == UserRole.SUPERADMIN
