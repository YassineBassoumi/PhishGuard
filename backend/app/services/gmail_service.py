"""
Gmail OAuth Service
Handles Gmail API authentication and email fetching
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from typing import List, Dict, Optional
import base64
import os
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)


class GmailService:
    """Service for Gmail OAuth and email operations"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.client_config = None
        self._load_client_config()
    
    def _load_client_config(self):
        """Load OAuth client configuration"""
        # Load from environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            logger.error("Gmail OAuth credentials not found in environment")
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env file")
        
        logger.info("Gmail OAuth credentials loaded successfully")
        
        self.client_config = {
            "web": {
                "client_id": client_id,
                "project_id": "phishing-485410",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost:8000/api/gmail/callback"],
                "javascript_origins": ["http://localhost:5173", "http://localhost:8000"]
            }
        }
    
    def get_authorization_url(self) -> str:
        """Generate OAuth authorization URL"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri="http://localhost:8000/api/gmail/callback"
            )
            
            auth_url, state = flow.authorization_url(
                access_type='offline',  # Required for refresh token
                include_granted_scopes='true',
                prompt='consent',  # Force consent screen to get new refresh token
                state='security_token'
            )
            
            logger.info("Generated Gmail authorization URL with offline access")
            return auth_url
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {str(e)}", exc_info=True)
            raise
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri="http://localhost:8000/api/gmail/callback"
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            logger.info("Successfully exchanged code for token")
            
            return {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {str(e)}", exc_info=True)
            raise
    
    def list_emails(self, credentials_dict: Dict, max_results: int = 20) -> List[Dict]:
        """Fetch list of emails from Gmail"""
        try:
            credentials = Credentials(
                token=credentials_dict.get("token"),
                refresh_token=credentials_dict.get("refresh_token"),
                token_uri=credentials_dict.get("token_uri"),
                client_id=credentials_dict.get("client_id"),
                client_secret=credentials_dict.get("client_secret"),
                scopes=credentials_dict.get("scopes")
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            
            # Get list of messages
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Retrieved {len(messages)} emails from Gmail")
            
            email_list = []
            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract email details
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get snippet
                snippet = msg.get('snippet', '')
                
                email_list.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'snippet': snippet
                })
            
            return email_list
        except Exception as e:
            logger.error(f"Failed to list emails: {str(e)}", exc_info=True)
            raise
    
    def get_email_content(self, credentials_dict: Dict, message_id: str) -> str:
        """Fetch full email content by message ID"""
        try:
            credentials = Credentials(
                token=credentials_dict.get("token"),
                refresh_token=credentials_dict.get("refresh_token"),
                token_uri=credentials_dict.get("token_uri"),
                client_id=credentials_dict.get("client_id"),
                client_secret=credentials_dict.get("client_secret"),
                scopes=credentials_dict.get("scopes")
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            
            msg = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract email content
            content = self._extract_email_body(msg)
            
            # Add headers for context - IMPORTANT: These headers are analyzed for phishing!
            # Including From/Subject helps detect spoofed senders and suspicious subjects
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            # Full content includes headers (more accurate phishing detection)
            full_content = f"From: {sender}\nSubject: {subject}\n\n{content}"
            
            # Debug logging
            logger.debug(f"Extracted email content length: {len(content)} chars")
            logger.debug(f"Full content length (with headers): {len(full_content)} chars")
            logger.debug(f"Content preview: {content[:100]}...")
            
            logger.info(f"Retrieved email content for message ID: {message_id}")
            return full_content
        except Exception as e:
            logger.error(f"Failed to get email content: {str(e)}", exc_info=True)
            raise
    
    def _extract_email_body(self, message: Dict) -> str:
        """Extract email body from message payload"""
        body_text = None
        body_html = None
        
        if 'parts' in message['payload']:
            parts = message['payload']['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if 'body' in message['payload'] and 'data' in message['payload']['body']:
                mime_type = message['payload'].get('mimeType', '')
                decoded = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                if mime_type == 'text/plain':
                    body_text = decoded
                elif mime_type == 'text/html':
                    body_html = decoded
                else:
                    body_text = decoded  # Default to text
        
        # Prefer plain text over HTML
        if body_text:
            return body_text
        elif body_html:
            # Convert HTML to plain text
            return self._html_to_text(body_html)
        else:
            # Fallback to snippet
            return message.get('snippet', '')
    
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
        Search emails using Gmail's native search API
        
        Args:
            credentials_dict: Gmail OAuth credentials
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
            credentials = Credentials(
                token=credentials_dict.get("token"),
                refresh_token=credentials_dict.get("refresh_token"),
                token_uri=credentials_dict.get("token_uri"),
                client_id=credentials_dict.get("client_id"),
                client_secret=credentials_dict.get("client_secret"),
                scopes=credentials_dict.get("scopes")
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            
            # Build Gmail search query
            query_parts = []
            
            # General search
            if filters.get('q'):
                query_parts.append(filters['q'])
            
            # From filter
            if filters.get('from_email'):
                query_parts.append(f"from:{filters['from_email']}")
            
            # Subject filter
            if filters.get('subject'):
                query_parts.append(f"subject:{filters['subject']}")
            
            # Date range filters
            if filters.get('date_from'):
                # Gmail format: after:YYYY/MM/DD
                date_str = filters['date_from'].replace('-', '/')
                query_parts.append(f"after:{date_str}")
            
            if filters.get('date_to'):
                # Gmail format: before:YYYY/MM/DD
                date_str = filters['date_to'].replace('-', '/')
                query_parts.append(f"before:{date_str}")
            
            # Attachment filter
            if filters.get('has_attachments') is not None:
                if filters['has_attachments']:
                    query_parts.append("has:attachment")
                else:
                    query_parts.append("-has:attachment")
            
            # Combine query parts
            search_query = ' '.join(query_parts) if query_parts else 'in:inbox'
            
            logger.info(f"Gmail search query: {search_query}")
            
            # Search messages using Gmail API
            results = service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails matching search criteria")
            
            # Fetch full details for each message
            email_list = []
            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract email details
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Parse date to YYYY-MM-DD format
                from email.utils import parsedate_to_datetime
                try:
                    date_obj = parsedate_to_datetime(date_header)
                    date = date_obj.strftime('%Y-%m-%d')
                except:
                    date = date_header
                
                # Get snippet
                snippet = msg.get('snippet', '')
                
                # Check for attachments
                has_attachments = False
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part.get('filename'):
                            has_attachments = True
                            break
                
                email_list.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'snippet': snippet,
                    'has_attachments': has_attachments
                })
            
            return email_list
            
        except Exception as e:
            logger.error(f"Failed to search emails: {str(e)}", exc_info=True)
            raise


# Singleton instance
gmail_service = GmailService()
