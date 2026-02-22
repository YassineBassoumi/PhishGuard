"""
Outlook OAuth Routes
Handles Outlook OAuth callback (auth initiation is handled by email_providers.py)
"""

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import base64
import urllib.parse
import logging

from app.services.outlook_service import outlook_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/email/outlook/callback")
async def outlook_callback(code: str = Query(...)):
    """Handle OAuth callback and exchange code for token"""
    try:
        # Exchange code for tokens
        credentials = outlook_service.exchange_code_for_token(code)
        
        # Convert datetime to string for JSON serialization
        if 'token_expiry' in credentials and isinstance(credentials['token_expiry'], datetime):
            credentials['token_expiry'] = credentials['token_expiry'].isoformat()
        
        # Encode credentials as URL-safe base64 to pass in URL
        credentials_json = json.dumps(credentials)
        credentials_encoded = base64.urlsafe_b64encode(credentials_json.encode()).decode()
        
        # Redirect to frontend with provider=outlook for unified handling
        redirect_url = f"http://localhost:5173?auth=success&provider=outlook&creds={credentials_encoded}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Outlook callback failed: {str(e)}", exc_info=True)
        # Redirect with error
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"http://localhost:5173?auth=error&provider=outlook&message={error_msg}")
