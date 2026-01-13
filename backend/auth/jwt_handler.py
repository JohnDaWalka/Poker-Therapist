"""JWT token handler for authentication."""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt


class JWTHandler:
    """Handle JWT token generation and validation."""

    def __init__(self) -> None:
        """Initialize JWT handler with configuration from environment."""
        self.secret_key = os.getenv("JWT_SECRET_KEY", "")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY must be set in environment")
        
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        self.refresh_expiration_days = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "30"))

    def create_access_token(
        self,
        user_id: str,
        email: str,
        provider: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new access token.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            provider: Authentication provider (microsoft, google, apple)
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT access token string
        """
        expires_at = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        
        payload = {
            "sub": user_id,
            "email": email,
            "provider": provider,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """Create a new refresh token.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            JWT refresh token string
        """
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_expiration_days)
        
        payload = {
            "sub": user_id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            token_type: Expected token type (access or refresh)
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid or expired
            ValueError: If token type doesn't match expected type
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise ValueError(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            
            return payload
        except JWTError as e:
            raise JWTError(f"Token validation failed: {str(e)}")

    def decode_token_without_verification(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging/logging only).
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload (unverified)
        """
        return jwt.decode(token, options={"verify_signature": False})

    def extract_user_id(self, token: str) -> Optional[str]:
        """Extract user ID from token.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID or None if token is invalid
        """
        try:
            payload = self.verify_token(token)
            return payload.get("sub")
        except (JWTError, ValueError):
            return None

    def extract_email(self, token: str) -> Optional[str]:
        """Extract email from token.
        
        Args:
            token: JWT token string
            
        Returns:
            Email address or None if token is invalid
        """
        try:
            payload = self.verify_token(token)
            return payload.get("email")
        except (JWTError, ValueError):
            return None
