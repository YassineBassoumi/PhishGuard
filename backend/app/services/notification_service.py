"""
Notification Service
Handles sending email notifications to users
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notification_models import NotificationPreference, NotificationHistory
from app.models.user_models import User, UserRole
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

# Setup Jinja2 environment for email templates
template_dir = os.path.join(os.path.dirname(__file__), 'email_templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))


class NotificationService:
    """Service for managing and sending notifications"""
    
    def __init__(self):
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    async def get_or_create_preferences(
        self,
        db: AsyncSession,
        user_id: int
    ) -> NotificationPreference:
        """Get user notification preferences or create default ones"""
        try:
            result = await db.execute(
                select(NotificationPreference).where(
                    NotificationPreference.user_id == user_id
                )
            )
            preferences = result.scalar_one_or_none()
            
            if not preferences:
                # Create default preferences
                preferences = NotificationPreference(user_id=user_id)
                db.add(preferences)
                await db.commit()
                await db.refresh(preferences)
                logger.info(f"Created default notification preferences for user {user_id}")
            
            return preferences
        except Exception as e:
            logger.error(f"Failed to get/create preferences: {str(e)}", exc_info=True)
            raise
    
    async def _log_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        subject: str,
        status: str = 'sent',
        error_message: Optional[str] = None
    ):
        """Log notification to history"""
        try:
            history = NotificationHistory(
                user_id=user_id,
                notification_type=notification_type,
                subject=subject,
                status=status,
                error_message=error_message
            )
            db.add(history)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")
    
    async def send_new_login_alert(
        self,
        db: AsyncSession,
        user: User,
        login_details: Dict
    ) -> bool:
        """
        Send alert for new login from unknown device
        
        Args:
            db: Database session
            user: User object
            login_details: Dict with login info (device, browser, location, ip_address, login_time)
        """
        try:
            # Get user preferences
            preferences = await self.get_or_create_preferences(db, user.id)
            
            if not preferences.email_notifications_enabled or not preferences.new_login_alerts:
                logger.info(f"New login alerts disabled for user {user.id}")
                return False
            
            # Determine recipient email
            recipient_email = preferences.notification_email or user.email
            
            # Prepare template data
            template_data = {
                'username': user.username,
                'device': login_details.get('device', 'Unknown Device'),
                'browser': login_details.get('browser', 'Unknown Browser'),
                'location': login_details.get('location', 'Unknown Location'),
                'ip_address': login_details.get('ip_address', 'Unknown'),
                'login_time': login_details.get('login_time', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
                'confirm_url': f"{self.frontend_url}/settings",
                'secure_url': f"{self.frontend_url}/settings?action=secure"
            }
            
            # Render email template
            template = jinja_env.get_template('new_login_alert.html')
            html_content = template.render(**template_data)
            
            # Send email
            subject = "🔐 New Login Detected on Your PhishGuard Account"
            success = await email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Log notification
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='new_login_alert',
                subject=subject,
                status='sent' if success else 'failed',
                error_message=None if success else 'Failed to send email'
            )
            
            if success:
                logger.info(f"Sent new login alert to user {user.id}")
            else:
                logger.error(f"Failed to send new login alert to user {user.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending new login alert: {str(e)}", exc_info=True)
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='new_login_alert',
                subject='New Login Alert',
                status='failed',
                error_message=str(e)
            )
            return False
    
    async def send_password_changed_alert(
        self,
        db: AsyncSession,
        user: User,
        change_details: Dict
    ) -> bool:
        """
        Send alert when password is changed
        
        Args:
            db: Database session
            user: User object
            change_details: Dict with change info (ip_address, location, changed_at)
        """
        try:
            # Get user preferences
            preferences = await self.get_or_create_preferences(db, user.id)
            
            if not preferences.email_notifications_enabled or not preferences.password_change_alerts:
                logger.info(f"Password change alerts disabled for user {user.id}")
                return False
            
            # Determine recipient email
            recipient_email = preferences.notification_email or user.email
            
            # Prepare template data
            template_data = {
                'username': user.username,
                'changed_at': change_details.get('changed_at', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
                'ip_address': change_details.get('ip_address', 'Unknown'),
                'location': change_details.get('location', 'Unknown Location'),
                'secure_url': f"{self.backend_url}/api/security/secure-account/{user.id}"
            }
            
            # Render email template
            template = jinja_env.get_template('password_changed_alert.html')
            html_content = template.render(**template_data)
            
            # Send email
            subject = "✅ Your PhishGuard Password Was Changed"
            success = await email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Log notification
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='password_changed_alert',
                subject=subject,
                status='sent' if success else 'failed',
                error_message=None if success else 'Failed to send email'
            )
            
            if success:
                logger.info(f"Sent password changed alert to user {user.id}")
            else:
                logger.error(f"Failed to send password changed alert to user {user.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending password changed alert: {str(e)}", exc_info=True)
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='password_changed_alert',
                subject='Password Changed Alert',
                status='failed',
                error_message=str(e)
            )
            return False
    
    async def send_two_factor_changed_alert(
        self,
        db: AsyncSession,
        user: User,
        action: str,  # 'Enabled' or 'Disabled'
        change_details: Dict
    ) -> bool:
        """
        Send alert when 2FA is enabled or disabled
        
        Args:
            db: Database session
            user: User object
            action: 'Enabled' or 'Disabled'
            change_details: Dict with change info (ip_address, location, changed_at)
        """
        try:
            # Get user preferences
            preferences = await self.get_or_create_preferences(db, user.id)
            
            if not preferences.email_notifications_enabled or not preferences.two_factor_change_alerts:
                logger.info(f"2FA change alerts disabled for user {user.id}")
                return False
            
            # Determine recipient email
            recipient_email = preferences.notification_email or user.email
            
            # Prepare template data
            template_data = {
                'username': user.username,
                'action': action,
                'status': 'enabled' if action == 'Enabled' else 'disabled',
                'status_text': 'ENABLED' if action == 'Enabled' else 'DISABLED',
                'changed_at': change_details.get('changed_at', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
                'ip_address': change_details.get('ip_address', 'Unknown'),
                'location': change_details.get('location', 'Unknown Location'),
                'secure_url': f"{self.frontend_url}/settings?action=secure"
            }
            
            # Render email template
            template = jinja_env.get_template('two_factor_changed_alert.html')
            html_content = template.render(**template_data)
            
            # Send email
            subject = f"🔐 Two-Factor Authentication {action} on Your Account"
            success = await email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Log notification
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='two_factor_changed_alert',
                subject=subject,
                status='sent' if success else 'failed',
                error_message=None if success else 'Failed to send email'
            )
            
            if success:
                logger.info(f"Sent 2FA {action.lower()} alert to user {user.id}")
            else:
                logger.error(f"Failed to send 2FA {action.lower()} alert to user {user.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending 2FA changed alert: {str(e)}", exc_info=True)
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='two_factor_changed_alert',
                subject=f'2FA {action} Alert',
                status='failed',
                error_message=str(e)
            )
            return False
    
    async def send_email_changed_alert(
        self,
        db: AsyncSession,
        user: User,
        old_email: str,
        new_email: str,
        change_details: Dict
    ) -> bool:
        """
        Send alert when the user's account email is changed.

        IMPORTANT: This sends to BOTH the old and new email addresses.
        - Old address: so the legitimate owner is warned if a hijacker swapped the email.
        - New address: confirmation that the change happened.

        Args:
            db: Database session
            user: User object (already updated with new_email)
            old_email: Email address before the change
            new_email: Email address after the change
            change_details: Dict with change info (ip_address, location, changed_at)
        """
        try:
            preferences = await self.get_or_create_preferences(db, user.id)
            if not preferences.email_notifications_enabled:
                logger.info(f"Email notifications disabled for user {user.id}")
                return False

            template_data = {
                'username': user.username,
                'old_email': old_email,
                'new_email': new_email,
                'changed_at': change_details.get('changed_at', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
                'ip_address': change_details.get('ip_address', 'Unknown'),
                'location': change_details.get('location', 'Unknown Location'),
                'secure_url': f"{self.frontend_url}/settings?action=secure"
            }

            template = jinja_env.get_template('email_changed_alert.html')
            html_content = template.render(**template_data)

            subject = "⚠️ Your PhishGuard Account Email Was Changed"

            # Send to BOTH addresses so the legitimate owner is warned even if attacker swapped the email
            success_old = await email_service.send_email(
                to_email=old_email,
                subject=subject,
                html_content=html_content
            )
            success_new = await email_service.send_email(
                to_email=new_email,
                subject=subject,
                html_content=html_content
            )

            success = success_old or success_new

            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='email_changed_alert',
                subject=f"Account email changed from {old_email} to {new_email}",
                status='sent' if success else 'failed',
                error_message=None if success else 'Failed to send to both addresses'
            )

            if success:
                logger.info(
                    f"Email change alert sent for user {user.id}: old={success_old}, new={success_new}"
                )
            else:
                logger.error(f"Failed to send email change alert to user {user.id}")

            return success

        except Exception as e:
            logger.error(f"Error sending email changed alert: {str(e)}", exc_info=True)
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='email_changed_alert',
                subject='Email Changed Alert',
                status='failed',
                error_message=str(e)
            )
            return False

    async def send_failed_login_attempts_alert(
        self,
        db: AsyncSession,
        user: User,
        attempt_details: Dict
    ) -> bool:
        """
        Notify a user when there have been multiple failed login attempts ON THEIR account.

        This is different from `brute_force_alert` (which goes to admins for IP-wide attacks).
        Here, the legitimate user is warned that someone is trying to break into THEIR account.

        Args:
            db: Database session
            user: User object (the target of the failed attempts)
            attempt_details: Dict with info (failed_count, ip_address, location, last_attempt_at, threshold)
        """
        try:
            preferences = await self.get_or_create_preferences(db, user.id)
            if not preferences.email_notifications_enabled:
                logger.info(f"Email notifications disabled for user {user.id}")
                return False

            recipient_email = preferences.notification_email or user.email

            template_data = {
                'username': user.username,
                'failed_count': attempt_details.get('failed_count', 0),
                'threshold': attempt_details.get('threshold', 3),
                'ip_address': attempt_details.get('ip_address', 'Unknown'),
                'location': attempt_details.get('location', 'Unknown Location'),
                'last_attempt_at': attempt_details.get(
                    'last_attempt_at',
                    datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                ),
                'secure_url': f"{self.frontend_url}/settings?action=secure"
            }

            template = jinja_env.get_template('failed_login_attempts_alert.html')
            html_content = template.render(**template_data)

            subject = f"🚨 {template_data['failed_count']} failed login attempts on your PhishGuard account"
            success = await email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content
            )

            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='failed_login_attempts_alert',
                subject=subject,
                status='sent' if success else 'failed',
                error_message=None if success else 'Failed to send email'
            )

            if success:
                logger.info(f"Sent failed-login-attempts alert to user {user.id}")
            else:
                logger.error(f"Failed to send failed-login-attempts alert to user {user.id}")

            return success

        except Exception as e:
            logger.error(f"Error sending failed-login-attempts alert: {str(e)}", exc_info=True)
            await self._log_notification(
                db=db,
                user_id=user.id,
                notification_type='failed_login_attempts_alert',
                subject='Failed Login Attempts Alert',
                status='failed',
                error_message=str(e)
            )
            return False

    async def send_database_error_alert(
        self,
        error_details: Dict
    ) -> bool:
        """
        Send critical alert to all admins and superadmins when database connection fails
        This is a system-level notification that doesn't require database access
        
        Args:
            error_details: Dict with error info (error_message, timestamp, operation, traceback)
        """
        try:
            # Since database is down, we can't query for admin users
            # We'll use a fallback email list from environment variables
            admin_emails = os.getenv("ADMIN_ALERT_EMAILS", "").split(",")
            admin_emails = [email.strip() for email in admin_emails if email.strip()]
            
            if not admin_emails:
                logger.error("No admin emails configured for database error alerts")
                return False
            
            # Prepare template data
            template_data = {
                'error_message': error_details.get('error_message', 'Unknown database error'),
                'timestamp': error_details.get('timestamp', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
                'operation': error_details.get('operation', 'Unknown operation'),
                'traceback': error_details.get('traceback', 'No traceback available'),
                'server_url': self.backend_url,
                'app_name': 'PhishGuard'
            }
            
            # Render email template
            template = jinja_env.get_template('database_error_alert.html')
            html_content = template.render(**template_data)
            
            # Send email to all admins
            subject = "🚨 CRITICAL: Database Connection Failed - PhishGuard"
            success_count = 0
            
            for admin_email in admin_emails:
                try:
                    success = await email_service.send_email(
                        to_email=admin_email,
                        subject=subject,
                        html_content=html_content
                    )
                    if success:
                        success_count += 1
                        logger.info(f"Sent database error alert to admin: {admin_email}")
                    else:
                        logger.error(f"Failed to send database error alert to admin: {admin_email}")
                except Exception as e:
                    logger.error(f"Error sending to {admin_email}: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending database error alert: {str(e)}", exc_info=True)
            return False
    
    async def send_brute_force_alert(
        self,
        attack_details: Dict,
        db: Optional[AsyncSession] = None
    ) -> bool:
        """
        Send critical alert to all admins when brute force attack is detected
        Sends both email alerts and in-app notifications
        
        Args:
            attack_details: Dict with attack info (ip_address, failed_attempts, usernames_attempted, 
                           timestamp, is_blocked, pattern)
            db: Optional database session for in-app notifications
        """
        try:
            # Get admin emails from environment for email alerts
            admin_emails = os.getenv("ADMIN_ALERT_EMAILS", "").split(",")
            admin_emails = [email.strip() for email in admin_emails if email.strip()]
            
            if not admin_emails:
                logger.error("No admin emails configured for brute force alerts")
                return False
            
            # Prepare template data
            template_data = {
                'ip_address': attack_details.get('ip_address', 'Unknown'),
                'failed_attempts': attack_details.get('failed_attempts', 0),
                'threshold': attack_details.get('threshold', 10),
                'window_minutes': attack_details.get('window_seconds', 300) // 60,
                'usernames_attempted': attack_details.get('usernames_attempted', []),
                'timestamp': attack_details.get('timestamp', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
                'is_blocked': attack_details.get('is_blocked', False),
                'block_duration_hours': attack_details.get('block_duration', 3600) // 3600,
                'pattern': attack_details.get('pattern', 'automated'),
                'location': attack_details.get('location', 'Unknown Location'),
                'server_url': self.backend_url,
                'app_name': 'PhishGuard'
            }
            
            # Render email template
            template = jinja_env.get_template('brute_force_alert.html')
            html_content = template.render(**template_data)
            
            # Send email to all admins
            subject = f"🚨 CRITICAL: Brute Force Attack Detected from {template_data['ip_address']}"
            email_success_count = 0
            
            for admin_email in admin_emails:
                try:
                    success = await email_service.send_email(
                        to_email=admin_email,
                        subject=subject,
                        html_content=html_content
                    )
                    if success:
                        email_success_count += 1
                        logger.info(f"Sent brute force email alert to admin: {admin_email}")
                    else:
                        logger.error(f"Failed to send brute force email alert to admin: {admin_email}")
                except Exception as e:
                    logger.error(f"Error sending email to {admin_email}: {str(e)}")
            
            # Add in-app notifications for admin users if database is available
            in_app_success_count = 0
            if db:
                try:
                    # Get all admin and superadmin users
                    admin_users = await self.get_admin_users(db)
                    
                    if admin_users:
                        # Create notification subject for in-app
                        usernames_str = ", ".join(attack_details.get('usernames_attempted', [])[:3])
                        if len(attack_details.get('usernames_attempted', [])) > 3:
                            usernames_str += f" +{len(attack_details.get('usernames_attempted', [])) - 3} more"
                        
                        in_app_subject = (
                            f"Brute Force Attack: {attack_details.get('failed_attempts', 0)} failed attempts "
                            f"from {attack_details.get('ip_address', 'Unknown')} "
                            f"targeting: {usernames_str or 'multiple accounts'}"
                        )
                        
                        # Log notification for each admin
                        for admin_user in admin_users:
                            try:
                                await self._log_notification(
                                    db=db,
                                    user_id=admin_user.id,
                                    notification_type='brute_force_alert',
                                    subject=in_app_subject,
                                    status='sent'
                                )
                                in_app_success_count += 1
                            except Exception as e:
                                logger.error(f"Failed to create in-app notification for admin {admin_user.id}: {str(e)}")
                        
                        logger.info(f"Created {in_app_success_count} in-app notifications for admins")
                except Exception as e:
                    logger.error(f"Error creating in-app notifications: {str(e)}", exc_info=True)
            
            # Consider success if at least one email was sent
            success = email_success_count > 0
            
            if success:
                logger.info(
                    f"Brute force alert sent: {email_success_count} emails, "
                    f"{in_app_success_count} in-app notifications"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending brute force alert: {str(e)}", exc_info=True)
            return False
    
    async def get_admin_users(self, db: AsyncSession) -> List[User]:
        """
        Get all admin and superadmin users for system notifications
        
        Args:
            db: Database session
            
        Returns:
            List of admin and superadmin users
        """
        try:
            result = await db.execute(
                select(User).where(
                    User.role.in_([UserRole.ADMIN, UserRole.SUPERADMIN]),
                    User.is_active == True,
                    User.is_banned == False
                )
            )
            admins = result.scalars().all()
            return admins
        except Exception as e:
            logger.error(f"Failed to get admin users: {str(e)}", exc_info=True)
            return []


# Singleton instance
notification_service = NotificationService()
