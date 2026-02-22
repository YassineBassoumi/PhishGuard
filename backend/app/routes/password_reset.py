"""
Password reset routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.models.password_reset_schemas import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse
)
from app.services.auth_service import auth_service
from app.services.password_reset_service import password_reset_service

router = APIRouter(prefix="/api/password-reset", tags=["Password Reset"])
logger = logging.getLogger(__name__)


@router.post("/request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset email
    
    - **email**: User's email address
    
    Returns a success message even if email doesn't exist (security best practice)
    """
    try:
        # Find user by email
        user = await auth_service.get_user_by_email(db, request.email)
        
        if user:
            # Invalidate any existing tokens for this user
            await password_reset_service.invalidate_user_tokens(db, user.id)
            
            # Create new reset token
            token = await password_reset_service.create_reset_token(db, user)
            
            # Send reset email
            email_sent = await password_reset_service.send_reset_email(user, token)
            
            if email_sent:
                logger.info(f"Password reset email sent to {user.email}")
            else:
                logger.error(f"Failed to send password reset email to {user.email}")
            
            await db.commit()
        else:
            # User not found, but don't reveal this for security
            logger.warning(f"Password reset requested for non-existent email: {request.email}")
        
        # Always return success message (security best practice)
        return PasswordResetResponse(
            message="Si cette adresse email existe, un lien de réinitialisation a été envoyé"
        )
    
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}", exc_info=True)
        await db.rollback()
        # Still return success message to avoid information disclosure
        return PasswordResetResponse(
            message="Si cette adresse email existe, un lien de réinitialisation a été envoyé"
        )


@router.post("/verify", response_model=PasswordResetResponse)
async def verify_reset_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify if a reset token is valid
    
    - **token**: Reset token from email
    
    Returns success if token is valid and not expired
    """
    try:
        user = await password_reset_service.verify_reset_token(db, token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalide ou expiré"
            )
        
        return PasswordResetResponse(
            message="Token valide"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la vérification du token"
        )


@router.post("/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm password reset with token and new password
    
    - **token**: Reset token from email
    - **new_password**: New password (minimum 8 characters)
    
    Resets the password and invalidates the token
    """
    try:
        # Verify token
        user = await password_reset_service.verify_reset_token(db, request.token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalide ou expiré"
            )
        
        # Check if user is banned
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte banni"
            )
        
        # Update password
        user.hashed_password = auth_service.get_password_hash(request.new_password)
        db.add(user)
        
        # Mark token as used
        await password_reset_service.mark_token_as_used(db, request.token)
        
        # Invalidate all other tokens for this user
        await password_reset_service.invalidate_user_tokens(db, user.id)
        
        # Invalidate all sessions for security
        from app.services.session_service import session_service
        await session_service.revoke_all_sessions(db, user.id)
        
        # Commit changes
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Password reset successful for user: {user.username}")
        
        return PasswordResetResponse(
            message="Mot de passe réinitialisé avec succès"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la réinitialisation du mot de passe"
        )
