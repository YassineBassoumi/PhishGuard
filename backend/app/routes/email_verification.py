"""
Email verification routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.models.email_verification_schemas import (
    EmailVerificationRequest,
    EmailVerificationConfirm,
    EmailVerificationResponse
)
from app.services.auth_service import auth_service
from app.services.email_verification_service import email_verification_service

router = APIRouter(prefix="/api/email-verification", tags=["Email Verification"])
logger = logging.getLogger(__name__)


@router.post("/resend", response_model=EmailVerificationResponse)
async def resend_verification_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend verification email
    
    - **email**: User's email address
    
    Returns success message
    """
    try:
        # Find user by email
        user = await auth_service.get_user_by_email(db, request.email)
        
        if user:
            # Check if already verified
            if user.email_verified:
                return EmailVerificationResponse(
                    message="Email déjà vérifié"
                )
            
            # Invalidate old tokens
            await email_verification_service.invalidate_user_tokens(db, user.id)
            
            # Create new token
            token = await email_verification_service.create_verification_token(db, user)
            
            # Send email
            email_sent = await email_verification_service.send_verification_email(user, token)
            
            if email_sent:
                logger.info(f"Verification email sent to {user.email}")
            else:
                logger.error(f"Failed to send verification email to {user.email}")
            
            await db.commit()
        
        # Always return success (security best practice)
        return EmailVerificationResponse(
            message="Si cette adresse existe, un email de vérification a été envoyé"
        )
    
    except Exception as e:
        logger.error(f"Resend verification email failed: {str(e)}", exc_info=True)
        await db.rollback()
        return EmailVerificationResponse(
            message="Si cette adresse existe, un email de vérification a été envoyé"
        )


@router.post("/verify", response_model=EmailVerificationResponse)
async def verify_email(
    request: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email with token
    
    - **token**: Verification token from email
    
    Marks the user's email as verified
    """
    try:
        # Verify token
        user = await email_verification_service.verify_token(db, request.token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalide ou expiré"
            )
        
        # Check if already verified
        if user.email_verified:
            return EmailVerificationResponse(
                message="Email déjà vérifié"
            )
        
        # Mark email as verified
        user.email_verified = True
        
        # Mark token as used
        await email_verification_service.mark_token_as_used(db, request.token)
        
        # Invalidate other tokens
        await email_verification_service.invalidate_user_tokens(db, user.id)
        
        await db.commit()
        
        logger.info(f"Email verified successfully for user: {user.username}")
        
        return EmailVerificationResponse(
            message="Email vérifié avec succès"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la vérification de l'email"
        )
