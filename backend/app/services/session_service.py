"""
Session management service
Handles user session tracking and management
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import Request
import uuid
import re

from app.models.session_models import UserSession
from app.models.user_models import User


class SessionService:
    """Session management service"""
    
    @staticmethod
    def extract_device_info(user_agent: str) -> str:
        """Extract device information from user agent"""
        if not user_agent:
            return "Unknown Device"
        
        # Detect browser
        browser = "Unknown Browser"
        if "Chrome" in user_agent and "Edg" not in user_agent:
            browser = "Chrome"
        elif "Firefox" in user_agent:
            browser = "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            browser = "Safari"
        elif "Edg" in user_agent:
            browser = "Edge"
        elif "Opera" in user_agent or "OPR" in user_agent:
            browser = "Opera"
        
        # Detect OS
        os_name = "Unknown OS"
        if "Windows" in user_agent:
            os_name = "Windows"
        elif "Mac OS" in user_agent or "Macintosh" in user_agent:
            os_name = "macOS"
        elif "Linux" in user_agent:
            os_name = "Linux"
        elif "Android" in user_agent:
            os_name = "Android"
        elif "iOS" in user_agent or "iPhone" in user_agent or "iPad" in user_agent:
            os_name = "iOS"
        
        return f"{browser} on {os_name}"
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "Unknown"
    
    @staticmethod
    async def create_session(
        db: AsyncSession,
        user: User,
        request: Request,
        expires_delta: timedelta
    ) -> tuple[UserSession, str]:
        """Create a new session for user"""
        # Generate unique JWT ID
        jti = str(uuid.uuid4())
        
        # Extract request information
        user_agent = request.headers.get("User-Agent", "")
        device_info = SessionService.extract_device_info(user_agent)
        ip_address = SessionService.get_client_ip(request)
        
        # Create session
        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            location=None,  # Can be enhanced with IP geolocation service
            expires_at=datetime.utcnow() + expires_delta
        )
        
        db.add(session)
        await db.flush()
        
        return session, jti
    
    @staticmethod
    async def get_user_sessions(
        db: AsyncSession,
        user_id: int,
        current_jti: Optional[str] = None
    ) -> List[dict]:
        """Get all active sessions for a user"""
        result = await db.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
            .order_by(UserSession.last_activity.desc())
        )
        sessions = result.scalars().all()
        
        # Mark current session
        session_list = []
        for session in sessions:
            session_dict = {
                "id": session.id,
                "device_info": session.device_info,
                "ip_address": session.ip_address,
                "location": session.location,
                "is_current": session.token_jti == current_jti,
                "last_activity": session.last_activity,
                "created_at": session.created_at,
                "expires_at": session.expires_at
            }
            session_list.append(session_dict)
        
        return session_list
    
    @staticmethod
    async def revoke_session(
        db: AsyncSession,
        session_id: int,
        user_id: int
    ) -> bool:
        """Revoke a specific session"""
        result = await db.execute(
            select(UserSession)
            .where(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        session.is_active = False
        await db.flush()
        return True
    
    @staticmethod
    async def revoke_all_sessions(
        db: AsyncSession,
        user_id: int,
        except_jti: Optional[str] = None
    ) -> int:
        """Revoke all sessions for a user except the current one"""
        query = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        )
        
        if except_jti:
            query = query.where(UserSession.token_jti != except_jti)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        count = 0
        for session in sessions:
            session.is_active = False
            count += 1
        
        await db.flush()
        return count
    
    @staticmethod
    async def validate_session(
        db: AsyncSession,
        jti: str
    ) -> bool:
        """Validate if a session is still active"""
        result = await db.execute(
            select(UserSession)
            .where(
                UserSession.token_jti == jti,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        session = result.scalar_one_or_none()
        return session is not None
    
    @staticmethod
    async def update_session_activity(
        db: AsyncSession,
        jti: str
    ) -> None:
        """Update last activity timestamp for a session"""
        result = await db.execute(
            select(UserSession)
            .where(UserSession.token_jti == jti)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.last_activity = datetime.utcnow()
            await db.flush()
    
    @staticmethod
    async def cleanup_expired_sessions(db: AsyncSession) -> int:
        """Clean up expired sessions"""
        result = await db.execute(
            delete(UserSession)
            .where(UserSession.expires_at < datetime.utcnow())
        )
        return result.rowcount


# Singleton instance
session_service = SessionService()
