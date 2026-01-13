"""OAuth/SSO Authentication Service for Poker Therapist.

This module provides OAuth 2.0 and OpenID Connect authentication support for:
- Microsoft Azure AD / Windows Accounts (institutional SSO)
- Google OAuth 2.0 / OpenID Connect
- Apple Sign In
"""

import os
import secrets
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, parse_qs, urlparse

import jwt
import requests
from authlib.integrations.base_client import OAuthError
from authlib.jose import JsonWebKey
from msal import ConfidentialClientApplication, PublicClientApplication

logger = logging.getLogger(__name__)


@dataclass
class AuthConfig:
    """Authentication configuration."""
    
    # Microsoft Azure AD Configuration
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    microsoft_redirect_uri: Optional[str] = None
    
    # Google OAuth Configuration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None
    
    # Apple Sign In Configuration
    apple_client_id: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_private_key: Optional[str] = None
    apple_redirect_uri: Optional[str] = None
    
    # Session configuration
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    session_timeout_minutes: int = 60

    @classmethod
    def from_env(cls) -> "AuthConfig":
        """Load authentication configuration from environment variables."""
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        
        # Warn if JWT secret is not configured (will use auto-generated, session won't persist)
        if not jwt_secret:
            logger.warning(
                "JWT_SECRET_KEY not configured - using auto-generated secret. "
                "Sessions will not persist across application restarts. "
                "Set JWT_SECRET_KEY environment variable for production."
            )
            jwt_secret = secrets.token_urlsafe(32)
        
        return cls(
            # Microsoft
            microsoft_client_id=os.getenv("MICROSOFT_CLIENT_ID"),
            microsoft_client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
            microsoft_tenant_id=os.getenv("MICROSOFT_TENANT_ID", "common"),
            microsoft_redirect_uri=os.getenv("MICROSOFT_REDIRECT_URI"),
            
            # Google
            google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
            google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            google_redirect_uri=os.getenv("GOOGLE_REDIRECT_URI"),
            
            # Apple
            apple_client_id=os.getenv("APPLE_CLIENT_ID"),
            apple_team_id=os.getenv("APPLE_TEAM_ID"),
            apple_key_id=os.getenv("APPLE_KEY_ID"),
            apple_private_key=os.getenv("APPLE_PRIVATE_KEY"),
            apple_redirect_uri=os.getenv("APPLE_REDIRECT_URI"),
            
            # Session
            jwt_secret=jwt_secret,
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "60")),
        )


@dataclass
class UserInfo:
    """User information from OAuth provider."""
    
    provider: str
    email: str
    name: Optional[str] = None
    user_id: Optional[str] = None
    picture: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class MicrosoftAuthService:
    """Microsoft Azure AD / Windows Account authentication service."""
    
    def __init__(self, config: AuthConfig):
        """Initialize Microsoft authentication service.
        
        Args:
            config: Authentication configuration
        """
        self.config = config
        self.authority = f"https://login.microsoftonline.com/{config.microsoft_tenant_id}"
        self.scopes = ["User.Read", "openid", "email", "profile"]
        
        if config.microsoft_client_secret:
            # Confidential client (web app)
            self.client = ConfidentialClientApplication(
                config.microsoft_client_id,
                authority=self.authority,
                client_credential=config.microsoft_client_secret,
            )
        else:
            # Public client (desktop/mobile app)
            self.client = PublicClientApplication(
                config.microsoft_client_id,
                authority=self.authority,
            )
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Get Microsoft OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(16)
        
        auth_url = self.client.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.config.microsoft_redirect_uri,
        )
        
        return auth_url, state
    
    def get_user_info(self, auth_code: str) -> Optional[UserInfo]:
        """Get user information from Microsoft OAuth.
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            UserInfo object or None on failure
        """
        try:
            result = self.client.acquire_token_by_authorization_code(
                auth_code,
                scopes=self.scopes,
                redirect_uri=self.config.microsoft_redirect_uri,
            )
            
            if "access_token" not in result:
                logger.error(f"Failed to get access token: {result.get('error_description')}")
                return None
            
            # Get user info from Microsoft Graph API
            headers = {"Authorization": f"Bearer {result['access_token']}"}
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers,
            )
            response.raise_for_status()
            user_data = response.json()
            
            return UserInfo(
                provider="microsoft",
                email=user_data.get("mail") or user_data.get("userPrincipalName"),
                name=user_data.get("displayName"),
                user_id=user_data.get("id"),
                raw_data=user_data,
            )
        except Exception as e:
            logger.error(f"Error getting Microsoft user info: {e}")
            return None


class GoogleAuthService:
    """Google OAuth 2.0 / OpenID Connect authentication service."""
    
    def __init__(self, config: AuthConfig):
        """Initialize Google authentication service.
        
        Args:
            config: Authentication configuration
        """
        self.config = config
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.userinfo_uri = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ]
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Get Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(16)
        
        params = {
            "client_id": self.config.google_client_id,
            "redirect_uri": self.config.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        
        auth_url = f"{self.auth_uri}?{urlencode(params)}"
        return auth_url, state
    
    def get_user_info(self, auth_code: str) -> Optional[UserInfo]:
        """Get user information from Google OAuth.
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            UserInfo object or None on failure
        """
        try:
            # Exchange authorization code for access token
            token_data = {
                "code": auth_code,
                "client_id": self.config.google_client_id,
                "client_secret": self.config.google_client_secret,
                "redirect_uri": self.config.google_redirect_uri,
                "grant_type": "authorization_code",
            }
            
            token_response = requests.post(self.token_uri, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            if "access_token" not in tokens:
                logger.error("Failed to get access token from Google")
                return None
            
            # Get user info
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            response = requests.get(self.userinfo_uri, headers=headers)
            response.raise_for_status()
            user_data = response.json()
            
            return UserInfo(
                provider="google",
                email=user_data.get("email"),
                name=user_data.get("name"),
                user_id=user_data.get("sub"),
                picture=user_data.get("picture"),
                raw_data=user_data,
            )
        except Exception as e:
            logger.error(f"Error getting Google user info: {e}")
            return None


class AppleAuthService:
    """Apple Sign In authentication service."""
    
    def __init__(self, config: AuthConfig):
        """Initialize Apple authentication service.
        
        Args:
            config: Authentication configuration
        """
        self.config = config
        self.auth_uri = "https://appleid.apple.com/auth/authorize"
        self.token_uri = "https://appleid.apple.com/auth/token"
        self.scopes = ["name", "email"]
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Get Apple Sign In authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(16)
        
        params = {
            "client_id": self.config.apple_client_id,
            "redirect_uri": self.config.apple_redirect_uri,
            "response_type": "code",
            "response_mode": "form_post",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        
        auth_url = f"{self.auth_uri}?{urlencode(params)}"
        return auth_url, state
    
    def _generate_client_secret(self) -> str:
        """Generate Apple client secret JWT.
        
        Returns:
            Client secret JWT string
        """
        headers = {
            "kid": self.config.apple_key_id,
            "alg": "ES256",
        }
        
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.config.apple_team_id,
            "iat": now,
            "exp": now + timedelta(days=180),
            "aud": "https://appleid.apple.com",
            "sub": self.config.apple_client_id,
        }
        
        return jwt.encode(
            payload,
            self.config.apple_private_key,
            algorithm="ES256",
            headers=headers,
        )
    
    def get_user_info(self, auth_code: str, user_data: Optional[Dict] = None) -> Optional[UserInfo]:
        """Get user information from Apple Sign In.
        
        Args:
            auth_code: Authorization code from OAuth callback
            user_data: Optional user data from Apple (only provided on first sign in)
            
        Returns:
            UserInfo object or None on failure
        """
        try:
            # Generate client secret
            client_secret = self._generate_client_secret()
            
            # Exchange authorization code for access token
            token_data = {
                "code": auth_code,
                "client_id": self.config.apple_client_id,
                "client_secret": client_secret,
                "redirect_uri": self.config.apple_redirect_uri,
                "grant_type": "authorization_code",
            }
            
            token_response = requests.post(self.token_uri, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Decode ID token to get user info
            id_token = tokens.get("id_token")
            if not id_token:
                logger.error("Failed to get ID token from Apple")
                return None
            
            # TODO: Implement proper JWT signature verification for production use
            # This requires fetching Apple's public keys from https://appleid.apple.com/auth/keys
            # and verifying the signature using those keys. For now, we decode without verification
            # which is acceptable for development but should be fixed before production deployment.
            # Security implications: Without verification, a malicious actor could forge tokens.
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            
            # Extract name from user_data if provided (only on first sign in)
            name = None
            if user_data and "name" in user_data:
                name_parts = []
                if "firstName" in user_data["name"]:
                    name_parts.append(user_data["name"]["firstName"])
                if "lastName" in user_data["name"]:
                    name_parts.append(user_data["name"]["lastName"])
                name = " ".join(name_parts) if name_parts else None
            
            return UserInfo(
                provider="apple",
                email=decoded.get("email"),
                name=name,
                user_id=decoded.get("sub"),
                raw_data=decoded,
            )
        except Exception as e:
            logger.error(f"Error getting Apple user info: {e}")
            return None


class AuthenticationService:
    """Main authentication service coordinator."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        """Initialize authentication service.
        
        Args:
            config: Optional authentication configuration (defaults to env vars)
        """
        self.config = config or AuthConfig.from_env()
        
        # Initialize provider services
        self.microsoft = None
        self.google = None
        self.apple = None
        
        if self.config.microsoft_client_id:
            self.microsoft = MicrosoftAuthService(self.config)
        
        if self.config.google_client_id:
            self.google = GoogleAuthService(self.config)
        
        if self.config.apple_client_id:
            self.apple = AppleAuthService(self.config)
    
    def get_available_providers(self) -> list[str]:
        """Get list of configured authentication providers.
        
        Returns:
            List of provider names
        """
        providers = []
        if self.microsoft:
            providers.append("microsoft")
        if self.google:
            providers.append("google")
        if self.apple:
            providers.append("apple")
        return providers
    
    def create_session_token(self, user_info: UserInfo) -> str:
        """Create a JWT session token for the user.
        
        Args:
            user_info: User information from OAuth provider
            
        Returns:
            JWT session token
        """
        now = datetime.now(timezone.utc)
        payload = {
            "provider": user_info.provider,
            "email": user_info.email,
            "name": user_info.name,
            "user_id": user_info.user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.config.session_timeout_minutes),
        }
        
        return jwt.encode(
            payload,
            self.config.jwt_secret,
            algorithm=self.config.jwt_algorithm,
        )
    
    def verify_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a session token.
        
        Args:
            token: JWT session token
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret,
                algorithms=[self.config.jwt_algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Session token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid session token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
