"""
Authentication routes
Handles user registration, login, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import timedelta, datetime, timezone
import logging

from app.models.auth_schemas import UserCreate, UserLogin, UserResponse, Token, UserUpdate, AccountDeactivateRequest, RegistrationResponse
from app.models.user_models import User
from app.services.auth_service import (
    auth_service,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
)
from app.database import get_db
from app.services.notification_service import notification_service
from jose import jwt, JWTError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Password (minimum 8 characters)
    
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
            password=user_data.password
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
                                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
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

            # ── Per-user failed-login tracking (alerts the TARGET user) ──
            # Look up whether this username actually exists so we can warn the
            # real account owner when someone is trying to break in.
            target_user = await auth_service.get_user_by_username(db, form_data.username)
            if target_user:
                user_alert_triggered = await rate_limiter.record_failed_login_per_user(
                    client_ip, form_data.username
                )
                if user_alert_triggered:
                    async def send_user_failed_login_alert_background():
                        async for notification_db in get_notification_db():
                            try:
                                from sqlalchemy import select
                                result = await notification_db.execute(
                                    select(User).where(User.id == target_user.id)
                                )
                                fresh_user = result.scalar_one()

                                stats = rate_limiter.get_user_failed_login_stats(
                                    form_data.username
                                )
                                location = await get_location_from_ip(client_ip)

                                await notification_service.send_failed_login_attempts_alert(
                                    db=notification_db,
                                    user=fresh_user,
                                    attempt_details={
                                        'failed_count': stats['failed_attempts'],
                                        'threshold': stats['threshold'],
                                        'ip_address': client_ip,
                                        'location': location,
                                        'last_attempt_at': datetime.now(timezone.utc).strftime(
                                            '%Y-%m-%d %H:%M:%S UTC'
                                        ),
                                    }
                                )
                                break
                            except Exception as e:
                                logger.error(
                                    f"Failed to send per-user failed-login alert: {str(e)}",
                                    exc_info=True,
                                )
                                break

                    asyncio.create_task(send_user_failed_login_alert_background())

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is banned (priority over deactivation - banned users cannot reactivate themselves)
        if user.is_banned:
            ban_message = f"Account has been banned"
            if user.ban_reason:
                ban_message += f": {user.ban_reason}"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ban_message
            )
        
        # Check if account is deactivated - offer reactivation
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ACCOUNT_DEACTIVATED",
                headers={"X-Reactivation-Required": "true"}
            )
        
        # Check if email is verified
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email non vérifié. Veuillez vérifier votre email avant de vous connecter.",
                headers={"X-Email-Verified": "false"}
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
        
        user.last_login = datetime.now(timezone.utc)
        
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
                """Background task to send notification with its own DB session.

                Also persists the resolved geolocation onto the freshly-created
                `user_sessions` row so the UI's "Gestion des Sessions" can show it.

                Only fires the new-login alert if the (user, IP, device) combination
                has never been seen before. This avoids the previous behaviour where
                EVERY login produced a notification, training users to ignore them.
                """
                async for notification_db in get_notification_db():
                    try:
                        # Resolve location once for both the session row and the alert
                        location = await get_location_from_ip(client_ip)

                        # Persist location on the freshly-created session
                        try:
                            from sqlalchemy import update as sql_update
                            from app.models.session_models import UserSession
                            await notification_db.execute(
                                sql_update(UserSession)
                                .where(UserSession.token_jti == jti)
                                .values(location=location)
                            )
                            await notification_db.commit()
                        except Exception as loc_err:
                            logger.warning(
                                f"Failed to persist session location for jti={jti}: {loc_err}"
                            )

                        # Skip the alert if this device has been seen before for this user.
                        # We exclude the freshly-created session (jti) so it doesn't
                        # falsely match itself.
                        already_known = await session_service.is_known_device(
                            db=notification_db,
                            user_id=user_id,
                            ip_address=client_ip,
                            user_agent=user_agent,
                            exclude_jti=jti,
                        )
                        if already_known:
                            logger.info(
                                f"Login from known device for user {user_id} "
                                f"(IP={client_ip}) — alert suppressed"
                            )
                            return

                        # New device → fetch user and fire the alert
                        from sqlalchemy import select
                        result = await notification_db.execute(
                            select(User).where(User.id == user_id)
                        )
                        fresh_user = result.scalar_one()

                        await notification_service.send_new_login_alert(
                            db=notification_db,
                            user=fresh_user,
                            login_details={
                                'device': user_agent[:50],
                                'browser': user_agent[:50],
                                'location': location,
                                'ip_address': client_ip,
                                'login_time': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
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


@router.post("/reactivate", response_model=Token, tags=["Authentication"])
async def reactivate_account(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Reactivate a deactivated account and log the user in.
    
    Requires:
    - Valid username + password
    - 2FA code (if 2FA was enabled before deactivation) via the `scope` field
    
    The account must be currently deactivated (is_active = False) and not banned.
    On success: sets is_active = True, creates a session and returns a JWT token.
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Banned users cannot self-reactivate
        if user.is_banned:
            ban_message = "Account has been banned"
            if user.ban_reason:
                ban_message += f": {user.ban_reason}"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ban_message
            )
        
        # Account must be deactivated to be reactivated
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le compte est déjà actif"
            )
        
        # Check 2FA (preserved from before deactivation)
        if user.two_factor_enabled:
            totp_code = form_data.scopes[0] if form_data.scopes else None
            
            if not totp_code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="2FA code required",
                    headers={"X-2FA-Required": "true"}
                )
            
            from app.services.two_factor_service import two_factor_service
            
            is_valid = two_factor_service.verify_totp(user.two_factor_secret, totp_code)
            if not is_valid:
                is_valid = two_factor_service.verify_backup_code(user, totp_code)
                if is_valid:
                    await db.commit()
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA code",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Reactivate the account
        user.is_active = True
        user.last_login = datetime.now(timezone.utc)
        
        logger.info(f"Account reactivated by user: {user.username} (ID: {user.id})")
        
        # Create session
        from app.services.session_service import session_service
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        session, jti = await session_service.create_session(
            db, user, request, access_token_expires
        )
        
        await db.commit()
        await db.refresh(user)
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
            jti=jti
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            is_first_login=False,
            suggested_provider=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account reactivation failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La réactivation du compte a échoué"
        )


@router.post("/logout", status_code=status.HTTP_200_OK, tags=["Authentication"])
async def logout(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout the current user by revoking the active session.

    The JWT remains cryptographically valid until its `exp`, but the matching
    `user_sessions` row is marked `is_active=False`, so any further request
    using this token will be rejected by `get_current_user` (401).
    """
    try:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            # Token invalid → nothing to revoke, but treat as success for idempotency
            return {"message": "Logged out"}

        jti = payload.get("jti")
        if not jti:
            # Legacy token without JTI — nothing to revoke server-side
            return {"message": "Logged out"}

        from app.services.session_service import session_service
        revoked = await session_service.revoke_session_by_jti(
            db, jti=jti, user_id=current_user.id
        )
        await db.commit()

        if revoked:
            logger.info(f"User logged out: {current_user.username} (jti={jti})")
        return {"message": "Logged out"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Logout failed for {current_user.username}: {str(e)}", exc_info=True)
        # Never block client-side logout on server errors
        return {"message": "Logged out"}


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
        old_email = None
        if user_update.email and user_update.email != current_user.email:
            existing_email = await auth_service.get_user_by_email(db, user_update.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            old_email = current_user.email
            current_user.email = user_update.email
        
        # Update username if provided
        if user_update.username and user_update.username != current_user.username:
            existing_username = await auth_service.get_user_by_username(db, user_update.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            current_user.username = user_update.username
        
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
                                    'changed_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
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

        # ── Email changed notification ──
        if old_email:
            try:
                # Reuse the same IP extraction logic
                email_change_ip = request.client.host if request and request.client else 'Unknown'
                if request:
                    forwarded_for = request.headers.get('X-Forwarded-For')
                    if forwarded_for:
                        email_change_ip = forwarded_for.split(',')[0].strip()

                # Capture data for background task before commit
                email_user_id = current_user.id
                email_old = old_email
                email_new = current_user.email
                email_username = current_user.username

                async def send_email_change_notification_background():
                    async for notification_db in get_db():
                        try:
                            from sqlalchemy import select
                            result = await notification_db.execute(
                                select(User).where(User.id == email_user_id)
                            )
                            fresh_user = result.scalar_one()

                            location = await get_location_from_ip(email_change_ip)

                            await notification_service.send_email_changed_alert(
                                db=notification_db,
                                user=fresh_user,
                                old_email=email_old,
                                new_email=email_new,
                                change_details={
                                    'changed_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                                    'ip_address': email_change_ip,
                                    'location': location,
                                }
                            )
                        finally:
                            await notification_db.close()
                        break

                asyncio.create_task(send_email_change_notification_background())
            except Exception as e:
                logger.error(f"Failed to queue email change notification: {str(e)}")

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


@router.put("/me/deactivate", status_code=status.HTTP_200_OK, tags=["Authentication"])
async def deactivate_current_user(
    deactivate_request: AccountDeactivateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate current user account
    
    Requires:
    - Password verification
    
    This action will:
    - Deactivate the account (is_active = False)
    - Invalidate all active sessions
    - The account can be reactivated by a SuperAdmin
    """
    try:
        # Verify password
        if not auth_service.verify_password(deactivate_request.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe incorrect"
            )
        
        # Log the deactivation
        logger.warning(f"Account deactivation initiated for user: {current_user.username} (ID: {current_user.id})")
        if deactivate_request.reason:
            logger.info(f"Deactivation reason: {deactivate_request.reason}")
        
        # Deactivate the user account
        current_user.is_active = False
        
        # Invalidate all active sessions
        from app.models.session_models import UserSession
        from sqlalchemy import update
        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == current_user.id, UserSession.is_active == True)
            .values(is_active=False)
        )
        
        await db.commit()
        
        logger.info(f"Account successfully deactivated: {current_user.username}")
        
        return {"message": "Votre compte a été désactivé avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deactivation failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La désactivation du compte a échoué"
        )
