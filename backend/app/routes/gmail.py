"""
Gmail OAuth Routes
Handles Gmail authentication and email fetching endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.gmail_service import gmail_service

router = APIRouter()


class TokenRequest(BaseModel):
    code: str


class EmailListRequest(BaseModel):
    credentials: Dict
    max_results: Optional[int] = 20


class EmailContentRequest(BaseModel):
    credentials: Dict
    message_id: str


@router.get("/gmail/auth")
async def gmail_auth():
    """Initiate Gmail OAuth flow"""
    try:
        auth_url = gmail_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")


@router.get("/gmail/callback")
async def gmail_callback(code: str = Query(...)):
    """Handle OAuth callback and exchange code for token"""
    from fastapi.responses import RedirectResponse
    import json
    import urllib.parse
    try:
        credentials = gmail_service.exchange_code_for_token(code)
        # Encode credentials as base64 to pass in URL
        import base64
        credentials_json = json.dumps(credentials)
        credentials_encoded = base64.b64encode(credentials_json.encode()).decode()
        
        # Redirect to port 5174 (current frontend port)
        redirect_url = f"http://localhost:5174?auth=success&creds={credentials_encoded}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        # Redirect with error
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"http://localhost:5174?auth=error&message={error_msg}")


@router.post("/gmail/emails")
async def list_emails(request: EmailListRequest):
    """Fetch list of emails from Gmail"""
    try:
        emails = gmail_service.list_emails(
            request.credentials,
            max_results=request.max_results
        )
        return {"emails": emails, "count": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch emails: {str(e)}")


@router.post("/gmail/email/content")
async def get_email_content(request: EmailContentRequest):
    """Fetch full content of a specific email"""
    try:
        content = gmail_service.get_email_content(
            request.credentials,
            request.message_id
        )
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch email content: {str(e)}")
