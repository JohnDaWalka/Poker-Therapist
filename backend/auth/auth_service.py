"""Main authentication service orchestrating all auth providers."""

import os
from typing import Any, Dict, Optional, Tuple

from .apple_auth import AppleAuthProvider
from .google_auth import GoogleAuthProvider
from .jwt_handler import JWTHandler
from .microsoft_auth import MicrosoftAuthProvider


class AuthService:
    """Orchestrate authentication across multiple providers.
    
    Supports:
    - Microsoft Azure AD / Windows accounts
    - Google OAuth 2.0
    - Apple Sign-In
    - JWT token management
    """

    def __init__(self) -> None:
        """Initialize authentication service with all providers."""
        self.jwt_handler = JWTHandler()
        
        # Initialize providers based on configuration
        self.microsoft_enabled = os.getenv("ENABLE_MICROSOFT_AUTH", "true").lower() == "true"
        self.google_enabled = os.getenv("ENABLE_GOOGLE_AUTH", "true").lower() == "true"
        self.apple_enabled = os.getenv("ENABLE_APPLE_AUTH", "true").lower() == "true"
        
        self.providers: Dict[str, Any] = {}
        
        if self.microsoft_enabled:
            try:
                self.providers["microsoft"] = MicrosoftAuthProvider()
            except ValueError as e:
                print(f"Microsoft auth disabled: {e}")
        
        if self.google_enabled:
            try:
                self.providers["google"] = GoogleAuthProvider()
            except ValueError as e:
                print(f"Google auth disabled: {e}")
        
        if self.apple_enabled:
            try:
                self.providers["apple"] = AppleAuthProvider()
            except ValueError as e:
                print(f"Apple auth disabled: {e}")
        
        if not self.providers:
            raise ValueError("No authentication providers are configured")
        
        self.default_provider = os.getenv("DEFAULT_AUTH_PROVIDER", "microsoft")
        self.require_authentication = os.getenv("REQUIRE_AUTHENTICATION", "true").lower() == "true"

    def get_authorization_url(
        self, 
        provider: str, 
        redirect_uri: str, 
        state: Optional[str] = None
    ) -> str:
        """Get OAuth authorization URL for a provider.
        
        Args:
            provider: Provider name (microsoft, google)
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
            
        Raises:
            ValueError: If provider is not supported or not enabled
        """
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' is not enabled")
        
        provider_instance = self.providers[provider]
        
        if provider == "apple":
            # Apple Sign-In is handled client-side on iOS/macOS
            raise ValueError("Apple Sign-In must be initiated from iOS/macOS client")
        
        return provider_instance.get_authorization_url(redirect_uri, state)

    def handle_oauth_callback(
        self, 
        provider: str, 
        authorization_code: str, 
        redirect_uri: str
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Handle OAuth callback and generate JWT tokens.
        
        Args:
            provider: Provider name (microsoft, google, apple)
            authorization_code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization request
            
        Returns:
            Tuple of (access_token, refresh_token, user_info)
            
        Raises:
            ValueError: If provider is not supported
            requests.HTTPError: If OAuth flow fails
        """
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' is not enabled")
        
        provider_instance = self.providers[provider]
        
        # Exchange code for provider tokens
        token_response = provider_instance.exchange_code_for_token(
            authorization_code, 
            redirect_uri
        )
        
        provider_access_token = token_response["access_token"]
        
        # Get user info from provider
        if provider == "apple":
            # For Apple, decode ID token to get user info
            user_info = provider_instance.verify_id_token(token_response["id_token"])
        else:
            user_info = provider_instance.get_user_info(provider_access_token)
        
        # Extract user details
        user_id = self._extract_user_id(provider, user_info)
        email = self._extract_email(provider, user_info)
        
        # Validate institutional email if using Microsoft
        if provider == "microsoft":
            if not provider_instance.validate_institutional_email(email):
                raise ValueError(
                    f"Email {email} does not belong to authorized institutional domain"
                )
        
        # Generate our JWT tokens
        access_token = self.jwt_handler.create_access_token(
            user_id=user_id,
            email=email,
            provider=provider,
            additional_claims={
                "provider_access_token": provider_access_token,
                "name": self._extract_name(provider, user_info),
            }
        )
        
        refresh_token = self.jwt_handler.create_refresh_token(user_id)
        
        return access_token, refresh_token, user_info

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT access token.
        
        Args:
            token: JWT access token
            
        Returns:
            Token payload with user information
            
        Raises:
            JWTError: If token is invalid or expired
        """
        return self.jwt_handler.verify_token(token, token_type="access")

    def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            JWTError: If refresh token is invalid
        """
        # Verify refresh token
        payload = self.jwt_handler.verify_token(refresh_token, token_type="refresh")
        user_id = payload["sub"]
        
        # Get user info from stored data (in production, fetch from database)
        # For now, we'll create new tokens with minimal claims
        
        # Generate new tokens
        access_token = self.jwt_handler.create_access_token(
            user_id=user_id,
            email="",  # Should fetch from database
            provider="",  # Should fetch from database
        )
        
        new_refresh_token = self.jwt_handler.create_refresh_token(user_id)
        
        return access_token, new_refresh_token

    def revoke_token(self, token: str, provider: str) -> bool:
        """Revoke a token with the provider.
        
        Args:
            token: Token to revoke
            provider: Provider name
            
        Returns:
            True if revocation successful
        """
        if provider not in self.providers:
            return False
        
        provider_instance = self.providers[provider]
        return provider_instance.revoke_token(token)

    def _extract_user_id(self, provider: str, user_info: Dict[str, Any]) -> str:
        """Extract user ID from provider user info.
        
        Args:
            provider: Provider name
            user_info: User information from provider
            
        Returns:
            User ID string
        """
        if provider == "microsoft":
            return user_info.get("id", "")
        elif provider == "google":
            return user_info.get("sub", "")
        elif provider == "apple":
            return user_info.get("sub", "")
        return ""

    def _extract_email(self, provider: str, user_info: Dict[str, Any]) -> str:
        """Extract email from provider user info.
        
        Args:
            provider: Provider name
            user_info: User information from provider
            
        Returns:
            Email address
        """
        if provider == "microsoft":
            return user_info.get("mail") or user_info.get("userPrincipalName", "")
        elif provider == "google":
            return user_info.get("email", "")
        elif provider == "apple":
            return user_info.get("email", "")
        return ""

    def _extract_name(self, provider: str, user_info: Dict[str, Any]) -> str:
        """Extract display name from provider user info.
        
        Args:
            provider: Provider name
            user_info: User information from provider
            
        Returns:
            Display name
        """
        if provider == "microsoft":
            return user_info.get("displayName", "")
        elif provider == "google":
            return user_info.get("name", "")
        elif provider == "apple":
            # Apple only provides name on first sign-in
            return user_info.get("name", {}).get("firstName", "") + " " + \
                   user_info.get("name", {}).get("lastName", "")
        return ""

    def is_authentication_required(self) -> bool:
        """Check if authentication is required for API access.
        
        Returns:
            True if authentication is required
        """
        return self.require_authentication

    def get_enabled_providers(self) -> list:
        """Get list of enabled authentication providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
