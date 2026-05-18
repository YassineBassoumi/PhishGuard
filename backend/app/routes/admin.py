"""
Admin routes
Handles user management and system administration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
import logging
from datetime import datetime, timezone

from app.models.auth_schemas import UserResponse, UserRoleUpdate, UserBanRequest
from app.models.user_models import User
from app.models.database_models import AnalysisHistory
from app.models.audit_models import AuditLog, AuditAction
from app.models.audit_schemas import AuditLogResponse
from app.utils.permissions import require_admin, require_superadmin
from app.services.audit_service import audit_service
from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users", tags=["Admin"])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users (Admin+ only)
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    try:
        # Get total count
        count_result = await db.execute(select(func.count(User.id)))
        total = count_result.scalar()
        
        # Get users
        result = await db.execute(
            select(User)
            .order_by(desc(User.created_at))
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()
        
        # Audit log
        await audit_service.log_action(
            db=db,
            action=AuditAction.ADMIN_VIEWED_USERS.value,
            actor_id=current_user.id,
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} listed users")
        
        return {
            "users": [UserResponse.model_validate(user) for user in users],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Admin"])
async def get_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details by ID (Admin+ only)
    
    - **user_id**: User ID to retrieve
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Audit log
        await audit_service.log_action(
            db=db,
            action=AuditAction.ADMIN_VIEWED_USER_DETAILS.value,
            actor_id=current_user.id,
            target_user_id=user.id,
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} viewed user {user.username}")
        
        return UserResponse.model_validate(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/users/{user_id}/role", response_model=UserResponse, tags=["Admin"])
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    request: Request,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user role (SuperAdmin only)
    
    - **user_id**: User ID to update
    - **role**: New role (user, admin, superadmin)
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-demotion
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        
        old_role = user.role
        user.role = role_update.role
        
        await db.commit()
        await db.refresh(user)
        
        # Log the action
        await audit_service.log_user_role_change(
            db=db,
            actor_id=current_user.id,
            target_user_id=user.id,
            old_role=old_role.value,
            new_role=role_update.role.value,
            request=request
        )
        await db.commit()
        
        logger.info(f"SuperAdmin {current_user.username} changed {user.username} role from {old_role} to {role_update.role}")
        
        return UserResponse.model_validate(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user (SuperAdmin only)
    
    - **user_id**: User ID to delete
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        username = user.username
        user_id_to_log = user.id
        
        # Log before deletion
        await audit_service.log_user_deletion(
            db=db,
            actor_id=current_user.id,
            target_user_id=user_id_to_log,
            target_username=username,
            request=request
        )
        await db.commit()
        
        # Expunge user from ORM session to avoid cascade issues
        db.expunge(user)
        
        # Use direct DELETE statements to avoid ORM cascade setting user_id=NULL
        # on NOT NULL columns (user_sessions, etc.)
        from sqlalchemy import delete as sql_delete
        from app.models.session_models import UserSession
        from app.models.email_provider_models import UserEmailCredential
        from app.models.database_models import AnalysisHistory
        from app.models.notification_models import NotificationPreference, NotificationHistory
        from app.models.password_reset_models import PasswordResetToken
        from app.models.email_verification_models import EmailVerificationToken
        
        await db.execute(sql_delete(UserSession).where(UserSession.user_id == user_id_to_log))
        await db.execute(sql_delete(UserEmailCredential).where(UserEmailCredential.user_id == user_id_to_log))
        await db.execute(sql_delete(AnalysisHistory).where(AnalysisHistory.user_id == user_id_to_log))
        await db.execute(sql_delete(NotificationHistory).where(NotificationHistory.user_id == user_id_to_log))
        await db.execute(sql_delete(NotificationPreference).where(NotificationPreference.user_id == user_id_to_log))
        await db.execute(sql_delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id_to_log))
        await db.execute(sql_delete(EmailVerificationToken).where(EmailVerificationToken.user_id == user_id_to_log))
        await db.execute(sql_delete(User).where(User.id == user_id_to_log))
        await db.commit()
        
        logger.info(f"SuperAdmin {current_user.username} deleted user {username}")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/stats", tags=["Admin"])
async def get_system_stats(
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system statistics (Admin+ only)
    
    Returns:
    - Total users count
    - Users by role
    - Total analyses count
    - Recent activity
    """
    try:
        # Total users
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()
        
        # Users by role
        users_by_role = {}
        for role in ["USER", "ADMIN", "SUPERADMIN"]:
            result = await db.execute(
                select(func.count(User.id)).where(User.role == role)
            )
            users_by_role[role] = result.scalar()
        
        # Total analyses
        total_analyses_result = await db.execute(select(func.count(AnalysisHistory.id)))
        total_analyses = total_analyses_result.scalar()
        
        # Active users (users with at least one analysis)
        active_users_result = await db.execute(
            select(func.count(func.distinct(AnalysisHistory.user_id)))
        )
        active_users = active_users_result.scalar()
        
        # Users logged in last 24 hours
        from datetime import datetime, timedelta
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_logins_result = await db.execute(
            select(func.count(User.id)).where(User.last_login >= yesterday)
        )
        recent_logins = recent_logins_result.scalar()
        
        # Users never logged in
        never_logged_in_result = await db.execute(
            select(func.count(User.id)).where(User.last_login.is_(None))
        )
        never_logged_in = never_logged_in_result.scalar()
        
        # Banned users count
        banned_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_banned == True)
        )
        banned_users = banned_users_result.scalar()
        
        # Audit log
        await audit_service.log_action(
            db=db,
            action=AuditAction.ADMIN_VIEWED_STATS.value,
            actor_id=current_user.id,
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} viewed system stats")
        
        return {
            "total_users": total_users,
            "users_by_role": users_by_role,
            "total_analyses": total_analyses,
            "active_users": active_users,
            "recent_logins_24h": recent_logins,
            "never_logged_in": never_logged_in,
            "banned_users": banned_users
        }
    
    except Exception as e:
        logger.error(f"Failed to get system stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )


@router.get("/users/{user_id}/activity", tags=["Admin"])
async def get_user_activity(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user activity details (Admin+ only)
    
    Returns:
    - Last login timestamp
    - Total analyses performed
    - Analyses by type (email/url)
    - Threat detection breakdown
    - Recent activity
    """
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Total analyses by this user
        total_analyses_result = await db.execute(
            select(func.count(AnalysisHistory.id)).where(AnalysisHistory.user_id == user_id)
        )
        total_analyses = total_analyses_result.scalar()
        
        # Analyses by type
        email_analyses_result = await db.execute(
            select(func.count(AnalysisHistory.id))
            .where(AnalysisHistory.user_id == user_id)
            .where(AnalysisHistory.analysis_type == "email")
        )
        email_analyses = email_analyses_result.scalar()
        
        url_analyses_result = await db.execute(
            select(func.count(AnalysisHistory.id))
            .where(AnalysisHistory.user_id == user_id)
            .where(AnalysisHistory.analysis_type == "url")
        )
        url_analyses = url_analyses_result.scalar()
        
        # Threat level breakdown
        threat_breakdown = {}
        for threat_level in ["safe", "suspicious", "dangerous"]:
            result = await db.execute(
                select(func.count(AnalysisHistory.id))
                .where(AnalysisHistory.user_id == user_id)
                .where(AnalysisHistory.threat_level == threat_level)
            )
            threat_breakdown[threat_level] = result.scalar()
        
        # Recent analyses (last 10)
        recent_analyses_result = await db.execute(
            select(AnalysisHistory)
            .where(AnalysisHistory.user_id == user_id)
            .order_by(desc(AnalysisHistory.created_at))
            .limit(10)
        )
        recent_analyses = recent_analyses_result.scalars().all()
        
        # Format recent analyses
        recent_activity = [
            {
                "id": analysis.id,
                "type": analysis.analysis_type,
                "threat_level": analysis.threat_level,
                "confidence": analysis.confidence,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None
            }
            for analysis in recent_analyses
        ]
        
        # Audit log
        await audit_service.log_action(
            db=db,
            action=AuditAction.ADMIN_VIEWED_USER_ACTIVITY.value,
            actor_id=current_user.id,
            target_user_id=user.id,
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} viewed activity for user {user.username}")
        
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "total_analyses": total_analyses,
            "analyses_by_type": {
                "email": email_analyses,
                "url": url_analyses
            },
            "threat_breakdown": threat_breakdown,
            "recent_activity": recent_activity
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user activity: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity"
        )



@router.post("/users/{user_id}/ban", response_model=UserResponse, tags=["Admin"])
async def ban_user(
    user_id: int,
    ban_request: UserBanRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Ban a user (Admin+ only)
    
    - **user_id**: User ID to ban
    - **reason**: Reason for banning (required)
    """
    try:
        # Log the incoming request for debugging
        logger.info(f"Ban request for user {user_id} with reason: {ban_request.reason}")
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-ban
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot ban your own account"
            )
        
        # Prevent banning other admins/superadmins (only superadmin can ban admins)
        if user.is_admin and not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SuperAdmin can ban other admins"
            )
        
        # Check if already banned
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already banned"
            )
        
        # Ban the user
        user.is_banned = True
        user.banned_at = datetime.now(timezone.utc)
        user.banned_by = current_user.id
        user.ban_reason = ban_request.reason
        
        await db.commit()
        await db.refresh(user)
        
        # Log the action
        await audit_service.log_user_ban(
            db=db,
            actor_id=current_user.id,
            target_user_id=user.id,
            reason=ban_request.reason,
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} banned user {user.username}. Reason: {ban_request.reason}")
        
        return UserResponse.model_validate(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ban user: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ban user"
        )


@router.post("/users/{user_id}/unban", response_model=UserResponse, tags=["Admin"])
async def unban_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Unban a user (Admin+ only)
    
    - **user_id**: User ID to unban
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is banned
        if not user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not banned"
            )
        
        # Unban the user
        user.is_banned = False
        user.banned_at = None
        user.banned_by = None
        user.ban_reason = None
        
        await db.commit()
        await db.refresh(user)
        
        # Log the action
        await audit_service.log_user_unban(
            db=db,
            actor_id=current_user.id,
            target_user_id=user.id,
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} unbanned user {user.username}")
        
        return UserResponse.model_validate(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unban user: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unban user"
        )


@router.get("/banned-users", tags=["Admin"])
async def list_banned_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all banned users (Admin+ only)
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    try:
        # Get total count of banned users
        count_result = await db.execute(
            select(func.count(User.id)).where(User.is_banned == True)
        )
        total = count_result.scalar()
        
        # Get banned users with pagination
        result = await db.execute(
            select(User)
            .where(User.is_banned == True)
            .order_by(desc(User.banned_at))
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()
        
        # Get banned_by usernames for each user
        users_with_details = []
        for user in users:
            user_dict = UserResponse.model_validate(user).model_dump()
            
            # Add banned_by username if available
            if user.banned_by:
                banned_by_result = await db.execute(
                    select(User).where(User.id == user.banned_by)
                )
                banned_by_user = banned_by_result.scalar_one_or_none()
                user_dict['banned_by_username'] = banned_by_user.username if banned_by_user else 'Unknown'
            else:
                user_dict['banned_by_username'] = None
            
            users_with_details.append(user_dict)
        
        logger.info(f"Admin {current_user.username} listed banned users")
        
        return {
            "users": users_with_details,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Failed to list banned users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve banned users"
        )



@router.get("/audit-logs", response_model=List[AuditLogResponse], tags=["Admin"])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    actor_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit logs with optional filtering (Admin+ only)
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **action**: Filter by action type (optional)
    - **actor_id**: Filter by actor user ID (optional)
    - **target_user_id**: Filter by target user ID (optional)
    """
    try:
        from sqlalchemy.orm import selectinload
        
        # Build query with eager loading of relationships
        query = select(AuditLog).options(
            selectinload(AuditLog.actor),
            selectinload(AuditLog.target_user)
        ).order_by(desc(AuditLog.created_at))
        
        # Apply filters
        if action:
            query = query.where(AuditLog.action == action)
        if actor_id:
            query = query.where(AuditLog.actor_id == actor_id)
        if target_user_id:
            query = query.where(AuditLog.target_user_id == target_user_id)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        # Format response with usernames
        response = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "action": log.action,
                "actor_id": log.actor_id,
                "actor_username": log.actor.username if log.actor else None,
                "target_user_id": log.target_user_id,
                "target_username": log.target_user.username if log.target_user else None,
                "details": log.details,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "created_at": log.created_at
            }
            response.append(AuditLogResponse(**log_dict))
        
        # Log this action
        await audit_service.log_action(
            db=db,
            action=AuditAction.ADMIN_VIEWED_AUDIT_LOGS.value,
            actor_id=current_user.id
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} viewed audit logs")
        
        return response
    
    except Exception as e:
        logger.error(f"Failed to get audit logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.get("/audit-logs/actions", tags=["Admin"])
async def get_audit_actions(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all available audit action types (Admin+ only)
    """
    return {
        "actions": [action.value for action in AuditAction]
    }


@router.get("/audit-logs/stats", tags=["Admin"])
async def get_audit_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit log statistics (Admin+ only)
    
    Returns:
    - Total audit logs count
    - Actions by type
    - Most active admins
    - Recent activity summary
    """
    try:
        # Total logs
        total_logs_result = await db.execute(select(func.count(AuditLog.id)))
        total_logs = total_logs_result.scalar()
        
        # Logs by action type
        actions_count = {}
        for action in AuditAction:
            result = await db.execute(
                select(func.count(AuditLog.id)).where(AuditLog.action == action.value)
            )
            count = result.scalar()
            if count > 0:
                actions_count[action.value] = count
        
        # Most active admins (top 5)
        from sqlalchemy import and_
        active_admins_result = await db.execute(
            select(
                AuditLog.actor_id,
                User.username,
                func.count(AuditLog.id).label('action_count')
            )
            .join(User, AuditLog.actor_id == User.id)
            .group_by(AuditLog.actor_id, User.username)
            .order_by(desc('action_count'))
            .limit(5)
        )
        active_admins = [
            {"user_id": row[0], "username": row[1], "action_count": row[2]}
            for row in active_admins_result.all()
        ]
        
        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_activity_result = await db.execute(
            select(func.count(AuditLog.id)).where(AuditLog.created_at >= yesterday)
        )
        recent_activity = recent_activity_result.scalar()
        
        logger.info(f"Admin {current_user.username} viewed audit stats")
        
        return {
            "total_logs": total_logs,
            "actions_by_type": actions_count,
            "most_active_admins": active_admins,
            "recent_activity_24h": recent_activity
        }
    
    except Exception as e:
        logger.error(f"Failed to get audit stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit statistics"
        )



# ============================================================================
# EMAIL PROVIDER MANAGEMENT
# ============================================================================

@router.get("/email-providers/connections", tags=["Admin - Email Providers"])
async def get_all_email_connections(
    skip: int = 0,
    limit: int = 100,
    provider: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all email provider connections (Admin+ only)
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **provider**: Filter by provider (gmail, outlook)
    - **user_id**: Filter by user ID
    """
    try:
        from app.models.email_provider_models import UserEmailCredential
        from datetime import datetime
        
        # Build query
        query = select(UserEmailCredential).order_by(desc(UserEmailCredential.created_at))
        
        # Apply filters
        if provider:
            query = query.where(UserEmailCredential.provider == provider)
        if user_id:
            query = query.where(UserEmailCredential.user_id == user_id)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        connections = result.scalars().all()
        
        # Format response with user details
        response = []
        for conn in connections:
            # Get user details
            user_result = await db.execute(select(User).where(User.id == conn.user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                # Check if token is expired
                is_expired = False
                if conn.token_expiry:
                    is_expired = conn.token_expiry < datetime.now(timezone.utc)
                
                response.append({
                    "id": conn.id,
                    "user_id": conn.user_id,
                    "username": user.username,
                    "email": user.email,
                    "provider": conn.provider,
                    "email_address": conn.email_address,
                    "token_expiry": conn.token_expiry,
                    "is_expired": is_expired,
                    "created_at": conn.created_at,
                    "updated_at": conn.updated_at
                })
        
        logger.info(f"Admin {current_user.username} viewed email provider connections")
        
        return response
    
    except Exception as e:
        logger.error(f"Failed to get email connections: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email connections"
        )


@router.get("/email-providers/stats", tags=["Admin - Email Providers"])
async def get_email_provider_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get email provider statistics (Admin+ only)
    
    Returns:
    - Total connections
    - Connections by provider
    - Active vs expired connections
    - Users with connections
    - Recent connections
    """
    try:
        from app.models.email_provider_models import UserEmailCredential
        from datetime import datetime, timedelta
        
        # Total connections
        total_result = await db.execute(select(func.count(UserEmailCredential.id)))
        total_connections = total_result.scalar()
        
        # Connections by provider
        connections_by_provider = {}
        for provider_name in ["gmail", "outlook"]:
            result = await db.execute(
                select(func.count(UserEmailCredential.id))
                .where(UserEmailCredential.provider == provider_name)
            )
            count = result.scalar()
            if count > 0:
                connections_by_provider[provider_name] = count
        
        # Active connections (not expired)
        now = datetime.now(timezone.utc)
        active_result = await db.execute(
            select(func.count(UserEmailCredential.id))
            .where(
                (UserEmailCredential.token_expiry.is_(None)) |
                (UserEmailCredential.token_expiry > now)
            )
        )
        active_connections = active_result.scalar()
        
        # Expired connections
        expired_result = await db.execute(
            select(func.count(UserEmailCredential.id))
            .where(
                (UserEmailCredential.token_expiry.isnot(None)) &
                (UserEmailCredential.token_expiry <= now)
            )
        )
        expired_connections = expired_result.scalar()
        
        # Users with connections
        users_result = await db.execute(
            select(func.count(func.distinct(UserEmailCredential.user_id)))
        )
        users_with_connections = users_result.scalar()
        
        # Recent connections (last 24 hours)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_result = await db.execute(
            select(func.count(UserEmailCredential.id))
            .where(UserEmailCredential.created_at >= yesterday)
        )
        recent_connections = recent_result.scalar()
        
        logger.info(f"Admin {current_user.username} viewed email provider stats")
        
        return {
            "total_connections": total_connections,
            "connections_by_provider": connections_by_provider,
            "active_connections": active_connections,
            "expired_connections": expired_connections,
            "users_with_connections": users_with_connections,
            "recent_connections_24h": recent_connections
        }
    
    except Exception as e:
        logger.error(f"Failed to get email provider stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email provider statistics"
        )


@router.delete("/email-providers/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin - Email Providers"])
async def revoke_email_connection(
    connection_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke an email provider connection (Admin+ only)
    
    - **connection_id**: Connection ID to revoke
    
    This will disconnect the user's email account.
    """
    try:
        from app.models.email_provider_models import UserEmailCredential
        
        # Get connection
        result = await db.execute(
            select(UserEmailCredential).where(UserEmailCredential.id == connection_id)
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email connection not found"
            )
        
        # Get user details for logging
        user_result = await db.execute(select(User).where(User.id == connection.user_id))
        user = user_result.scalar_one_or_none()
        
        provider = connection.provider
        user_id = connection.user_id
        username = user.username if user else "Unknown"
        
        # Delete connection
        await db.delete(connection)
        await db.commit()
        
        # Log the action
        await audit_service.log_action(
            db=db,
            action="EMAIL_CONNECTION_REVOKED",
            actor_id=current_user.id,
            target_user_id=user_id,
            details={
                "provider": provider,
                "connection_id": connection_id
            },
            request=request
        )
        await db.commit()
        
        logger.info(f"Admin {current_user.username} revoked {provider} connection for user {username}")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke email connection: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke email connection"
        )


@router.get("/email-providers/users/{user_id}/connections", tags=["Admin - Email Providers"])
async def get_user_email_connections(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all email connections for a specific user (Admin+ only)
    
    - **user_id**: User ID to get connections for
    """
    try:
        from app.models.email_provider_models import UserEmailCredential
        from datetime import datetime
        
        # Check if user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all connections for this user
        result = await db.execute(
            select(UserEmailCredential)
            .where(UserEmailCredential.user_id == user_id)
            .order_by(desc(UserEmailCredential.created_at))
        )
        connections = result.scalars().all()
        
        # Format response
        response = []
        for conn in connections:
            # Check if token is expired
            is_expired = False
            if conn.token_expiry:
                is_expired = conn.token_expiry < datetime.now(timezone.utc)
            
            response.append({
                "id": conn.id,
                "provider": conn.provider,
                "email_address": conn.email_address,
                "token_expiry": conn.token_expiry,
                "is_expired": is_expired,
                "created_at": conn.created_at,
                "updated_at": conn.updated_at
            })
        
        logger.info(f"Admin {current_user.username} viewed email connections for user {user.username}")
        
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "connections": response,
            "total_connections": len(response)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user email connections: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user email connections"
        )



# ============================================================================
# RATE LIMIT MANAGEMENT
# ============================================================================

@router.get("/rate-limits/status/{ip_address}", tags=["Admin - Rate Limits"])
async def get_rate_limit_status(
    ip_address: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get rate limit status for a specific IP address (Admin+ only)
    
    - **ip_address**: IP address to check
    
    Returns current rate limit status including:
    - Requests per endpoint
    - Remaining requests
    - Rate limit windows
    """
    try:
        from app.utils.rate_limit_utils import get_rate_limit_status
        
        status = get_rate_limit_status(ip_address)
        
        logger.info(f"Admin {current_user.username} checked rate limit status for IP {ip_address}")
        
        return status
    
    except Exception as e:
        logger.error(f"Failed to get rate limit status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rate limit status"
        )


@router.delete("/rate-limits/clear/{ip_address}", tags=["Admin - Rate Limits"])
async def clear_rate_limit(
    ip_address: str,
    request: Request,
    endpoint: Optional[str] = None,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear rate limit records for an IP address (SuperAdmin only)
    
    - **ip_address**: IP address to clear
    - **endpoint**: Optional specific endpoint to clear (clears all if not provided)
    
    This will reset rate limiting for the specified IP, allowing them to make requests again.
    Use with caution - only for legitimate users who were accidentally rate limited.
    """
    try:
        from app.utils.rate_limit_utils import clear_rate_limit
        
        cleared = clear_rate_limit(ip_address, endpoint)
        
        if not cleared:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No rate limit records found for this IP"
            )
        
        # Audit log — destructive operation
        await audit_service.log_action(
            db=db,
            action=AuditAction.RATE_LIMIT_CLEARED.value,
            actor_id=current_user.id,
            details={"ip_address": ip_address, "endpoint": endpoint or "all"},
            request=request
        )
        await db.commit()
        
        logger.warning(
            f"SuperAdmin {current_user.username} cleared rate limits for IP {ip_address}"
            + (f" on endpoint {endpoint}" if endpoint else " (all endpoints)")
        )
        
        return {
            "message": "Rate limit cleared successfully",
            "ip_address": ip_address,
            "endpoint": endpoint or "all"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear rate limit: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear rate limit"
        )


@router.get("/rate-limits/top-requesters", tags=["Admin - Rate Limits"])
async def get_top_requesters(
    limit: int = 10,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top IP addresses by request count (Admin+ only)
    
    - **limit**: Maximum number of results to return (default: 10)
    
    Returns list of IP addresses sorted by total request count.
    Useful for identifying potential abuse or high-traffic sources.
    """
    try:
        from app.utils.rate_limit_utils import get_top_requesters
        
        top_requesters = get_top_requesters(limit)
        
        logger.info(f"Admin {current_user.username} viewed top requesters")
        
        return {
            "top_requesters": top_requesters,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Failed to get top requesters: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve top requesters"
        )


@router.get("/rate-limits/stats", tags=["Admin - Rate Limits"])
async def get_rate_limit_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall rate limiting statistics (Admin+ only)
    
    Returns:
    - Total IPs being tracked
    - Total endpoints being tracked
    - Total requests tracked
    - Most hit endpoints
    """
    try:
        from app.utils.rate_limit_utils import get_rate_limit_stats
        
        stats = get_rate_limit_stats()
        
        logger.info(f"Admin {current_user.username} viewed rate limit stats")
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get rate limit stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rate limit statistics"
        )


@router.get("/rate-limits/check/{ip_address}/{endpoint:path}", tags=["Admin - Rate Limits"])
async def check_if_rate_limited(
    ip_address: str,
    endpoint: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if an IP is currently rate limited for a specific endpoint (Admin+ only)
    
    - **ip_address**: IP address to check
    - **endpoint**: Endpoint path to check (e.g., /api/auth/login)
    
    Returns whether the IP is currently rate limited and details about their usage.
    """
    try:
        from app.utils.rate_limit_utils import is_ip_rate_limited, get_rate_limit_status
        
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        is_limited = is_ip_rate_limited(ip_address, endpoint)
        status = get_rate_limit_status(ip_address)
        
        endpoint_status = status.get("endpoints", {}).get(endpoint, {})
        
        logger.info(f"Admin {current_user.username} checked if IP {ip_address} is rate limited on {endpoint}")
        
        return {
            "ip_address": ip_address,
            "endpoint": endpoint,
            "is_rate_limited": is_limited,
            "endpoint_status": endpoint_status
        }
    
    except Exception as e:
        logger.error(f"Failed to check rate limit: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check rate limit status"
        )


@router.get("/rate-limits/config", tags=["Admin - Rate Limits"])
async def get_rate_limit_config(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current rate limit configuration (Admin+ only)
    
    Returns the rate limit settings for all endpoints.
    Shows maximum requests and time window for each endpoint.
    """
    try:
        from app.middleware import rate_limiter
        
        # Format the limits for better readability
        formatted_limits = {}
        for endpoint, (max_requests, window_seconds) in rate_limiter.limits.items():
            formatted_limits[endpoint] = {
                "max_requests": max_requests,
                "window_seconds": window_seconds,
                "window_minutes": window_seconds / 60,
                "description": f"{max_requests} requests per {window_seconds} seconds"
            }
        
        logger.info(f"Admin {current_user.username} viewed rate limit configuration")
        
        return {
            "limits": formatted_limits,
            "total_endpoints_configured": len(formatted_limits)
        }
    
    except Exception as e:
        logger.error(f"Failed to get rate limit config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rate limit configuration"
        )



# ============================================================================
# SYSTEM NOTIFICATIONS TESTING
# ============================================================================

@router.post("/test/database-error-notification", tags=["Admin - Testing"])
async def test_database_error_notification(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Test database error notification system (Admin+ only)
    
    Sends a test database error alert to all configured admin emails.
    This is useful for testing the notification system without causing an actual database error.
    """
    try:
        from app.services.notification_service import notification_service
        from datetime import datetime
        import traceback
        
        # Prepare test error details
        error_details = {
            'error_message': 'TEST: Simulated database connection failure for notification testing',
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'operation': 'TEST: Admin-triggered notification test',
            'traceback': 'This is a test notification. No actual error occurred.\n\nStack trace simulation:\n  File "test.py", line 1, in <module>\n    test_database_error()\n  File "test.py", line 5, in test_database_error\n    raise Exception("Test error")'
        }
        
        # Send the test notification
        success = await notification_service.send_database_error_alert(error_details)
        
        if success:
            logger.info(f"Admin {current_user.username} sent test database error notification")
            return {
                "message": "Test database error notification sent successfully",
                "sent_to": "All configured admin emails",
                "timestamp": error_details['timestamp']
            }
        else:
            logger.error(f"Failed to send test database error notification for admin {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test notification. Check if ADMIN_ALERT_EMAILS is configured in .env"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing database error notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )



# ============================================================================
# BRUTE FORCE DETECTION
# ============================================================================

@router.get("/brute-force/attacks", tags=["Admin - Security"])
async def get_brute_force_attacks(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all IPs currently flagged for brute force attacks (Admin+ only)
    
    Returns list of IPs with attack details including:
    - IP address
    - Failed login attempts
    - Usernames attempted
    - Block status
    - Attack pattern
    """
    try:
        from app.middleware.rate_limiter import rate_limiter
        
        attacks = rate_limiter.get_all_brute_force_ips()
        
        logger.info(f"Admin {current_user.username} viewed brute force attacks")
        
        return {
            "attacks": attacks,
            "total": len(attacks),
            "threshold": rate_limiter.brute_force_threshold,
            "window_seconds": rate_limiter.brute_force_window,
            "block_duration_seconds": rate_limiter.brute_force_block_duration
        }
    
    except Exception as e:
        logger.error(f"Failed to get brute force attacks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve brute force attacks"
        )


@router.get("/brute-force/check/{ip_address}", tags=["Admin - Security"])
async def check_brute_force_status(
    ip_address: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Check brute force status for a specific IP address (Admin+ only)
    
    - **ip_address**: IP address to check
    
    Returns detailed statistics about failed login attempts and block status.
    """
    try:
        from app.middleware.rate_limiter import rate_limiter
        
        stats = rate_limiter.get_brute_force_stats(ip_address)
        
        logger.info(f"Admin {current_user.username} checked brute force status for IP {ip_address}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to check brute force status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check brute force status"
        )


@router.delete("/brute-force/unblock/{ip_address}", tags=["Admin - Security"])
async def unblock_brute_force_ip(
    ip_address: str,
    request: Request,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually unblock an IP that was blocked for brute force (SuperAdmin only)
    
    - **ip_address**: IP address to unblock
    
    Use with caution - only unblock IPs that were incorrectly flagged.
    """
    try:
        from app.middleware.rate_limiter import rate_limiter
        
        # Check if IP is blocked
        if ip_address not in rate_limiter.brute_force_ips:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IP address is not currently blocked"
            )
        
        # Remove from blocked IPs
        del rate_limiter.brute_force_ips[ip_address]
        
        # Clear failed login history
        if ip_address in rate_limiter.failed_logins:
            del rate_limiter.failed_logins[ip_address]
        
        # Audit log — destructive operation
        await audit_service.log_action(
            db=db,
            action=AuditAction.BRUTE_FORCE_IP_UNBLOCKED.value,
            actor_id=current_user.id,
            details={"ip_address": ip_address},
            request=request
        )
        await db.commit()
        
        logger.warning(f"SuperAdmin {current_user.username} manually unblocked IP {ip_address}")
        
        return {
            "message": "IP address unblocked successfully",
            "ip_address": ip_address
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unblock IP: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unblock IP address"
        )


@router.post("/test/brute-force-notification", tags=["Admin - Testing"])
async def test_brute_force_notification(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Test brute force attack notification system (Admin+ only)
    
    Sends a test brute force alert to all configured admin emails and in-app notifications.
    This is useful for testing the notification system without triggering an actual attack.
    """
    try:
        from app.services.notification_service import notification_service
        from datetime import datetime
        
        # Prepare test attack details
        attack_details = {
            'ip_address': '192.168.1.100',
            'failed_attempts': 15,
            'threshold': 10,
            'window_seconds': 300,
            'usernames_attempted': ['admin', 'root', 'user', 'test', 'administrator'],
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'is_blocked': True,
            'block_duration': 3600,
            'pattern': 'automated',
            'location': 'Test Location (Simulated)'
        }
        
        # Send the test notification (email + in-app)
        success = await notification_service.send_brute_force_alert(attack_details, db)
        
        if success:
            logger.info(f"Admin {current_user.username} sent test brute force notification")
            return {
                "message": "Test brute force notification sent successfully",
                "sent_to": "All configured admin emails + in-app notification center",
                "timestamp": attack_details['timestamp'],
                "test_ip": attack_details['ip_address']
            }
        else:
            logger.error(f"Failed to send test brute force notification for admin {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test notification. Check if ADMIN_ALERT_EMAILS is configured in .env"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing brute force notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )
