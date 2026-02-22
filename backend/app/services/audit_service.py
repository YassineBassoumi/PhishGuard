"""
Audit logging service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from fastapi import Request
import logging

from app.models.audit_models import AuditLog, AuditAction

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging"""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        actor_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Log an admin action
        
        Args:
            db: Database session
            action: Action type (from AuditAction enum)
            actor_id: ID of user performing the action
            target_user_id: ID of user being affected (if applicable)
            details: Additional context (dict)
            request: FastAPI request object (for IP and user agent)
        
        Returns:
            Created AuditLog instance
        """
        try:
            # Extract IP and user agent from request
            ip_address = None
            user_agent = None
            
            if request:
                # Get real IP (considering proxies)
                ip_address = request.headers.get("X-Forwarded-For")
                if ip_address:
                    ip_address = ip_address.split(",")[0].strip()
                else:
                    ip_address = request.client.host if request.client else None
                
                user_agent = request.headers.get("User-Agent")
            
            # Create audit log entry
            audit_log = AuditLog(
                action=action,
                actor_id=actor_id,
                target_user_id=target_user_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(audit_log)
            await db.flush()
            
            logger.info(f"Audit log created: {action} by user {actor_id}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}", exc_info=True)
            # Don't raise - audit logging should not break the main operation
            return None
    
    @staticmethod
    async def log_user_role_change(
        db: AsyncSession,
        actor_id: int,
        target_user_id: int,
        old_role: str,
        new_role: str,
        request: Optional[Request] = None
    ):
        """Log user role change"""
        await AuditService.log_action(
            db=db,
            action=AuditAction.USER_ROLE_CHANGED.value,
            actor_id=actor_id,
            target_user_id=target_user_id,
            details={
                "old_role": old_role,
                "new_role": new_role
            },
            request=request
        )
    
    @staticmethod
    async def log_user_ban(
        db: AsyncSession,
        actor_id: int,
        target_user_id: int,
        reason: str,
        request: Optional[Request] = None
    ):
        """Log user ban"""
        await AuditService.log_action(
            db=db,
            action=AuditAction.USER_BANNED.value,
            actor_id=actor_id,
            target_user_id=target_user_id,
            details={"reason": reason},
            request=request
        )
    
    @staticmethod
    async def log_user_unban(
        db: AsyncSession,
        actor_id: int,
        target_user_id: int,
        request: Optional[Request] = None
    ):
        """Log user unban"""
        await AuditService.log_action(
            db=db,
            action=AuditAction.USER_UNBANNED.value,
            actor_id=actor_id,
            target_user_id=target_user_id,
            request=request
        )
    
    @staticmethod
    async def log_user_deletion(
        db: AsyncSession,
        actor_id: int,
        target_user_id: int,
        target_username: str,
        request: Optional[Request] = None
    ):
        """Log user deletion"""
        await AuditService.log_action(
            db=db,
            action=AuditAction.USER_DELETED.value,
            actor_id=actor_id,
            target_user_id=target_user_id,
            details={"username": target_username},
            request=request
        )


# Singleton instance
audit_service = AuditService()
