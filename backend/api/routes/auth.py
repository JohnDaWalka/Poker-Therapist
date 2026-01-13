"""Authentication routes for OAuth and SSO."""

from typing import Dict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from backend.api.auth import auth_config, oauth
from backend.agent.memory.firestore_adapter import firestore_adapter


router = APIRouter()


@router.get("/auth/login/microsoft")
async def login_microsoft(request: Request):
    """Initiate Microsoft Azure AD OAuth flow.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Redirect to Microsoft login
    """
    redirect_uri = request.url_for("auth_microsoft_callback")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback/microsoft")
async def auth_microsoft_callback(request: Request) -> Dict:
    """Handle Microsoft OAuth callback.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Authentication response with token
    """
    try:
        token = await oauth.microsoft.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        email = user_info.get("email")
        
        # Validate institutional email
        if not auth_config.is_institutional_email(email):
            raise HTTPException(
                status_code=403, 
                detail="Access denied. Please use your institutional email."
            )
        
        # Create or update user in Firestore
        user_id = user_info.get("sub")
        await firestore_adapter.create_user(user_id, email)
        
        # Create JWT token
        access_token = auth_config.create_access_token({
            "sub": user_id,
            "email": email,
            "provider": "microsoft",
            "name": user_info.get("name"),
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "name": user_info.get("name"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/login/google")
async def login_google(request: Request):
    """Initiate Google OAuth flow.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Redirect to Google login
    """
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback/google")
async def auth_google_callback(request: Request) -> Dict:
    """Handle Google OAuth callback.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Authentication response with token
    """
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        email = user_info.get("email")
        
        # Validate user
        if not auth_config.validate_user(email, "google"):
            raise HTTPException(
                status_code=403, 
                detail="Access denied. You are not authorized to use this application."
            )
        
        # Create or update user in Firestore
        user_id = user_info.get("sub")
        await firestore_adapter.create_user(user_id, email)
        
        # Create JWT token
        access_token = auth_config.create_access_token({
            "sub": user_id,
            "email": email,
            "provider": "google",
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/logout")
async def logout() -> Dict:
    """Logout endpoint.
    
    Returns:
        Logout confirmation
    """
    return {"message": "Logged out successfully"}


@router.get("/auth/me")
async def get_current_user_info(request: Request) -> Dict:
    """Get current user information.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Current user information
    """
    from backend.api.auth import get_current_user
    from fastapi import Depends
    
    # This would be used with dependency injection in the actual route
    # For now, return placeholder
    return {
        "message": "Use bearer token to authenticate",
        "example": "Authorization: Bearer <your-token>"
    }
