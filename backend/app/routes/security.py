"""
Security Routes
Handles account security actions like securing compromised accounts
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
import secrets
import logging

from app.database import get_db
from app.models.user_models import User
from app.models.password_reset_models import PasswordResetToken
from app.services.auth_service import get_current_active_user
from app.services.email_service import email_service
from app.services.session_service import session_service

router = APIRouter(prefix="/api/security", tags=["Security"])
logger = logging.getLogger(__name__)


@router.get("/secure-account/{user_id}")
@router.post("/secure-account/{user_id}")
async def secure_account(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Secure a potentially compromised account
    
    This endpoint can be called without authentication (via email link)
    to secure an account if someone else changed the password
    
    Actions taken:
    1. Invalidate all active sessions (force logout everywhere)
    2. Generate password reset token
    3. Send password reset email
    4. Log security event
    """
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 1. Invalidate all sessions (force logout everywhere)
        from app.models.session_models import UserSession
        deleted_sessions = await db.execute(
            delete(UserSession).where(UserSession.user_id == user_id)
        )
        session_count = deleted_sessions.rowcount
        
        # 2. Generate password reset token
        from app.services.password_reset_service import password_reset_service
        reset_token = await password_reset_service.create_reset_token(db, user)
        
        # 3. Send security alert + password reset email
        from app.services.notification_service import notification_service
        
        # Get client IP
        client_ip = request.client.host if request and request.client else 'Unknown'
        if request:
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                client_ip = forwarded_for.split(',')[0].strip()
        
        # Get location
        from app.utils.geolocation import get_location_from_ip
        location = await get_location_from_ip(client_ip)
        
        # Send comprehensive security email
        import os
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .action-box {{ background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Account Security Alert</h1>
                    <p>Your account has been secured</p>
                </div>
                <div class="content">
                    <p>Hi <strong>{user.username}</strong>,</p>
                    
                    <div class="alert-box">
                        <h3>⚠️ Security Action Taken</h3>
                        <p>You (or someone) clicked "Secure My Account" because of an unauthorized password change.</p>
                    </div>
                    
                    <div class="action-box">
                        <h3>✅ Actions Completed</h3>
                        <ul>
                            <li>All active sessions terminated ({session_count} session(s) logged out)</li>
                            <li>Password reset token generated</li>
                            <li>Account access temporarily restricted</li>
                        </ul>
                    </div>
                    
                    <div class="info">
                        <p><strong>Security Request Details:</strong></p>
                        <p>📅 Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p>🌍 Location: {location}</p>
                        <p>🔢 IP Address: {client_ip}</p>
                    </div>
                    
                    <h3>🔐 Next Steps - Reset Your Password</h3>
                    <p>To regain access to your account, please reset your password immediately:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="button">Reset My Password</a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        Or copy this link: <br>
                        <code style="background: #f0f0f0; padding: 5px; display: block; margin-top: 10px; word-break: break-all;">
                            {reset_url}
                        </code>
                    </p>
                    
                    <p><strong>This link expires in 1 hour.</strong></p>
                    
                    <div class="alert-box">
                        <h3>🛡️ Security Recommendations</h3>
                        <ul>
                            <li>Choose a strong, unique password (12+ characters)</li>
                            <li>Enable Two-Factor Authentication (2FA)</li>
                            <li>Never share your password with anyone</li>
                            <li>Check for suspicious activity in your account</li>
                        </ul>
                    </div>
                    
                    <p><strong>Didn't request this?</strong></p>
                    <p>If you didn't click "Secure My Account", someone may have access to your email. 
                    Please secure your email account immediately and contact our support team.</p>
                    
                    <div class="footer">
                        <p>This is an automated security message from PhishGuard AI</p>
                        <p>© 2026 PhishGuard AI. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        await email_service.send_email(
            to_email=user.email,
            subject="🔒 Your PhishGuard Account Has Been Secured",
            html_content=html_content
        )
        
        await db.commit()
        
        logger.warning(
            f"Account secured for user {user.username} (ID: {user_id}). "
            f"{session_count} sessions terminated. IP: {client_ip}, Location: {location}"
        )
        
        # Redirect to frontend success page
        import os
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(url=f"{frontend_url}/account-secured", status_code=303)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to secure account {user_id}: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to secure account"
        )


@router.post("/secure-account-authenticated")
async def secure_account_authenticated(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Secure account for authenticated user
    
    Same as /secure-account but requires authentication
    Useful if user is still logged in and wants to secure their account
    """
    return await secure_account(current_user.id, db, request)
