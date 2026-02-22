"""
Password reset service
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.password_reset_models import PasswordResetToken
from app.models.user_models import User
from app.services.email_service import email_service


class PasswordResetService:
    """Password reset service"""
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def create_reset_token(
        db: AsyncSession,
        user: User,
        expires_in_hours: int = 1
    ) -> str:
        """
        Create a password reset token for a user
        
        Args:
            db: Database session
            user: User object
            expires_in_hours: Token expiration time in hours
        
        Returns:
            str: Reset token
        """
        # Generate token
        token = PasswordResetService.generate_reset_token()
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        # Create token record
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(reset_token)
        await db.flush()
        
        return token
    
    @staticmethod
    async def verify_reset_token(
        db: AsyncSession,
        token: str
    ) -> Optional[User]:
        """
        Verify a reset token and return the associated user
        
        Args:
            db: Database session
            token: Reset token
        
        Returns:
            User object if token is valid, None otherwise
        """
        # Find token
        result = await db.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token == token,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        )
        reset_token = result.scalar_one_or_none()
        
        if not reset_token:
            return None
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == reset_token.user_id)
        )
        user = result.scalar_one_or_none()
        
        return user
    
    @staticmethod
    async def mark_token_as_used(
        db: AsyncSession,
        token: str
    ) -> bool:
        """
        Mark a reset token as used
        
        Args:
            db: Database session
            token: Reset token
        
        Returns:
            bool: True if token was marked as used
        """
        result = await db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.token == token)
        )
        reset_token = result.scalar_one_or_none()
        
        if not reset_token:
            return False
        
        reset_token.is_used = True
        await db.flush()
        
        return True
    
    @staticmethod
    async def invalidate_user_tokens(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """
        Invalidate all reset tokens for a user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            int: Number of tokens invalidated
        """
        result = await db.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.is_used == False
            )
        )
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.is_used = True
            count += 1
        
        await db.flush()
        return count
    
    @staticmethod
    async def cleanup_expired_tokens(db: AsyncSession) -> int:
        """
        Clean up expired tokens
        
        Args:
            db: Database session
        
        Returns:
            int: Number of tokens deleted
        """
        result = await db.execute(
            delete(PasswordResetToken)
            .where(PasswordResetToken.expires_at < datetime.utcnow())
        )
        return result.rowcount
    
    @staticmethod
    async def send_reset_email(
        user: User,
        token: str,
        frontend_url: str = "http://localhost:5173"
    ) -> bool:
        """
        Send password reset email to user
        
        Args:
            user: User object
            token: Reset token
            frontend_url: Frontend application URL
        
        Returns:
            bool: True if email sent successfully
        """
        return await email_service.send_password_reset_email(
            to_email=user.email,
            username=user.username,
            reset_token=token,
            frontend_url=frontend_url
        )


# Singleton instance
password_reset_service = PasswordResetService()
