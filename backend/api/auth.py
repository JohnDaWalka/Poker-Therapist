"""OAuth authentication middleware for FastAPI backend."""

import os
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt


# Security scheme
security = HTTPBearer(auto_error=False)


class AuthConfig:
    """Authentication configuration for backend API."""
    
    def __init__(self):
        """Initialize authentication configuration from environment."""
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
        
        # List of authorized email addresses (VIP users)
        authorized_emails_str = os.getenv("AUTHORIZED_EMAILS", "")
        self.authorized_emails = [
            email.strip() 
            for email in authorized_emails_str.split(",") 
            if email.strip()
        ]


# Global auth config
auth_config = AuthConfig()


class User:
    """Authenticated user information."""
    
    def __init__(
        self,
        email: str,
        provider: Optional[str] = None,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Initialize user.
        
        Args:
            email: User email address
            provider: OAuth provider (microsoft, google, apple, or None for legacy)
            name: User display name
            user_id: Provider-specific user ID
        """
        self.email = email
        self.provider = provider
        self.name = name
        self.user_id = user_id
    
    @property
    def is_authorized(self) -> bool:
        """Check if user is in authorized list.
        
        Returns:
            True if user email is in authorized list
        """
        return self.email in auth_config.authorized_emails
    
    @property
    def is_vip(self) -> bool:
        """Check if user has VIP status (alias for is_authorized).
        
        Returns:
            True if user has VIP status
        """
        return self.is_authorized


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    if not auth_config.jwt_secret:
        return None
    
    try:
        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)] = None,
    x_user_email: Annotated[Optional[str], Header()] = None,
) -> Optional[User]:
    """Get current authenticated user from JWT token or email header.
    
    This function supports multiple authentication methods:
    1. OAuth/JWT: Bearer token in Authorization header
    2. Legacy: X-User-Email header for backward compatibility
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        x_user_email: User email from X-User-Email header (legacy)
        
    Returns:
        User object or None if not authenticated
        
    Raises:
        HTTPException: If authentication is required but invalid
    """
    # Try OAuth/JWT authentication first
    if credentials and credentials.credentials:
        payload = verify_jwt_token(credentials.credentials)
        if payload:
            return User(
                email=payload.get("email"),
                provider=payload.get("provider"),
                name=payload.get("name"),
                user_id=payload.get("user_id"),
            )
    
    # Fall back to legacy email header authentication
    if x_user_email:
        return User(email=x_user_email)
    
    # No authentication provided
    if auth_config.require_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return None


async def require_authenticated_user(
    user: Annotated[Optional[User], Depends(get_current_user)]
) -> User:
    """Require an authenticated user.
    
    Args:
        user: Current user from dependency injection
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_vip_user(
    user: Annotated[User, Depends(require_authenticated_user)]
) -> User:
    """Require an authenticated VIP user.
    
    Args:
        user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not a VIP
    """
    if not user.is_vip:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="VIP access required",
        )
    return user


# Type aliases for dependency injection
CurrentUser = Annotated[Optional[User], Depends(get_current_user)]
AuthenticatedUser = Annotated[User, Depends(require_authenticated_user)]
VIPUser = Annotated[User, Depends(require_vip_user)]
