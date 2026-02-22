"""
Notifications API Routes
Handles fetching and managing user notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, desc
from datetime import datetime
import logging

from app.database import get_db
from app.models.user_models import User
from app.models.notification_models import NotificationHistory
from app.services.auth_service import get_current_active_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)


@router.get("/recent")
async def get_recent_notifications(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent notifications for the current user
    
    Returns:
    - notifications: List of recent notifications
    - unread_count: Number of unread notifications
    """
    try:
        # Get recent notifications
        result = await db.execute(
            select(NotificationHistory)
            .where(NotificationHistory.user_id == current_user.id)
            .order_by(desc(NotificationHistory.sent_at))
            .limit(limit)
        )
        notifications = result.scalars().all()
        
        # Get unread count
        unread_result = await db.execute(
            select(NotificationHistory)
            .where(
                and_(
                    NotificationHistory.user_id == current_user.id,
                    NotificationHistory.is_read == False
                )
            )
        )
        unread_count = len(unread_result.scalars().all())
        
        # Format notifications
        notifications_list = [
            {
                "id": notif.id,
                "notification_type": notif.notification_type,
                "subject": notif.subject,
                "sent_at": notif.sent_at.isoformat(),
                "status": notif.status,
                "is_read": notif.is_read,
                "read_at": notif.read_at.isoformat() if notif.read_at else None
            }
            for notif in notifications
        ]
        
        return {
            "notifications": notifications_list,
            "unread_count": unread_count
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.get("/all")
async def get_all_notifications(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all notifications with pagination
    """
    try:
        offset = (page - 1) * per_page
        
        # Get notifications
        result = await db.execute(
            select(NotificationHistory)
            .where(NotificationHistory.user_id == current_user.id)
            .order_by(desc(NotificationHistory.sent_at))
            .offset(offset)
            .limit(per_page)
        )
        notifications = result.scalars().all()
        
        # Get total count
        count_result = await db.execute(
            select(NotificationHistory)
            .where(NotificationHistory.user_id == current_user.id)
        )
        total = len(count_result.scalars().all())
        
        # Format notifications
        notifications_list = [
            {
                "id": notif.id,
                "notification_type": notif.notification_type,
                "subject": notif.subject,
                "sent_at": notif.sent_at.isoformat(),
                "status": notif.status,
                "is_read": notif.is_read,
                "read_at": notif.read_at.isoformat() if notif.read_at else None
            }
            for notif in notifications
        ]
        
        return {
            "notifications": notifications_list,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch all notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a notification as read
    """
    try:
        # Get notification
        result = await db.execute(
            select(NotificationHistory)
            .where(
                and_(
                    NotificationHistory.id == notification_id,
                    NotificationHistory.user_id == current_user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Mark as read
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark all notifications as read for the current user
    """
    try:
        await db.execute(
            update(NotificationHistory)
            .where(
                and_(
                    NotificationHistory.user_id == current_user.id,
                    NotificationHistory.is_read == False
                )
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        
        await db.commit()
        
        return {"message": "All notifications marked as read"}
        
    except Exception as e:
        logger.error(f"Failed to mark all as read: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a notification
    """
    try:
        # Get notification
        result = await db.execute(
            select(NotificationHistory)
            .where(
                and_(
                    NotificationHistory.id == notification_id,
                    NotificationHistory.user_id == current_user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        await db.delete(notification)
        await db.commit()
        
        return {"message": "Notification deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete notification: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )
