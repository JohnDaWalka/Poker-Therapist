"""Apple Sign-In authentication provider."""

import os
import time
from typing import Any, Dict, Optional

import jwt as pyjwt
import requests


class AppleAuthProvider:
    """Handle Apple Sign-In authentication for iOS, macOS, and watchOS.
    
    Supports:
    - Sign in with Apple on iOS/macOS/watchOS
    - Server-side validation of Apple ID tokens
    - Apple REST API authentication
    """

    def __init__(self) -> None:
        """Initialize Apple authentication provider with configuration."""
        self.team_id = os.getenv("APPLE_TEAM_ID", "")
        self.services_id = os.getenv("APPLE_SERVICES_ID", "")
        self.key_id = os.getenv("APPLE_KEY_ID", "")
        self.bundle_id_ios = os.getenv("APPLE_BUNDLE_ID_IOS", "")
        self.bundle_id_watchos = os.getenv("APPLE_BUNDLE_ID_WATCHOS", "")
        
        # Private key for server-side authentication
        private_key_path = os.getenv("APPLE_PRIVATE_KEY_PATH", "")
        private_key_content = os.getenv("APPLE_PRIVATE_KEY", "")
        
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, "r") as f:
                self.private_key = f.read()
        elif private_key_content:
            self.private_key = private_key_content
        else:
            self.private_key = ""
        
        # Apple endpoints
        self.token_uri = "https://appleid.apple.com/auth/token"
        self.keys_uri = "https://appleid.apple.com/auth/keys"
        self.revoke_uri = "https://appleid.apple.com/auth/revoke"
        
        if not self.team_id:
            raise ValueError("APPLE_TEAM_ID must be set in environment")
        if not self.services_id:
            raise ValueError("APPLE_SERVICES_ID must be set in environment")

    def create_client_secret(self) -> str:
        """Create a client secret JWT for Apple authentication.
        
        Client secret is a JWT signed with Apple's private key.
        Valid for 6 months maximum.
        
        Returns:
            Client secret JWT
            
        Raises:
            ValueError: If private key is not configured
        """
        if not self.private_key:
            raise ValueError("Apple private key must be configured")
        if not self.key_id:
            raise ValueError("APPLE_KEY_ID must be set in environment")
        
        # JWT expires in 6 months (maximum allowed by Apple)
        expiration = int(time.time()) + (6 * 30 * 24 * 60 * 60)
        
        headers = {
            "kid": self.key_id,
            "alg": "ES256",
        }
        
        payload = {
            "iss": self.team_id,
            "iat": int(time.time()),
            "exp": expiration,
            "aud": "https://appleid.apple.com",
            "sub": self.services_id,
        }
        
        return pyjwt.encode(payload, self.private_key, algorithm="ES256", headers=headers)

    def exchange_code_for_token(
        self, 
        authorization_code: str, 
        redirect_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from Apple Sign-In
            redirect_uri: Optional redirect URI (required for web)
            
        Returns:
            Token response with access_token, id_token, refresh_token
            
        Raises:
            requests.HTTPError: If token exchange fails
        """
        client_secret = self.create_client_secret()
        
        data = {
            "client_id": self.services_id,
            "client_secret": client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
        }
        
        if redirect_uri:
            data["redirect_uri"] = redirect_uri
        
        response = requests.post(self.token_uri, data=data)
        response.raise_for_status()
        
        return response.json()

    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify and decode Apple ID token.
        
        Apple ID tokens are JWTs that need to be verified against Apple's public keys.
        
        Args:
            id_token: Apple ID token (JWT)
            
        Returns:
            Decoded token claims including sub (user ID), email, etc.
            
        Raises:
            pyjwt.InvalidTokenError: If token verification fails
        """
        # Get Apple's public keys
        response = requests.get(self.keys_uri)
        response.raise_for_status()
        keys = response.json()["keys"]
        
        # Decode header to get key ID
        unverified_header = pyjwt.get_unverified_header(id_token)
        key_id = unverified_header["kid"]
        
        # Find the matching public key
        public_key = None
        for key in keys:
            if key["kid"] == key_id:
                public_key = pyjwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not public_key:
            raise ValueError("Public key not found for token")
        
        # Verify and decode token
        decoded = pyjwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=self.services_id,
            issuer="https://appleid.apple.com",
        )
        
        return decoded

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token response
            
        Raises:
            requests.HTTPError: If token refresh fails
        """
        client_secret = self.create_client_secret()
        
        data = {
            "client_id": self.services_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        response = requests.post(self.token_uri, data=data)
        response.raise_for_status()
        
        return response.json()

    def revoke_token(self, token: str, token_type_hint: str = "access_token") -> bool:
        """Revoke an access or refresh token.
        
        Args:
            token: Token to revoke
            token_type_hint: Type of token ('access_token' or 'refresh_token')
            
        Returns:
            True if revocation successful
        """
        try:
            client_secret = self.create_client_secret()
            
            data = {
                "client_id": self.services_id,
                "client_secret": client_secret,
                "token": token,
                "token_type_hint": token_type_hint,
            }
            
            response = requests.post(self.revoke_uri, data=data)
            return response.status_code == 200
        except (requests.RequestException, ValueError):
            return False

    def validate_bundle_id(self, bundle_id: str) -> bool:
        """Validate that bundle ID is authorized.
        
        Args:
            bundle_id: iOS/watchOS bundle identifier
            
        Returns:
            True if bundle ID is authorized
        """
        return bundle_id in [self.bundle_id_ios, self.bundle_id_watchos]
