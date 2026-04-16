"""
Authentication service
Handles password hashing, JWT tokens, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
import os

from app.models.user_models import User
from app.models.auth_schemas import TokenData
from app.database import get_db

# OAuth2 scheme for form-based login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# HTTPBearer scheme for token-based authentication (easier for Swagger UI)
http_bearer = HTTPBearer(auto_error=False)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-09876543210")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        # Bcrypt has a 72 byte limit, truncate if necessary
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Convert hashed_password string to bytes if needed
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        # Bcrypt has a 72 byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string for database storage
        return hashed.decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, jti: Optional[str] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        # Add JWT ID for session tracking
        if jti:
            to_encode.update({"jti": jti})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = await AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def create_user(db: AsyncSession, email: str, username: str, password: str) -> User:
        """Create a new user"""
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        db.add(user)
        await db.flush()
        return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from HTTPBearer first (for Swagger UI), then OAuth2
    actual_token = None
    if credentials and credentials.credentials:
        actual_token = credentials.credentials
    elif token:
        actual_token = token
    
    if not actual_token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(actual_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")  # Get JWT ID for session validation
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await AuthService.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    # Validate session if JTI is present
    if jti:
        from app.services.session_service import session_service
        is_valid = await session_service.validate_session(db, jti)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been revoked or expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update session activity
        await session_service.update_session_activity(db, jti)
    
    # Check if user is banned
    if user.is_banned:
        ban_message = "Your account has been banned"
        if user.ban_reason:
            ban_message += f": {user.ban_reason}"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ban_message
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Singleton instance
auth_service = AuthService()
