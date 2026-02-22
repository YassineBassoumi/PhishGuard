"""
Session management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from app.database import get_db
from app.models.user_models import User
from app.models.session_schemas import SessionListResponse, SessionResponse, RevokeSessionRequest
from app.services.auth_service import get_current_active_user, oauth2_scheme, SECRET_KEY, ALGORITHM
from app.services.session_service import session_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("/", response_model=SessionListResponse)
async def get_sessions(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get all active sessions for the current user"""
    try:
        # Extract JTI from current token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        current_jti = payload.get("jti")
        
        # Get all sessions
        sessions = await session_service.get_user_sessions(db, current_user.id, current_jti)
        
        await db.commit()
        
        return SessionListResponse(
            sessions=[SessionResponse(**session) for session in sessions],
            total=len(sessions)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sessions: {str(e)}"
        )


@router.post("/revoke")
async def revoke_session(
    request: RevokeSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific session"""
    try:
        success = await session_service.revoke_session(
            db,
            request.session_id,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        await db.commit()
        
        return {"message": "Session revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke session: {str(e)}"
        )


@router.post("/revoke-all")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Revoke all sessions except the current one"""
    try:
        # Extract JTI from current token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        current_jti = payload.get("jti")
        
        # Revoke all other sessions
        count = await session_service.revoke_all_sessions(
            db,
            current_user.id,
            except_jti=current_jti
        )
        
        await db.commit()
        
        return {
            "message": f"Successfully revoked {count} session(s)",
            "count": count
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke sessions: {str(e)}"
        )
