"""
Unified Email Service
Routes email operations to appropriate provider (Gmail, Outlook)
"""

from enum import Enum
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.services.gmail_service import gmail_service
from app.services.outlook_service import outlook_service
from app.models.email_provider_models import UserEmailCredential
from app.models.user_models import User

logger = logging.getLogger(__name__)


class EmailProvider(str, Enum):
    """Supported email providers"""
    GMAIL = 'gmail'
    OUTLOOK = 'outlook'


class UnifiedEmailService:
    """Unified service for multi-provider email operations"""
    
    def __init__(self):
        self.providers = {
            EmailProvider.GMAIL: gmail_service,
            EmailProvider.OUTLOOK: outlook_service,
        }
    
    def get_provider_service(self, provider: EmailProvider):
        """Get service instance for provider"""
        service = self.providers.get(provider)
        if not service:
            raise ValueError(f"Provider {provider} not supported")
        return service
    
    def get_authorization_url(self, provider: EmailProvider) -> str:
        """Get OAuth authorization URL for provider"""
        try:
            service = self.get_provider_service(provider)
            return service.get_authorization_url()
        except Exception as e:
            logger.error(f"Failed to get auth URL for {provider}: {str(e)}")
            raise
    
    async def get_user_credentials(
        self, 
        db: AsyncSession, 
        user_id: int, 
        provider: EmailProvider
    ) -> Optional[Dict]:
        """Get user's credentials for specific provider"""
        try:
            result = await db.execute(
                select(UserEmailCredential).where(
                    UserEmailCredential.user_id == user_id,
                    UserEmailCredential.provider == provider.value
                )
            )
            credential = result.scalar_one_or_none()
            
            if not credential:
                return None
            
            # Base credentials from database
            creds = {
                "token": credential.access_token,
                "refresh_token": credential.refresh_token,
                "token_expiry": credential.token_expiry,
                "email_address": credential.email_address
            }
            
            # Add provider-specific OAuth configuration needed for token refresh
            if provider == EmailProvider.GMAIL:
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                creds.update({
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
                })
            elif provider == EmailProvider.OUTLOOK:
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                creds.update({
                    "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
                    "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
                    "token_uri": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                    "scopes": ["https://graph.microsoft.com/Mail.Read"]
                })
            
            return creds
        except Exception as e:
            logger.error(f"Failed to get credentials for user {user_id}, provider {provider}: {str(e)}")
            return None
    
    async def store_user_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider,
        credentials: Dict
    ):
        """Store or update user credentials for provider"""
        try:
            from datetime import datetime, timezone
            from sqlalchemy.dialects.postgresql import insert
            
            # Convert token_expiry string to datetime if needed
            token_expiry = credentials.get('token_expiry')
            if token_expiry and isinstance(token_expiry, str):
                token_expiry = datetime.fromisoformat(token_expiry)
            
            # Prepare credential data
            credential_data = {
                'user_id': user_id,
                'provider': provider.value,
                'access_token': credentials.get('token'),
                'refresh_token': credentials.get('refresh_token'),
                'token_expiry': token_expiry,
                'email_address': credentials.get('email_address')
            }
            
            # Use PostgreSQL INSERT ... ON CONFLICT DO UPDATE (upsert)
            stmt = insert(UserEmailCredential).values(**credential_data)
            stmt = stmt.on_conflict_do_update(
                constraint='uq_user_provider',
                set_={
                    'access_token': stmt.excluded.access_token,
                    'refresh_token': stmt.excluded.refresh_token,
                    'token_expiry': stmt.excluded.token_expiry,
                    'email_address': stmt.excluded.email_address,
                    'updated_at': datetime.now(timezone.utc)
                }
            )
            
            await db.execute(stmt)
            await db.commit()
            logger.info(f"Stored credentials for user {user_id}, provider {provider}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to store credentials: {str(e)}", exc_info=True)
            raise
    
    async def fetch_emails(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider,
        max_results: int = 20
    ) -> Dict:
        """Fetch emails from specified provider"""
        try:
            # Get user credentials
            credentials = await self.get_user_credentials(db, user_id, provider)
            if not credentials:
                raise ValueError(f"No credentials found for provider {provider}")

            # Check if token is expired and refresh if needed
            credentials = await self._ensure_valid_token(db, user_id, provider, credentials)

            # Get provider service
            service = self.get_provider_service(provider)

            # Fetch emails (with one forced refresh retry on token rejection)
            try:
                emails = service.list_emails(credentials, max_results)
            except Exception as first_err:
                error_str = str(first_err)
                if 'token expired' in error_str.lower() or '401' in error_str:
                    logger.warning(f"Token rejected by {provider}, forcing refresh...")
                    credentials = await self._ensure_valid_token(
                        db, user_id, provider, credentials, force=True
                    )
                    emails = service.list_emails(credentials, max_results)
                else:
                    raise

            return {
                'success': True,
                'provider': provider.value,
                'emails': emails,
                'count': len(emails)
            }
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to fetch emails from {provider}: {error_str}", exc_info=True)
            
            # Check if it's an invalid_grant error (expired/revoked refresh token)
            if 'invalid_grant' in error_str.lower() or 'refresh' in error_str.lower():
                # Mark credentials as invalid and require re-authentication
                await self._mark_credentials_invalid(db, user_id, provider)
                return {
                    'success': False,
                    'provider': provider.value,
                    'error': 'REAUTH_REQUIRED',
                    'error_message': 'Your email connection has expired. Please reconnect your account.',
                    'requires_reauth': True,
                    'emails': [],
                    'count': 0
                }
            
            return {
                'success': False,
                'provider': provider.value,
                'error': error_str,
                'emails': [],
                'count': 0
            }
    
    async def get_email_content(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider,
        message_id: str
    ) -> str:
        """Get full email content from provider"""
        try:
            # Get user credentials
            credentials = await self.get_user_credentials(db, user_id, provider)
            if not credentials:
                raise ValueError(f"No credentials found for provider {provider}")
            
            # Check if token is expired and refresh if needed
            credentials = await self._ensure_valid_token(db, user_id, provider, credentials)
            
            # Get provider service
            service = self.get_provider_service(provider)
            
            # Fetch email content
            content = service.get_email_content(credentials, message_id)
            
            return content
        except Exception as e:
            logger.error(f"Failed to get email content from {provider}: {str(e)}", exc_info=True)
            raise
    
    async def _ensure_valid_token(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider,
        credentials: Dict,
        force: bool = False
    ) -> Dict:
        """
        Check if token is expired and refresh if needed

        Args:
            db: Database session
            user_id: User ID
            provider: Email provider
            credentials: Current credentials dictionary
            force: If True, always refresh regardless of expiry

        Returns:
            Updated credentials with fresh token
        """
        try:
            from datetime import datetime, timedelta, timezone

            if force:
                logger.info(f"Force-refreshing token for {provider}")
            else:
                # Check if token_expiry exists and is expired
                token_expiry = credentials.get('token_expiry')

                if not token_expiry:
                    # No expiry info, assume token is valid
                    logger.warning(f"No token expiry info for {provider}, assuming valid")
                    return credentials

                # Parse token_expiry if it's a string
                if isinstance(token_expiry, str):
                    try:
                        token_expiry = datetime.fromisoformat(token_expiry.replace('Z', '+00:00'))
                    except:
                        logger.warning(f"Could not parse token_expiry: {token_expiry}")
                        return credentials

                # Ensure token_expiry is timezone-aware (assume UTC if naive)
                if token_expiry.tzinfo is None:
                    token_expiry = token_expiry.replace(tzinfo=timezone.utc)

                # Check if token is expired or will expire in next 5 minutes
                now = datetime.now(timezone.utc)
                buffer = timedelta(minutes=5)

                if token_expiry > now + buffer:
                    # Token is still valid
                    logger.debug(f"Token for {provider} is still valid until {token_expiry}")
                    return credentials
            
            # Token is expired or about to expire, refresh it
            logger.info(f"Token for {provider} expired or expiring soon, refreshing...")
            
            refresh_token = credentials.get('refresh_token')
            if not refresh_token:
                raise ValueError(f"No refresh token available for {provider}")
            
            # Get provider service and refresh token
            service = self.get_provider_service(provider)
            
            if provider == EmailProvider.GMAIL:
                # Gmail uses google-auth library
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import Request
                
                creds = Credentials(
                    token=credentials.get('token'),
                    refresh_token=refresh_token,
                    token_uri=credentials.get('token_uri'),
                    client_id=credentials.get('client_id'),
                    client_secret=credentials.get('client_secret'),
                    scopes=credentials.get('scopes')
                )
                
                # Refresh the token
                creds.refresh(Request())
                
                # Update credentials
                credentials['token'] = creds.token
                credentials['token_expiry'] = creds.expiry
                
            elif provider == EmailProvider.OUTLOOK:
                # Outlook uses custom refresh method
                refreshed = service.refresh_access_token(refresh_token)
                
                # Update credentials
                credentials['token'] = refreshed['token']
                credentials['refresh_token'] = refreshed.get('refresh_token', refresh_token)
                credentials['token_expiry'] = refreshed['token_expiry']
            
            else:
                raise ValueError(f"Token refresh not implemented for {provider}")
            
            # Save updated credentials to database
            result = await db.execute(
                select(UserEmailCredential).where(
                    UserEmailCredential.user_id == user_id,
                    UserEmailCredential.provider == provider.value
                )
            )
            credential_record = result.scalar_one_or_none()
            
            if credential_record:
                # Persist refreshed token fields to the actual DB columns
                credential_record.access_token = credentials['token']
                credential_record.refresh_token = credentials['refresh_token']
                credential_record.token_expiry = credentials['token_expiry']
                await db.commit()
                logger.info(f"Successfully refreshed and saved token for {provider}")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to refresh token for {provider}: {str(e)}", exc_info=True)
            # Return original credentials and let the API call fail with proper error
            return credentials
    
    async def get_connected_providers(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[str]:
        """Get list of providers user has connected"""
        try:
            result = await db.execute(
                select(UserEmailCredential.provider).where(
                    UserEmailCredential.user_id == user_id
                )
            )
            providers = [row[0] for row in result.all()]
            return providers
        except Exception as e:
            logger.error(f"Failed to get connected providers: {str(e)}")
            return []
    
    async def disconnect_provider(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider
    ):
        """Disconnect/remove provider credentials"""
        try:
            result = await db.execute(
                select(UserEmailCredential).where(
                    UserEmailCredential.user_id == user_id,
                    UserEmailCredential.provider == provider.value
                )
            )
            credential = result.scalar_one_or_none()
            
            if credential:
                await db.delete(credential)
                await db.commit()
                logger.info(f"Disconnected provider {provider} for user {user_id}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to disconnect provider: {str(e)}", exc_info=True)
            raise
    
    async def _mark_credentials_invalid(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider
    ):
        """
        Mark credentials as invalid (requires re-authentication)
        This is called when refresh token is expired/revoked
        """
        try:
            result = await db.execute(
                select(UserEmailCredential).where(
                    UserEmailCredential.user_id == user_id,
                    UserEmailCredential.provider == provider.value
                )
            )
            credential = result.scalar_one_or_none()
            
            if credential:
                # Delete the invalid credentials to force re-authentication
                await db.delete(credential)
                await db.commit()
                logger.info(f"Marked credentials as invalid for user {user_id}, provider {provider}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to mark credentials invalid: {str(e)}", exc_info=True)
    
    async def search_emails(
        self,
        db: AsyncSession,
        user_id: int,
        provider: EmailProvider,
        filters: Dict,
        max_results: int = 50
    ) -> Dict:
        """
        Search emails using provider's native search API
        
        Args:
            db: Database session
            user_id: User ID
            provider: Email provider
            filters: Search filters dict with keys:
                - q: General search query (searches subject, sender, body)
                - from_email: Sender email or name
                - subject: Subject keywords
                - date_from: Start date (YYYY-MM-DD)
                - date_to: End date (YYYY-MM-DD)
                - has_attachments: Boolean
            max_results: Maximum number of results
            
        Returns:
            Dict with success status, emails list, and match count
        """
        try:
            # Get user credentials
            credentials = await self.get_user_credentials(db, user_id, provider)
            if not credentials:
                raise ValueError(f"No credentials found for provider {provider}")
            
            # Check if token is expired and refresh if needed
            credentials = await self._ensure_valid_token(db, user_id, provider, credentials)
            
            # Get provider service
            service = self.get_provider_service(provider)
            
            # Use provider's native search API - searches ALL emails!
            logger.info(f"Using native {provider.value} search API with filters: {filters}")
            emails = service.search_emails(credentials, filters, max_results)
            
            return {
                'success': True,
                'provider': provider.value,
                'emails': emails,
                'count': len(emails),
                'filters_applied': filters,
                'search_method': 'native_api'
            }
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to search emails from {provider}: {error_str}", exc_info=True)
            
            # Check if it's an invalid_grant error (expired/revoked refresh token)
            if 'invalid_grant' in error_str.lower() or 'refresh' in error_str.lower():
                # Mark credentials as invalid and require re-authentication
                await self._mark_credentials_invalid(db, user_id, provider)
                return {
                    'success': False,
                    'provider': provider.value,
                    'error': 'REAUTH_REQUIRED',
                    'error_message': 'Your email connection has expired. Please reconnect your account.',
                    'requires_reauth': True,
                    'emails': [],
                    'count': 0
                }
            
            return {
                'success': False,
                'provider': provider.value,
                'error': error_str,
                'emails': [],
                'count': 0
            }
    
    def _filter_emails(self, emails: List[Dict], filters: Dict) -> List[Dict]:
        """
        Filter emails based on search criteria
        
        Args:
            emails: List of email dicts
            filters: Search filters
            
        Returns:
            Filtered list of emails
        """
        filtered = emails
        
        # General search (q) - searches in subject, sender, and snippet
        if filters.get('q'):
            query = filters['q'].lower()
            filtered = [
                email for email in filtered
                if (query in email.get('subject', '').lower() or
                    query in email.get('from', '').lower() or
                    query in email.get('snippet', '').lower())
            ]
        
        # From email filter
        if filters.get('from_email'):
            from_query = filters['from_email'].lower()
            filtered = [
                email for email in filtered
                if from_query in email.get('from', '').lower()
            ]
        
        # Subject filter
        if filters.get('subject'):
            subject_query = filters['subject'].lower()
            filtered = [
                email for email in filtered
                if subject_query in email.get('subject', '').lower()
            ]
        
        # Date range filter
        if filters.get('date_from') or filters.get('date_to'):
            from datetime import datetime
            
            date_from = None
            date_to = None
            
            if filters.get('date_from'):
                try:
                    date_from = datetime.strptime(filters['date_from'], '%Y-%m-%d')
                except:
                    pass
            
            if filters.get('date_to'):
                try:
                    date_to = datetime.strptime(filters['date_to'], '%Y-%m-%d')
                    # Include the entire end date
                    from datetime import timedelta
                    date_to = date_to + timedelta(days=1)
                except:
                    pass
            
            if date_from or date_to:
                filtered_by_date = []
                for email in filtered:
                    email_date_str = email.get('date', '')
                    if email_date_str:
                        try:
                            # Parse email date (format may vary)
                            email_date = datetime.strptime(email_date_str.split('T')[0], '%Y-%m-%d')
                            
                            if date_from and email_date < date_from:
                                continue
                            if date_to and email_date >= date_to:
                                continue
                            
                            filtered_by_date.append(email)
                        except:
                            # If date parsing fails, include the email
                            filtered_by_date.append(email)
                
                filtered = filtered_by_date
        
        # Has attachments filter
        if filters.get('has_attachments') is not None:
            has_attachments = filters['has_attachments']
            filtered = [
                email for email in filtered
                if email.get('has_attachments', False) == has_attachments
            ]
        
        return filtered


# Singleton instance
unified_email_service = UnifiedEmailService()
