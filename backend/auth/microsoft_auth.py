"""Microsoft Azure AD / Windows account authentication provider."""

import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests


class MicrosoftAuthProvider:
    """Handle Microsoft Azure AD and Windows account authentication.
    
    Supports:
    - Microsoft personal accounts (e.g., @outlook.com, @hotmail.com)
    - Azure AD organizational accounts
    - Institutional SSO (e.g., @ctstate.edu)
    """

    def __init__(self) -> None:
        """Initialize Microsoft authentication provider with configuration."""
        self.tenant_id = os.getenv("AZURE_TENANT_ID", "common")
        self.client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        self.authority = os.getenv(
            "AZURE_AUTHORITY", 
            f"https://login.microsoftonline.com/{self.tenant_id}"
        )
        self.scopes = os.getenv("AZURE_SCOPES", "User.Read email profile openid").split()
        self.institutional_domain = os.getenv("INSTITUTIONAL_EMAIL_DOMAIN", "")
        
        if not self.client_id:
            raise ValueError("AZURE_CLIENT_ID must be set in environment")
        if not self.client_secret:
            raise ValueError("AZURE_CLIENT_SECRET must be set in environment")

    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """Generate OAuth 2.0 authorization URL.
        
        Args:
            redirect_uri: URI to redirect to after authorization
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "response_mode": "query",
        }
        
        if state:
            params["state"] = state
        
        # For institutional SSO, add domain_hint
        if self.institutional_domain:
            params["domain_hint"] = self.institutional_domain
        
        auth_url = f"{self.authority}/oauth2/v2.0/authorize"
        return f"{auth_url}?{urlencode(params)}"

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
        token_url = f"{self.authority}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": " ".join(self.scopes),
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        return response.json()

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information from Microsoft Graph API.
        
        Args:
            access_token: Microsoft access token
            
        Returns:
            User profile data including id, email, name, etc.
            
        Raises:
            requests.HTTPError: If API request fails
        """
        graph_url = "https://graph.microsoft.com/v1.0/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        response = requests.get(graph_url, headers=headers)
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
        token_url = f"{self.authority}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": " ".join(self.scopes),
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        return response.json()

    def validate_institutional_email(self, email: str) -> bool:
        """Validate that email belongs to institutional domain.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email matches institutional domain or no domain restriction
        """
        if not self.institutional_domain:
            return True  # No restriction
        
        return email.lower().endswith(f"@{self.institutional_domain.lower()}")

    def revoke_token(self, token: str) -> bool:
        """Revoke an access or refresh token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        revoke_url = f"{self.authority}/oauth2/v2.0/logout"
        
        try:
            # Microsoft doesn't have a standard revocation endpoint
            # Instead, we use logout endpoint with post_logout_redirect_uri
            params = {
                "post_logout_redirect_uri": "http://localhost:8000/logout",
            }
            response = requests.get(revoke_url, params=params)
            return response.status_code == 200
        except requests.RequestException:
            return False
