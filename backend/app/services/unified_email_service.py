"""
Unified Email Service
Routes email operations to appropriate provider (Gmail, Outlook, Yahoo)
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
    YAHOO = 'yahoo'


class UnifiedEmailService:
    """Unified service for multi-provider email operations"""
    
    def __init__(self):
        self.providers = {
            EmailProvider.GMAIL: gmail_service,
            EmailProvider.OUTLOOK: outlook_service,
            # EmailProvider.YAHOO: yahoo_service,  # To be implemented
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
            from datetime import datetime
            
            # Convert token_expiry string to datetime if needed
            token_expiry = credentials.get('token_expiry')
            if token_expiry and isinstance(token_expiry, str):
                token_expiry = datetime.fromisoformat(token_expiry)
            
            # Check if credentials already exist
            result = await db.execute(
                select(UserEmailCredential).where(
                    UserEmailCredential.user_id == user_id,
                    UserEmailCredential.provider == provider.value
                )
            )
            credential = result.scalar_one_or_none()
            
            if credential:
                # Update existing
                credential.access_token = credentials.get('token')
                credential.refresh_token = credentials.get('refresh_token')
                credential.token_expiry = token_expiry
                credential.email_address = credentials.get('email_address')
            else:
                # Create new
                credential = UserEmailCredential(
                    user_id=user_id,
                    provider=provider.value,
                    access_token=credentials.get('token'),
                    refresh_token=credentials.get('refresh_token'),
                    token_expiry=token_expiry,
                    email_address=credentials.get('email_address')
                )
                db.add(credential)
            
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
            
            # Get provider service
            service = self.get_provider_service(provider)
            
            # Fetch emails
            emails = service.list_emails(credentials, max_results)
            
            return {
                'success': True,
                'provider': provider.value,
                'emails': emails,
                'count': len(emails)
            }
        except Exception as e:
            logger.error(f"Failed to fetch emails from {provider}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'provider': provider.value,
                'error': str(e),
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
            
            # Get provider service
            service = self.get_provider_service(provider)
            
            # Fetch email content
            content = service.get_email_content(credentials, message_id)
            
            return content
        except Exception as e:
            logger.error(f"Failed to get email content from {provider}: {str(e)}", exc_info=True)
            raise
    
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


# Singleton instance
unified_email_service = UnifiedEmailService()
