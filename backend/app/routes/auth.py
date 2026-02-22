"""
Authentication routes
Handles user registration, login, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import timedelta, datetime
import logging

from app.models.auth_schemas import UserCreate, UserLogin, UserResponse, Token, UserUpdate, AccountDeleteRequest, RegistrationResponse
from app.models.user_models import User
from app.services.auth_service import (
    auth_service,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.database import get_db
from app.services.notification_service import notification_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Password (minimum 6 characters)
    - **full_name**: Optional full name
    
    Sends verification email - user must verify before logging in
    """
    try:
        # Check if username already exists
        existing_user = await auth_service.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = await auth_service.get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user (email_verified defaults to False)
        user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        await db.flush()
        
        # Create verification token and send email
        from app.services.email_verification_service import email_verification_service
        token = await email_verification_service.create_verification_token(db, user)
        email_sent = await email_verification_service.send_verification_email(user, token)
        
        if email_sent:
            logger.info(f"Verification email sent to {user.email}")
        else:
            logger.error(f"Failed to send verification email to {user.email}")
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"New user registered: {user.username}")
        
        # Return success without token - user must verify email first
        return {
            "message": "Inscription réussie! Veuillez vérifier votre email pour activer votre compte.",
            "email": user.email,
            "username": user.username
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token, tags=["Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Login with username and password
    
    Returns JWT access token
    If 2FA is enabled, requires totp_code in scopes field
    """
    try:
        # Get client IP for brute force detection
        client_ip = request.client.host if request and request.client else 'Unknown'
        if request:
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                client_ip = forwarded_for.split(',')[0].strip()
        
        # Check if IP is blocked due to brute force
        from app.middleware.rate_limiter import rate_limiter
        if rate_limiter.is_ip_blocked(client_ip):
            logger.warning(f"Blocked login attempt from brute force IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your IP has been temporarily blocked due to multiple failed login attempts. Please try again later.",
                headers={"X-Blocked-Reason": "brute-force"}
            )
        
        user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            # Record failed login attempt
            is_brute_force = await rate_limiter.record_failed_login(client_ip, form_data.username)
            
            # If brute force detected, send alert
            if is_brute_force:
                logger.critical(f"Brute force attack detected from IP: {client_ip}")
                
                # Send notification asynchronously
                import asyncio
                from app.services.notification_service import notification_service
                from app.utils.geolocation import get_location_from_ip
                from app.database import get_db as get_notification_db
                
                async def send_brute_force_alert_background():
                    """Background task to send brute force alert with its own DB session"""
                    async for notification_db in get_notification_db():
                        try:
                            # Get attack stats
                            stats = rate_limiter.get_brute_force_stats(client_ip)
                            
                            # Get location
                            location = await get_location_from_ip(client_ip)
                            
                            # Prepare attack details
                            attack_details = {
                                'ip_address': client_ip,
                                'failed_attempts': stats['failed_attempts'],
                                'threshold': stats['threshold'],
                                'window_seconds': stats['window_seconds'],
                                'usernames_attempted': stats['usernames_attempted'],
                                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                                'is_blocked': stats['is_blocked'],
                                'block_duration': rate_limiter.brute_force_block_duration,
                                'pattern': stats['pattern'],
                                'location': location
                            }
                            
                            # Send alert (email + in-app)
                            await notification_service.send_brute_force_alert(attack_details, notification_db)
                            break  # Exit after first successful iteration
                        except Exception as e:
                            logger.error(f"Failed to send brute force alert: {str(e)}", exc_info=True)
                            break
                
                # Start background task
                asyncio.create_task(send_brute_force_alert_background())
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Check if email is verified
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email non vérifié. Veuillez vérifier votre email avant de vous connecter.",
                headers={"X-Email-Verified": "false"}
            )
        
        # Check if user is banned
        if user.is_banned:
            ban_message = f"Account has been banned"
            if user.ban_reason:
                ban_message += f": {user.ban_reason}"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ban_message
            )
        
        # Check if 2FA is enabled
        if user.two_factor_enabled:
            # Get TOTP code from scopes (we use this field to pass the 2FA code)
            totp_code = form_data.scopes[0] if form_data.scopes else None
            
            if not totp_code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="2FA code required",
                    headers={"X-2FA-Required": "true"}
                )
            
            # Import 2FA service
            from app.services.two_factor_service import two_factor_service
            
            # Try TOTP verification first
            is_valid = two_factor_service.verify_totp(user.two_factor_secret, totp_code)
            
            # If TOTP fails, try backup code
            if not is_valid:
                is_valid = two_factor_service.verify_backup_code(user, totp_code)
                if is_valid:
                    # Backup code was used, save the updated codes
                    await db.commit()
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA code",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Update last login timestamp
        from app.services.session_service import session_service
        
        # Check if this is first login
        is_first_login = user.is_first_login if hasattr(user, 'is_first_login') else False
        
        # Detect email provider from user's email
        suggested_provider = None
        if is_first_login:
            email_domain = user.email.lower().split('@')[-1]
            if 'gmail.com' in email_domain:
                suggested_provider = 'gmail'
            elif 'outlook.com' in email_domain or 'hotmail.com' in email_domain or 'live.com' in email_domain:
                suggested_provider = 'outlook'
            
            # Mark first login as complete
            user.is_first_login = False
        
        user.last_login = datetime.utcnow()
        
        # Create session and get JTI
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Use the actual request object for session tracking
        session, jti = await session_service.create_session(
            db, user, request, access_token_expires
        )
        
        await db.commit()
        await db.refresh(user)
        
        # Create access token with JTI
        access_token = auth_service.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
            jti=jti
        )
        
        # Get client IP address
        client_ip = request.client.host if request and request.client else 'Unknown'
        # Check for forwarded IP (if behind proxy)
        if request:
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                client_ip = forwarded_for.split(',')[0].strip()
        
        # Get user agent
        user_agent = request.headers.get('User-Agent', 'Unknown Device') if request else 'Unknown Device'
        
        # Extract user data before background task (avoid lazy loading issues)
        user_id = user.id
        
        # Send new login notification (async, don't wait)
        # Note: We don't pass db session to background task - it will create its own
        try:
            import asyncio
            from app.database import get_db as get_notification_db
            from app.utils.geolocation import get_location_from_ip
            
            async def send_login_notification_background():
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
                        
                        await notification_service.send_new_login_alert(
                            db=notification_db,
                            user=fresh_user,
                            login_details={
                                'device': user_agent[:50],
                                'browser': user_agent[:50],
                                'location': location,
                                'ip_address': client_ip,
                                'login_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                            }
                        )
                    finally:
                        await notification_db.close()
                    break
            
            asyncio.create_task(send_login_notification_background())
        except Exception as e:
            logger.error(f"Failed to queue login notification: {str(e)}")
        
        logger.info(f"User logged in: {user.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            is_first_login=is_first_login,
            suggested_provider=suggested_provider
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Requires authentication
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, tags=["Authentication"])
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Update current user information
    
    Requires authentication
    """
    try:
        # Update email if provided
        if user_update.email and user_update.email != current_user.email:
            existing_email = await auth_service.get_user_by_email(db, user_update.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            current_user.email = user_update.email
        
        # Update full name if provided
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name
        
        # Update password if provided
        if user_update.password:
            # Verify old password is provided
            if not user_update.old_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is required to change password"
                )
            
            # Verify old password is correct
            if not auth_service.verify_password(user_update.old_password, current_user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is incorrect"
                )
            
            # Update to new password
            current_user.hashed_password = auth_service.get_password_hash(user_update.password)
            
            # Get client IP address
            client_ip = request.client.host if request and request.client else 'Unknown'
            # Check for forwarded IP (if behind proxy)
            if request:
                forwarded_for = request.headers.get('X-Forwarded-For')
                if forwarded_for:
                    client_ip = forwarded_for.split(',')[0].strip()
            
            # Extract user data before background task (avoid lazy loading issues)
            user_id = current_user.id
            user_email = current_user.email
            username = current_user.username
            
            # Send password changed notification (async, don't wait)
            # Note: We don't pass db session to background task - it will create its own
            try:
                import asyncio
                from app.database import get_db
                from app.utils.geolocation import get_location_from_ip
                
                async def send_notification_background():
                    """Background task to send notification with its own DB session"""
                    async for notification_db in get_db():
                        try:
                            # Fetch fresh user object in this session
                            from sqlalchemy import select
                            result = await notification_db.execute(
                                select(User).where(User.id == user_id)
                            )
                            fresh_user = result.scalar_one()
                            
                            # Get location from IP
                            location = await get_location_from_ip(client_ip)
                            
                            await notification_service.send_password_changed_alert(
                                db=notification_db,
                                user=fresh_user,
                                change_details={
                                    'changed_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                                    'ip_address': client_ip,
                                    'location': location
                                }
                            )
                        finally:
                            await notification_db.close()
                        break
                
                asyncio.create_task(send_notification_background())
            except Exception as e:
                logger.error(f"Failed to queue password change notification: {str(e)}")
        
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"User updated: {current_user.username}")
        
        return UserResponse.model_validate(current_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update failed"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, tags=["Authentication"])
async def delete_current_user(
    delete_request: AccountDeleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user account permanently
    
    Requires:
    - Password verification
    - Confirmation text: "DELETE MY ACCOUNT"
    
    This action is irreversible and will:
    - Delete all user data
    - Delete all analysis history
    - Delete all sessions
    - Delete email provider connections
    """
    try:
        # Verify password
        if not auth_service.verify_password(delete_request.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Verify confirmation text
        if delete_request.confirmation != "DELETE MY ACCOUNT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation text must be exactly 'DELETE MY ACCOUNT'"
            )
        
        # Log the deletion for audit
        logger.warning(f"Account deletion initiated for user: {current_user.username} (ID: {current_user.id})")
        
        # Use direct DELETE statements to avoid ORM cascade issues
        from sqlalchemy import delete
        from app.models.session_models import UserSession
        from app.models.email_provider_models import UserEmailCredential
        from app.models.database_models import AnalysisHistory
        from app.models.audit_models import AuditLog
        
        user_id = current_user.id
        
        # Expunge current_user from session to avoid tracking issues
        db.expunge(current_user)
        
        # Delete all user sessions using direct DELETE
        await db.execute(
            delete(UserSession).where(UserSession.user_id == user_id)
        )
        
        # Delete email provider credentials
        await db.execute(
            delete(UserEmailCredential).where(UserEmailCredential.user_id == user_id)
        )
        
        # Delete analysis history
        await db.execute(
            delete(AnalysisHistory).where(AnalysisHistory.user_id == user_id)
        )
        
        # Delete audit logs where user is actor or target
        await db.execute(
            delete(AuditLog).where(
                (AuditLog.actor_id == user_id) | (AuditLog.target_user_id == user_id)
            )
        )
        
        # Delete user
        await db.execute(
            delete(User).where(User.id == user_id)
        )
        
        await db.commit()
        
        logger.info(f"Account successfully deleted: {current_user.username}")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deletion failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )
