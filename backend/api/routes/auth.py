"""Authentication API routes for OAuth 2.0 flows."""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Response
from pydantic import BaseModel, EmailStr

from backend.auth import AuthService

# Configure logging
logger = logging.getLogger(__name__)

# Constants
BEARER_PREFIX = "Bearer "

router = APIRouter()

# Initialize auth service
try:
    auth_service = AuthService()
except ValueError as e:
    logger.warning(f"Auth service initialization failed: {e}")
    auth_service = None


class AuthUrlRequest(BaseModel):
    """Request model for getting authorization URL."""
    
    provider: str
    redirect_uri: str
    state: Optional[str] = None


class AuthUrlResponse(BaseModel):
    """Response model for authorization URL."""
    
    authorization_url: str
    state: Optional[str] = None


class TokenRequest(BaseModel):
    """Request model for token exchange."""
    
    provider: str
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    """Response model for token exchange."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str


class UserInfoResponse(BaseModel):
    """Response model for user information."""
    
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    provider: str


class LogoutRequest(BaseModel):
    """Request model for logout."""
    
    provider: str
    token: str


@router.get("/")
async def auth_root() -> dict:
    """Auth API root endpoint.
    
    Returns:
        Available authentication endpoints and providers
    """
    if not auth_service:
        return {
            "message": "Authentication service not configured",
            "enabled": False,
        }
    
    return {
        "message": "Poker Therapist Authentication API",
        "enabled_providers": auth_service.get_enabled_providers(),
        "endpoints": {
            "get_auth_url": "/auth/authorize",
            "callback": "/auth/callback",
            "token_refresh": "/auth/refresh",
            "user_info": "/auth/me",
        }
    }


@router.get("/providers")
async def get_providers() -> dict:
    """Get list of enabled authentication providers.
    
    Returns:
        List of enabled providers and their configuration
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    providers = auth_service.get_enabled_providers()
    
    return {
        "providers": providers,
        "default": os.getenv("DEFAULT_AUTH_PROVIDER", "google"),
        "require_authentication": auth_service.is_authentication_required(),
    }


@router.post("/authorize", response_model=AuthUrlResponse)
async def get_authorization_url(request: AuthUrlRequest) -> AuthUrlResponse:
    """Get OAuth 2.0 authorization URL for a provider.
    
    Args:
        request: Authorization URL request with provider and redirect URI
        
    Returns:
        Authorization URL to redirect user to
        
    Raises:
        HTTPException: If provider is not supported or auth service not configured
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    try:
        auth_url = auth_service.get_authorization_url(
            provider=request.provider,
            redirect_uri=request.redirect_uri,
            state=request.state,
        )
        
        return AuthUrlResponse(
            authorization_url=auth_url,
            state=request.state,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    redirect_uri: Optional[str] = Query(None, description="Redirect URI used in authorization request"),
) -> TokenResponse:
    """Handle OAuth 2.0 callback and exchange code for tokens.
    
    Args:
        provider: Authentication provider (google, microsoft, apple)
        code: Authorization code from OAuth callback
        state: State parameter for CSRF validation
        redirect_uri: Redirect URI used in authorization (optional, falls back to default)
        
    Returns:
        Access token and refresh token
        
    Raises:
        HTTPException: If callback fails or provider is not supported
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    # Use provided redirect_uri or fall back to default
    if not redirect_uri:
        redirect_uri = _get_redirect_uri(provider)
    
    # NOTE: State validation should be implemented by the client
    # The client should store the state value before redirecting to auth URL
    # and verify it matches when receiving the callback
    
    try:
        access_token, refresh_token, user_info = auth_service.handle_oauth_callback(
            provider=provider,
            authorization_code=code,
            redirect_uri=redirect_uri,
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/token", response_model=TokenResponse)
async def exchange_code_for_token(request: TokenRequest) -> TokenResponse:
    """Exchange authorization code for access and refresh tokens.
    
    This is an alternative to the GET callback endpoint for clients
    that prefer POST requests.
    
    Args:
        request: Token request with provider, code, and redirect URI
        
    Returns:
        Access token and refresh token
        
    Raises:
        HTTPException: If token exchange fails
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    try:
        access_token, refresh_token, user_info = auth_service.handle_oauth_callback(
            provider=request.provider,
            authorization_code=request.code,
            redirect_uri=request.redirect_uri,
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        
    Returns:
        New access token and refresh token
        
    Raises:
        HTTPException: If token refresh fails
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    try:
        access_token, new_refresh_token = auth_service.refresh_token(
            request.refresh_token
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user(
    authorization: str = Header(..., description="Bearer token in format 'Bearer <token>'")
) -> UserInfoResponse:
    """Get current user information from access token.
    
    Args:
        authorization: Authorization header with bearer token
        
    Returns:
        User information from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    # Extract token from Authorization header
    if not authorization.startswith(BEARER_PREFIX):
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authorization header format. Expected '{BEARER_PREFIX}<token>'"
        )
    
    token = authorization[len(BEARER_PREFIX):]  # Remove Bearer prefix
    
    try:
        payload = auth_service.validate_token(token)
        
        return UserInfoResponse(
            user_id=payload.get("sub", ""),
            email=payload.get("email", ""),
            name=payload.get("name", ""),
            provider=payload.get("provider", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@router.post("/logout")
async def logout(request: LogoutRequest) -> dict:
    """Logout and revoke tokens.
    
    Args:
        request: Logout request with provider and token
        
    Returns:
        Logout status
    """
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured"
        )
    
    success = auth_service.revoke_token(request.token, request.provider)
    
    return {
        "success": success,
        "message": "Logged out successfully" if success else "Logout failed",
    }


def _get_redirect_uri(provider: str) -> str:
    """Get redirect URI for provider from environment.
    
    Args:
        provider: Provider name (google, microsoft, apple)
        
    Returns:
        Redirect URI for the provider
    """
    # Check for Vercel deployment
    vercel_url = os.getenv("VERCEL_URL", None)
    if vercel_url:
        # Use Vercel URL for production
        return f"https://{vercel_url}/api/auth/callback/{provider}"
    
    # Fall back to environment-specific redirect URIs
    if provider == "google":
        return os.getenv(
            "GOOGLE_REDIRECT_URI_WEB",
            "http://localhost:8501/auth/callback/google"
        )
    elif provider == "microsoft":
        return os.getenv(
            "AZURE_REDIRECT_URI_WEB",
            "http://localhost:8501/auth/callback/microsoft"
        )
    elif provider == "apple":
        return os.getenv(
            "APPLE_REDIRECT_URI_WEB",
            "http://localhost:8501/auth/callback/apple"
        )
    
    # Default fallback
    return f"http://localhost:8501/auth/callback/{provider}"
