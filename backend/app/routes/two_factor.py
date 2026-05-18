"""
Two-Factor Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user_models import User
from app.models.auth_schemas import (
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorDisableRequest,
    TwoFactorStatusResponse
)
from app.services.auth_service import get_current_active_user, auth_service
from app.services.two_factor_service import two_factor_service
from app.services.notification_service import notification_service
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/2fa", tags=["Two-Factor Authentication"])


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get 2FA status for current user"""
    return TwoFactorStatusResponse(
        enabled=current_user.two_factor_enabled,
        backup_codes_remaining=two_factor_service.get_remaining_backup_codes(current_user)
    )


@router.post("/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Setup 2FA for the current user
    Returns QR code and backup codes
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled. Disable it first to set up again."
        )
    
    # Generate secret, QR code, and backup codes
    secret, qr_code, backup_codes = await two_factor_service.setup_2fa(current_user)
    
    # Save to database
    await db.commit()
    
    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/enable")
async def enable_2fa(
    verify_request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Enable 2FA after verifying the initial token
    User must scan QR code and enter a valid token
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Call /setup first."
        )
    
    # Verify the token
    success = await two_factor_service.enable_2fa(current_user, verify_request.token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please try again."
        )
    
    # Save to database
    await db.commit()
    
    # Get client IP address
    client_ip = request.client.host if request and request.client else 'Unknown'
    # Check for forwarded IP (if behind proxy)
    if request:
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
    
    # Extract user data before background task (avoid lazy loading issues)
    user_id = current_user.id
    
    # Send 2FA enabled notification (async, don't wait)
    # Note: We don't pass db session to background task - it will create its own
    try:
        import asyncio
        from app.database import get_db as get_notification_db
        from app.utils.geolocation import get_location_from_ip
        
        async def send_2fa_enabled_notification_background():
            """Background task to send notification with its own DB session"""
            async for notification_db in get_notification_db():
                try:
                    # Fetch fresh user object in this session
                    from sqlalchemy import select
                    result = await notification_db.execute(
                        select(User).where(User.id == user_id)
                    )
                    fresh_user = result.scalar_one()
                    
                    # Get location from IP
                    location = await get_location_from_ip(client_ip)
                    
                    await notification_service.send_two_factor_changed_alert(
                        db=notification_db,
                        user=fresh_user,
                        action='Enabled',
                        change_details={
                            'changed_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                            'ip_address': client_ip,
                            'location': location
                        }
                    )
                finally:
                    await notification_db.close()
                break
        
        asyncio.create_task(send_2fa_enabled_notification_background())
    except Exception as e:
        logger.error(f"Failed to queue 2FA enabled notification: {str(e)}")
    
    return {
        "message": "Two-factor authentication enabled successfully",
        "enabled": True
    }


@router.post("/disable")
async def disable_2fa(
    disable_request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Disable 2FA (requires password verification)
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Disable 2FA
    success = await two_factor_service.disable_2fa(
        current_user,
        disable_request.password,
        auth_service
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    
    # Save to database
    await db.commit()
    
    # Get client IP address
    client_ip = request.client.host if request and request.client else 'Unknown'
    # Check for forwarded IP (if behind proxy)
    if request:
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
    
    # Extract user data before background task (avoid lazy loading issues)
    user_id = current_user.id
    
    # Send 2FA disabled notification (async, don't wait)
    # Note: We don't pass db session to background task - it will create its own
    try:
        import asyncio
        from app.database import get_db as get_notification_db
        from app.utils.geolocation import get_location_from_ip
        
        async def send_2fa_disabled_notification_background():
            """Background task to send notification with its own DB session"""
            async for notification_db in get_notification_db():
                try:
                    # Fetch fresh user object in this session
                    from sqlalchemy import select
                    result = await notification_db.execute(
                        select(User).where(User.id == user_id)
                    )
                    fresh_user = result.scalar_one()
                    
                    # Get location from IP
                    location = await get_location_from_ip(client_ip)
                    
                    await notification_service.send_two_factor_changed_alert(
                        db=notification_db,
                        user=fresh_user,
                        action='Disabled',
                        change_details={
                            'changed_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                            'ip_address': client_ip,
                            'location': location
                        }
                    )
                finally:
                    await notification_db.close()
                break
        
        asyncio.create_task(send_2fa_disabled_notification_background())
    except Exception as e:
        logger.error(f"Failed to queue 2FA disabled notification: {str(e)}")
    
    return {
        "message": "Two-factor authentication disabled successfully",
        "enabled": False
    }


@router.post("/verify")
async def verify_2fa_token(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify a 2FA token (for testing purposes)
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    is_valid = two_factor_service.verify_totp(
        current_user.two_factor_secret,
        request.token
    )
    
    return {
        "valid": is_valid,
        "message": "Token is valid" if is_valid else "Token is invalid"
    }


@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate backup codes
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Regenerate codes
    backup_codes = await two_factor_service.regenerate_backup_codes(current_user)
    
    # Save to database
    await db.commit()
    
    return {
        "message": "Backup codes regenerated successfully",
        "backup_codes": backup_codes
    }
