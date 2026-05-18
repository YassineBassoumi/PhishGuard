"""
Email verification service
Handles email verification token generation, validation, and email sending
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models.email_verification_models import EmailVerificationToken
from app.models.user_models import User
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for handling email verification"""
    
    TOKEN_EXPIRY_HOURS = 24  # 24 hours validity
    
    async def create_verification_token(self, db: AsyncSession, user: User) -> str:
        """
        Create a new email verification token for a user
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Token string
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
        
        # Create token record
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(verification_token)
        await db.flush()
        
        logger.info(f"Created email verification token for user {user.id}: {token[:20]}...")
        
        return token
    
    async def verify_token(self, db: AsyncSession, token: str) -> Optional[User]:
        """
        Verify an email verification token and return the associated user
        
        Args:
            db: Database session
            token: Verification token
            
        Returns:
            User object if token is valid, None otherwise
        """
        logger.info(f"Attempting to verify token: {token[:20]}...")
        
        # Find token
        result = await db.execute(
            select(EmailVerificationToken)
            .where(
                and_(
                    EmailVerificationToken.token == token,
                    EmailVerificationToken.is_used == False,
                    EmailVerificationToken.expires_at > datetime.now(timezone.utc)
                )
            )
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            # Debug: Check if token exists at all
            result_any = await db.execute(
                select(EmailVerificationToken)
                .where(EmailVerificationToken.token == token)
            )
            any_token = result_any.scalar_one_or_none()
            
            if any_token:
                logger.warning(f"Token found but invalid - is_used: {any_token.is_used}, expires_at: {any_token.expires_at}, now: {datetime.now(timezone.utc)}")
            else:
                logger.warning(f"Token not found in database: {token[:20]}...")
            
            return None
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == token_record.user_id)
        )
        user = result.scalar_one_or_none()
        
        logger.info(f"Token verified successfully for user: {user.username if user else 'None'}")
        
        return user
    
    async def mark_token_as_used(self, db: AsyncSession, token: str):
        """
        Mark a verification token as used
        
        Args:
            db: Database session
            token: Verification token
        """
        result = await db.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token == token)
        )
        token_record = result.scalar_one_or_none()
        
        if token_record:
            token_record.is_used = True
            await db.flush()
            logger.info(f"Marked verification token as used for user {token_record.user_id}")
    
    async def invalidate_user_tokens(self, db: AsyncSession, user_id: int):
        """
        Invalidate all verification tokens for a user
        
        Args:
            db: Database session
            user_id: User ID
        """
        result = await db.execute(
            select(EmailVerificationToken)
            .where(
                and_(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.is_used == False
                )
            )
        )
        tokens = result.scalars().all()
        
        for token in tokens:
            token.is_used = True
        
        await db.flush()
        logger.info(f"Invalidated {len(tokens)} verification tokens for user {user_id}")
    
    async def send_verification_email(self, user: User, token: str) -> bool:
        """
        Send verification email to user
        
        Args:
            user: User object
            token: Verification token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Create verification link
        verification_link = f"http://localhost:5173/verify-email?token={token}"
        
        # Email subject
        subject = "Vérifiez votre adresse email - PhishGuard AI"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .content h2 {{
                    color: #1a202c;
                    font-size: 22px;
                    margin-top: 0;
                    margin-bottom: 20px;
                }}
                .content p {{
                    color: #4a5568;
                    font-size: 16px;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                    margin: 20px 0;
                }}
                .info-box {{
                    background: #f7fafc;
                    border-left: 4px solid #667eea;
                    padding: 16px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info-box p {{
                    margin: 0;
                    font-size: 14px;
                    color: #4a5568;
                }}
                .footer {{
                    background: #f7fafc;
                    padding: 20px 30px;
                    text-align: center;
                    color: #718096;
                    font-size: 14px;
                }}
                .link {{
                    color: #667eea;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ PhishGuard AI</h1>
                </div>
                <div class="content">
                    <h2>Bienvenue, {user.username}!</h2>
                    <p>Merci de vous être inscrit sur PhishGuard AI. Pour activer votre compte, veuillez vérifier votre adresse email en cliquant sur le bouton ci-dessous:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">Vérifier mon Email</a>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>⏰ Ce lien est valide pendant 24 heures</strong></p>
                        <p>Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.</p>
                    </div>
                    
                    <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur:</p>
                    <p class="link">{verification_link}</p>
                </div>
                <div class="footer">
                    <p>© 2026 PhishGuard AI - Protection contre le phishing</p>
                    <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Bienvenue sur PhishGuard AI!
        
        Merci de vous être inscrit, {user.username}.
        
        Pour activer votre compte, veuillez vérifier votre adresse email en cliquant sur ce lien:
        {verification_link}
        
        Ce lien est valide pendant 24 heures.
        
        Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.
        
        © 2026 PhishGuard AI
        """
        
        # Send email
        return await email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_body,
            text_content=text_body
        )


# Singleton instance
email_verification_service = EmailVerificationService()
