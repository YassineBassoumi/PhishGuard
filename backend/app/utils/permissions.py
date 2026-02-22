"""
Permission decorators for role-based access control (RBAC)
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from app.models.user_models import User, UserRole
from app.services.auth_service import get_current_active_user


def require_role(*allowed_roles: UserRole):
    """
    Decorator to require specific roles for endpoint access
    
    Usage:
        @require_role(UserRole.ADMIN, UserRole.SUPERADMIN)
        async def admin_endpoint(current_user: User = Depends(get_current_active_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require admin or superadmin role
    
    Usage:
        async def admin_endpoint(current_user: User = Depends(require_admin)):
            ...
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_superadmin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require superadmin role
    
    Usage:
        async def superadmin_endpoint(current_user: User = Depends(require_superadmin)):
            ...
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SuperAdmin access required"
        )
    return current_user
