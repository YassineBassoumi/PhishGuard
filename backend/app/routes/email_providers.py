"""
Email Provider Routes
Unified API endpoints for multi-provider email support
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
import json
import base64
import urllib.parse
import logging

from app.services.unified_email_service import unified_email_service, EmailProvider
from app.services.auth_service import get_current_active_user
from app.models.user_models import User
from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


class EmailListRequest(BaseModel):
    provider: str
    max_results: Optional[int] = 20


class EmailContentRequest(BaseModel):
    provider: str
    message_id: str


class DisconnectProviderRequest(BaseModel):
    provider: str


@router.get("/providers")
async def get_available_providers():
    """Get list of available email providers"""
    return {
        "providers": [
            {
                "id": "gmail",
                "name": "Gmail",
                "description": "Google Gmail",
                "icon": "gmail",
                "available": True
            },
            {
                "id": "outlook",
                "name": "Outlook",
                "description": "Microsoft Outlook/Hotmail",
                "icon": "outlook",
                "available": True
            },
            {
                "id": "yahoo",
                "name": "Yahoo Mail",
                "description": "Yahoo Mail",
                "icon": "yahoo",
                "available": False  # Not yet implemented
            }
        ]
    }


@router.get("/providers/connected")
async def get_connected_providers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of providers user has connected"""
    try:
        providers = await unified_email_service.get_connected_providers(db, current_user.id)
        return {
            "connected_providers": providers,
            "count": len(providers)
        }
    except Exception as e:
        logger.error(f"Failed to get connected providers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve connected providers"
        )


@router.get("/{provider}/auth")
async def provider_auth(provider: str):
    """Initiate OAuth flow for specified provider"""
    try:
        # Validate provider
        try:
            email_provider = EmailProvider(provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}"
            )
        
        # Get authorization URL
        auth_url = unified_email_service.get_authorization_url(email_provider)
        return {"auth_url": auth_url}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate auth URL for {provider}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {str(e)}"
        )


@router.get("/outlook/callback")
async def outlook_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Handle Outlook OAuth callback"""
    try:
        from app.services.outlook_service import outlook_service
        from datetime import datetime
        
        # Exchange code for tokens
        credentials = outlook_service.exchange_code_for_token(code)
        
        # Convert datetime to string for JSON serialization
        if 'token_expiry' in credentials and isinstance(credentials['token_expiry'], datetime):
            credentials['token_expiry'] = credentials['token_expiry'].isoformat()
        
        # Encode credentials as URL-safe base64 to pass in URL
        credentials_json = json.dumps(credentials)
        credentials_encoded = base64.urlsafe_b64encode(credentials_json.encode()).decode()
        
        # Redirect to frontend with credentials
        redirect_url = f"http://localhost:5173?auth=success&provider=outlook&creds={credentials_encoded}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Outlook callback failed: {str(e)}", exc_info=True)
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"http://localhost:5173?auth=error&provider=outlook&message={error_msg}")


@router.post("/emails")
async def list_emails(
    request: EmailListRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch emails from specified provider"""
    try:
        # Validate provider
        try:
            email_provider = EmailProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {request.provider}"
            )
        
        # Fetch emails
        result = await unified_email_service.fetch_emails(
            db,
            current_user.id,
            email_provider,
            request.max_results
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to fetch emails')
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emails: {str(e)}"
        )


@router.post("/email/content")
async def get_email_content(
    request: EmailContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch full content of specific email"""
    try:
        # Validate provider
        try:
            email_provider = EmailProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {request.provider}"
            )
        
        # Get email content
        content = await unified_email_service.get_email_content(
            db,
            current_user.id,
            email_provider,
            request.message_id
        )
        
        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get email content: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email content: {str(e)}"
        )


@router.post("/providers/disconnect")
async def disconnect_provider(
    request: DisconnectProviderRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect email provider"""
    try:
        # Validate provider
        try:
            email_provider = EmailProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {request.provider}"
            )
        
        # Disconnect provider
        await unified_email_service.disconnect_provider(
            db,
            current_user.id,
            email_provider
        )
        
        return {
            "success": True,
            "message": f"Successfully disconnected {request.provider}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect provider: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect provider: {str(e)}"
        )


@router.post("/providers/store-credentials")
async def store_provider_credentials(
    provider: str,
    credentials: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Store provider credentials (called from frontend after OAuth)"""
    try:
        # Validate provider
        try:
            email_provider = EmailProvider(provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}"
            )
        
        # Store credentials
        await unified_email_service.store_user_credentials(
            db,
            current_user.id,
            email_provider,
            credentials
        )
        
        return {
            "success": True,
            "message": f"Successfully connected {provider}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to store credentials: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store credentials: {str(e)}"
        )
