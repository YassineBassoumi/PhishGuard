"""
Microsoft Outlook OAuth Service
Handles Outlook/Hotmail authentication and email fetching via Microsoft Graph API
"""

import requests
from typing import List, Dict, Optional
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OutlookService:
    """Service for Outlook OAuth and email operations"""
    
    SCOPES = [
        'https://graph.microsoft.com/Mail.Read',
        'https://graph.microsoft.com/User.Read',
        'offline_access'  # For refresh tokens
    ]
    
    def __init__(self):
        self.client_config = None
        self._load_client_config()
    
    def _load_client_config(self):
        """Load OAuth client configuration"""
        from dotenv import load_dotenv
        load_dotenv()
        
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            logger.warning("Microsoft OAuth credentials not found in environment")
            self.client_config = None
            return
        
        logger.info("Microsoft OAuth credentials loaded successfully")
        
        self.client_config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "http://localhost:8000/api/email/outlook/callback",
            "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "scopes": ' '.join(self.SCOPES)
        }
    
    def get_authorization_url(self) -> str:
        """Generate OAuth authorization URL"""
        if not self.client_config:
            raise ValueError("Microsoft OAuth not configured")
        
        try:
            auth_url = (
                f"{self.client_config['authorize_url']}?"
                f"client_id={self.client_config['client_id']}"
                f"&response_type=code"
                f"&redirect_uri={self.client_config['redirect_uri']}"
                f"&scope={self.client_config['scopes']}"
                "&response_mode=query"
                "&prompt=consent"
            )
            
            logger.info("Generated Microsoft authorization URL")
            return auth_url
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {str(e)}", exc_info=True)
            raise
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        if not self.client_config:
            raise ValueError("Microsoft OAuth not configured")
        
        try:
            token_data = {
                'client_id': self.client_config['client_id'],
                'client_secret': self.client_config['client_secret'],
                'code': code,
                'redirect_uri': self.client_config['redirect_uri'],
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(self.client_config['token_url'], data=token_data)
            response.raise_for_status()
            
            tokens = response.json()
            
            logger.info("Successfully exchanged code for Microsoft token")
            
            # Calculate token expiry
            expires_in = tokens.get('expires_in', 3600)
            token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return {
                "token": tokens['access_token'],
                "refresh_token": tokens.get('refresh_token'),
                "token_uri": self.client_config['token_url'],
                "client_id": self.client_config['client_id'],
                "client_secret": self.client_config['client_secret'],
                "scopes": self.SCOPES,
                "token_expiry": token_expiry  # Return datetime object, not string
            }
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {str(e)}", exc_info=True)
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh expired access token"""
        if not self.client_config:
            raise ValueError("Microsoft OAuth not configured")
        
        try:
            token_data = {
                'client_id': self.client_config['client_id'],
                'client_secret': self.client_config['client_secret'],
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(self.client_config['token_url'], data=token_data)
            response.raise_for_status()
            
            tokens = response.json()
            
            expires_in = tokens.get('expires_in', 3600)
            token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return {
                "token": tokens['access_token'],
                "refresh_token": tokens.get('refresh_token', refresh_token),
                "token_expiry": token_expiry  # Return datetime object, not string
            }
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}", exc_info=True)
            raise
    
    def list_emails(self, credentials_dict: Dict, max_results: int = 20) -> List[Dict]:
        """Fetch list of emails from Microsoft Graph API"""
        try:
            access_token = credentials_dict.get("token")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get messages with required fields
            url = (
                f"https://graph.microsoft.com/v1.0/me/messages?"
                f"$top={max_results}"
                f"&$select=id,subject,from,receivedDateTime,bodyPreview,internetMessageId"
                f"&$orderby=receivedDateTime desc"
            )
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                raise Exception("Token expired")
            
            response.raise_for_status()
            
            emails = response.json().get('value', [])
            logger.info(f"Retrieved {len(emails)} emails from Outlook")
            
            email_list = []
            for email in emails:
                from_data = email.get('from', {}).get('emailAddress', {})
                email_list.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'from': from_data.get('address', 'Unknown'),
                    'date': email.get('receivedDateTime', ''),
                    'snippet': email.get('bodyPreview', ''),
                    'provider': 'outlook'
                })
            
            return email_list
        except Exception as e:
            logger.error(f"Failed to list Outlook emails: {str(e)}", exc_info=True)
            raise
    
    def get_email_content(self, credentials_dict: Dict, message_id: str) -> str:
        """Fetch full email content by message ID"""
        try:
            access_token = credentials_dict.get("token")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                raise Exception("Token expired")
            
            response.raise_for_status()
            
            msg = response.json()
            
            # Extract email details
            from_data = msg.get('from', {}).get('emailAddress', {})
            sender = from_data.get('address', 'Unknown')
            subject = msg.get('subject', 'No Subject')
            
            # Get body content (prefer text, fallback to HTML)
            body = msg.get('body', {})
            content_type = body.get('contentType', 'text')
            content = body.get('content', '')
            
            # If content is HTML, convert to plain text
            if content_type.lower() == 'html':
                content = self._html_to_text(content)
            
            # Debug logging
            logger.debug(f"Extracted Outlook email content length: {len(content)} chars")
            logger.debug(f"Content type: {content_type}")
            logger.debug(f"Content preview: {content[:100]}...")
            
            full_content = f"From: {sender}\nSubject: {subject}\n\n{content}"
            
            logger.info(f"Retrieved Outlook email content for message ID: {message_id}")
            return full_content
        except Exception as e:
            logger.error(f"Failed to get Outlook email content: {str(e)}", exc_info=True)
            raise
    
    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text for analysis
        Removes HTML tags while preserving text content
        """
        import re
        
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Replace <br> and <p> with newlines
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</p>', '\n\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</div>', '\n', html, flags=re.IGNORECASE)
        
        # Remove all remaining HTML tags
        html = re.sub(r'<[^>]+>', '', html)
        
        # Decode HTML entities
        import html as html_module
        text = html_module.unescape(html)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines
        text = '\n'.join(lines)
        
        return text
    
    def search_emails(self, credentials_dict: Dict, filters: Dict, max_results: int = 100) -> List[Dict]:
        """
        Search emails using Microsoft Graph API search
        
        Args:
            credentials_dict: Outlook OAuth credentials
            filters: Search filters dict with keys:
                - q: General search query
                - from_email: Sender email or name
                - subject: Subject keywords
                - date_from: Start date (YYYY-MM-DD)
                - date_to: End date (YYYY-MM-DD)
                - has_attachments: Boolean
            max_results: Maximum number of results
            
        Returns:
            List of matching emails
        """
        try:
            access_token = credentials_dict.get("token")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Build Microsoft Graph filter query
            filter_parts = []
            
            # From filter
            if filters.get('from_email'):
                from_email = filters['from_email'].replace("'", "''")  # Escape quotes
                filter_parts.append(f"from/emailAddress/address eq '{from_email}' or contains(from/emailAddress/name, '{from_email}')")
            
            # Subject filter
            if filters.get('subject'):
                subject = filters['subject'].replace("'", "''")
                filter_parts.append(f"contains(subject, '{subject}')")
            
            # Date range filters
            if filters.get('date_from'):
                date_from = f"{filters['date_from']}T00:00:00Z"
                filter_parts.append(f"receivedDateTime ge {date_from}")
            
            if filters.get('date_to'):
                date_to = f"{filters['date_to']}T23:59:59Z"
                filter_parts.append(f"receivedDateTime le {date_to}")
            
            # Attachment filter
            if filters.get('has_attachments') is not None:
                has_attachments = 'true' if filters['has_attachments'] else 'false'
                filter_parts.append(f"hasAttachments eq {has_attachments}")
            
            # Build URL with filters
            url = f"https://graph.microsoft.com/v1.0/me/messages?$top={max_results}&$select=id,subject,from,receivedDateTime,bodyPreview,hasAttachments&$orderby=receivedDateTime desc"
            
            if filter_parts:
                filter_query = ' and '.join(filter_parts)
                url += f"&$filter={filter_query}"
            
            # For general search (q), use Microsoft Graph search endpoint
            if filters.get('q'):
                search_query = filters['q']
                url = f"https://graph.microsoft.com/v1.0/me/messages?$top={max_results}&$search=\"{search_query}\"&$select=id,subject,from,receivedDateTime,bodyPreview,hasAttachments&$orderby=receivedDateTime desc"
                
                # Combine with filters if present
                if filter_parts:
                    filter_query = ' and '.join(filter_parts)
                    url += f"&$filter={filter_query}"
            
            logger.info(f"Outlook search URL: {url}")
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                raise Exception("Token expired")
            
            response.raise_for_status()
            
            emails = response.json().get('value', [])
            logger.info(f"Found {len(emails)} emails matching search criteria")
            
            email_list = []
            for email in emails:
                from_data = email.get('from', {}).get('emailAddress', {})
                
                # Parse date to YYYY-MM-DD format
                date_str = email.get('receivedDateTime', '')
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date = date_obj.strftime('%Y-%m-%d')
                except:
                    date = date_str
                
                email_list.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'from': from_data.get('address', 'Unknown'),
                    'date': date,
                    'snippet': email.get('bodyPreview', ''),
                    'has_attachments': email.get('hasAttachments', False)
                })
            
            return email_list
            
        except Exception as e:
            logger.error(f"Failed to search Outlook emails: {str(e)}", exc_info=True)
            raise


# Singleton instance
outlook_service = OutlookService()
