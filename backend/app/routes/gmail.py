"""
Gmail OAuth Routes
Handles Gmail OAuth callback (auth initiation is handled by email_providers.py)
"""

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
import json
import base64
import urllib.parse
from app.services.gmail_service import gmail_service

router = APIRouter()


@router.get("/gmail/callback")
async def gmail_callback(code: str = Query(...)):
    """Handle OAuth callback and exchange code for token"""
    try:
        credentials = gmail_service.exchange_code_for_token(code)
        
        # Encode credentials as URL-safe base64 to pass in URL
        credentials_json = json.dumps(credentials)
        credentials_encoded = base64.urlsafe_b64encode(credentials_json.encode()).decode()
        
        # Redirect to frontend with provider=gmail for unified handling
        redirect_url = f"http://localhost:5173?auth=success&provider=gmail&creds={credentials_encoded}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        # Redirect with error
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"http://localhost:5173?auth=error&provider=gmail&message={error_msg}")
