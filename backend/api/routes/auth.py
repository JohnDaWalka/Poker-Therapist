"""Authentication routes for OAuth/SSO integration."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend.api.auth import CurrentUser, AuthenticatedUser, VIPUser


router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserResponse(BaseModel):
    """User response model."""
    
    email: EmailStr
    name: str | None = None
    provider: str | None = None
    is_authorized: bool
    is_vip: bool


class HealthResponse(BaseModel):
    """Authentication health check response."""
    
    oauth_enabled: bool
    jwt_configured: bool
    auth_required: bool


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: AuthenticatedUser) -> UserResponse:
    """Get current authenticated user information.
    
    This endpoint requires authentication via JWT token or email header.
    
    Args:
        user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        email=user.email,
        name=user.name,
        provider=user.provider,
        is_authorized=user.is_authorized,
        is_vip=user.is_vip,
    )


@router.get("/vip-check")
async def check_vip_status(user: VIPUser) -> dict[str, str]:
    """Check if user has VIP status.
    
    This endpoint requires VIP user authentication.
    
    Args:
        user: Current VIP user
        
    Returns:
        VIP status confirmation
    """
    return {
        "message": f"VIP access confirmed for {user.email}",
        "status": "vip",
    }


@router.get("/health", response_model=HealthResponse)
async def auth_health_check() -> HealthResponse:
    """Check authentication configuration status.
    
    Returns:
        Authentication configuration status
    """
    from backend.api.auth import auth_config
    
    return HealthResponse(
        oauth_enabled=bool(auth_config.jwt_secret),
        jwt_configured=bool(auth_config.jwt_secret),
        auth_required=auth_config.require_auth,
    )


@router.get("/test-optional")
async def test_optional_auth(user: CurrentUser) -> dict[str, str | None]:
    """Test endpoint with optional authentication.
    
    This endpoint works with or without authentication.
    
    Args:
        user: Current user (if authenticated)
        
    Returns:
        User information or guest status
    """
    if user:
        return {
            "status": "authenticated",
            "email": user.email,
            "provider": user.provider,
        }
    return {
        "status": "guest",
        "email": None,
        "provider": None,
    }
