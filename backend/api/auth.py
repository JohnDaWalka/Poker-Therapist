"""Authentication configuration and utilities."""

import os
from typing import Dict, List, Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from itsdangerous import URLSafeTimedSerializer
from jose import JWTError, jwt


# OAuth configuration
oauth = OAuth()

# Microsoft Azure AD OAuth
oauth.register(
    name="microsoft",
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    server_metadata_url=f'https://login.microsoftonline.com/{os.getenv("AZURE_TENANT_ID")}/v2.0/.well-known/openid-configuration',
    client_kwargs={
        "scope": "openid email profile User.Read"
    }
)

# Google OAuth
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile https://www.googleapis.com/auth/cloud-platform"
    }
)


class AuthConfig:
    """Authentication configuration."""
    
    def __init__(self):
        """Initialize authentication configuration."""
        self.enabled = os.getenv("AUTHENTICATION_ENABLED", "true").lower() == "true"
        self.secret_key = os.getenv("SESSION_SECRET_KEY", "development-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
        
        # Allowed institutional email domains
        domains_str = os.getenv("INSTITUTIONAL_EMAIL_DOMAINS", "ctstate.edu")
        self.institutional_domains = [d.strip() for d in domains_str.split(",") if d.strip()]
        
        # Session serializer for secure cookies
        self.serializer = URLSafeTimedSerializer(self.secret_key)
    
    def create_access_token(self, data: Dict) -> str:
        """Create JWT access token.
        
        Args:
            data: Token payload data
            
        Returns:
            Encoded JWT token
        """
        from datetime import datetime, timedelta
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT access token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def is_institutional_email(self, email: str) -> bool:
        """Check if email is from an institutional domain.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email is from an institutional domain
        """
        if not email:
            return False
        
        email_domain = email.split("@")[-1].lower()
        return any(email_domain == domain.lower() for domain in self.institutional_domains)
    
    def validate_user(self, email: str, provider: str) -> bool:
        """Validate user based on email and authentication provider.
        
        Args:
            email: User email address
            provider: Authentication provider (microsoft, google)
            
        Returns:
            True if user is authorized
        """
        # Check if from institutional domain for Microsoft authentication
        if provider == "microsoft":
            return self.is_institutional_email(email)
        
        # For Google, allow authorized emails
        from chatbot_app import AUTHORIZED_EMAILS
        return email in AUTHORIZED_EMAILS or self.is_institutional_email(email)


# Global auth config instance
auth_config = AuthConfig()

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If authentication is required and fails
    """
    # If authentication is disabled, return default user
    if not auth_config.enabled:
        return {"email": "development@localhost", "provider": "none"}
    
    # If no credentials provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    token = credentials.credentials
    user_data = auth_config.verify_token(token)
    
    return user_data


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """Get current user if authenticated, otherwise None.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User data from token or None
    """
    if not auth_config.enabled or credentials is None:
        return None
    
    try:
        token = credentials.credentials
        user_data = auth_config.verify_token(token)
        return user_data
    except HTTPException:
        return None
