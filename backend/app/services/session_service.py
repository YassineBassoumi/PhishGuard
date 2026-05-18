"""
Session management service
Handles user session tracking and management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List


def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Force a datetime to be timezone-aware in UTC.

    The legacy code path stored values via `datetime.now(timezone.utc)` which produces a
    naive datetime. When such a value is serialized by Pydantic it is emitted
    without a `Z`/offset, and the browser then interprets it as **local time**.
    For a UTC+01 user this caused `last_activity` to appear shifted by 1 hour.

    Treating any naive datetime as UTC here guarantees the JSON payload always
    carries an explicit offset, which `new Date(...)` parses correctly.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
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
            expires_at=datetime.now(timezone.utc) + expires_delta,
        )
        
        db.add(session)
        await db.flush()
        
        return session, jti
    
    @staticmethod
    async def is_known_device(
        db: AsyncSession,
        user_id: int,
        ip_address: str,
        user_agent: str,
        exclude_jti: Optional[str] = None
    ) -> bool:
        """
        Check whether the (user, ip_address, device_info) combination has been seen
        before for this user. Used to decide whether a "new login" alert is worth sending.

        Strategy:
            - We compare on (ip_address, device_info) — device_info is the parsed
              "Browser on OS" string, which is much more stable than the raw user_agent
              (the raw UA changes on every minor browser update and would defeat the check).
            - We exclude the current session's JTI so the freshly-created session does
              not falsely match itself.

        Returns:
            True  → device already seen for this user (skip the alert).
            False → never seen before, treat as a new device (send the alert).
        """
        device_info = SessionService.extract_device_info(user_agent)

        query = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.ip_address == ip_address,
            UserSession.device_info == device_info,
        )
        if exclude_jti:
            query = query.where(UserSession.token_jti != exclude_jti)

        result = await db.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

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
                UserSession.expires_at > datetime.now(timezone.utc)
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
                # Force UTC tz-info so the JSON includes an explicit offset and
                # the browser does NOT interpret it as local time.
                "last_activity": _as_utc(session.last_activity),
                "created_at": _as_utc(session.created_at),
                "expires_at": _as_utc(session.expires_at),
            }
            session_list.append(session_dict)
        
        return session_list
    
    @staticmethod
    async def revoke_session(
        db: AsyncSession,
        session_id: int,
        user_id: int,
        current_jti: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Revoke a specific session.

        Returns:
            (success, error_code):
                success=True  → session was revoked
                success=False → error_code in {"not_found", "current_session"}
        """
        result = await db.execute(
            select(UserSession)
            .where(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            return False, "not_found"

        # Refuse to revoke the caller's own current session via this endpoint.
        # The dedicated logout endpoint must be used instead, so the API
        # does not invalidate the very token making the request.
        if current_jti and session.token_jti == current_jti:
            return False, "current_session"

        session.is_active = False
        await db.flush()
        return True, None

    @staticmethod
    async def revoke_session_by_jti(
        db: AsyncSession,
        jti: str,
        user_id: int
    ) -> bool:
        """
        Revoke a session identified by its JWT ID (used by /auth/logout).
        Returns True if a matching active session was found and revoked.
        """
        result = await db.execute(
            select(UserSession)
            .where(
                UserSession.token_jti == jti,
                UserSession.user_id == user_id,
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
                UserSession.expires_at > datetime.now(timezone.utc)
            )
        )
        session = result.scalar_one_or_none()
        return session is not None
    
    @staticmethod
    async def update_session_activity(
        db: AsyncSession,
        jti: str
    ) -> None:
        """
        Update last activity timestamp for a session
        
        Note: Uses a direct UPDATE query instead of ORM for better performance
        and to avoid timeout issues on slow database connections.
        """
        try:
            # Direct UPDATE query - much faster than loading object and flushing
            await db.execute(
                update(UserSession)
                .where(UserSession.token_jti == jti)
                .values(last_activity=datetime.now(timezone.utc))
            )
            # Don't flush here - let the request handler commit at the end
            # This prevents blocking on every request
        except Exception as e:
            # Log but don't fail the request if session update fails
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to update session activity for {jti}: {str(e)}"
            )
    
    @staticmethod
    async def cleanup_expired_sessions(db: AsyncSession) -> int:
        """Clean up expired sessions"""
        result = await db.execute(
            delete(UserSession)
            .where(UserSession.expires_at < datetime.now(timezone.utc))
        )
        return result.rowcount


# Singleton instance
session_service = SessionService()
