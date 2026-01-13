"""Google OAuth 2.0 authentication provider."""

import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests


class GoogleAuthProvider:
    """Handle Google OAuth 2.0 authentication and Google Cloud Platform integration.
    
    Supports:
    - Google account sign-in
    - Google Cloud Platform API access
    - OpenID Connect
    """

    def __init__(self) -> None:
        """Initialize Google authentication provider with configuration."""
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
        
        # OAuth scopes
        default_scopes = "openid email profile https://www.googleapis.com/auth/devstorage.read_write"
        self.scopes = os.getenv("GOOGLE_OAUTH_SCOPES", default_scopes).split()
        
        # OAuth endpoints
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.userinfo_uri = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.revoke_uri = "https://oauth2.googleapis.com/revoke"
        
        if not self.client_id:
            raise ValueError("GOOGLE_CLIENT_ID must be set in environment")
        if not self.client_secret:
            raise ValueError("GOOGLE_CLIENT_SECRET must be set in environment")

    def get_authorization_url(
        self, 
        redirect_uri: str, 
        state: Optional[str] = None,
        access_type: str = "offline",
        prompt: str = "consent",
    ) -> str:
        """Generate OAuth 2.0 authorization URL.
        
        Args:
            redirect_uri: URI to redirect to after authorization
            state: Optional state parameter for CSRF protection
            access_type: 'offline' to get refresh token, 'online' otherwise
            prompt: 'consent' to force consent screen, 'select_account' to show account picker
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "access_type": access_type,
            "prompt": prompt,
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_uri}?{urlencode(params)}"

    def exchange_code_for_token(
        self, 
        authorization_code: str, 
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization request
            
        Returns:
            Token response with access_token, id_token, refresh_token, etc.
            
        Raises:
            requests.HTTPError: If token exchange fails
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        
        response = requests.post(self.token_uri, data=data)
        response.raise_for_status()
        
        return response.json()

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information from Google.
        
        Args:
            access_token: Google access token
            
        Returns:
            User profile data including sub (user ID), email, name, picture, etc.
            
        Raises:
            requests.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        response = requests.get(self.userinfo_uri, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token response
            
        Raises:
            requests.HTTPError: If token refresh fails
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        response = requests.post(self.token_uri, data=data)
        response.raise_for_status()
        
        return response.json()

    def revoke_token(self, token: str) -> bool:
        """Revoke an access or refresh token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        try:
            response = requests.post(
                self.revoke_uri,
                params={"token": token},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify and decode Google ID token.
        
        Args:
            id_token: Google ID token (JWT)
            
        Returns:
            Decoded token claims
            
        Raises:
            requests.HTTPError: If verification fails
        """
        # Use Google's tokeninfo endpoint to verify
        response = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token}
        )
        response.raise_for_status()
        
        token_info = response.json()
        
        # Verify audience matches our client ID
        if token_info.get("aud") != self.client_id:
            raise ValueError("ID token audience does not match client ID")
        
        return token_info
