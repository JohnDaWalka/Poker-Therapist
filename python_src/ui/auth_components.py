"""Streamlit authentication UI components."""

import streamlit as st
from typing import Optional
from python_src.services.auth_service import AuthenticationService, UserInfo


def render_oauth_login_buttons(auth_service: AuthenticationService) -> None:
    """Render OAuth login buttons for available providers.
    
    Args:
        auth_service: Authentication service instance
    """
    st.subheader("🔐 Sign In with OAuth/SSO")
    
    providers = auth_service.get_available_providers()
    
    if not providers:
        st.warning("⚠️ No OAuth providers configured. Please set up environment variables.")
        st.info("""
        To enable OAuth authentication, configure the following environment variables:
        
        **Microsoft/Azure AD:**
        - `MICROSOFT_CLIENT_ID`
        - `MICROSOFT_CLIENT_SECRET`
        - `MICROSOFT_TENANT_ID`
        - `MICROSOFT_REDIRECT_URI`
        
        **Google OAuth:**
        - `GOOGLE_CLIENT_ID`
        - `GOOGLE_CLIENT_SECRET`
        - `GOOGLE_REDIRECT_URI`
        
        **Apple Sign In:**
        - `APPLE_CLIENT_ID`
        - `APPLE_TEAM_ID`
        - `APPLE_KEY_ID`
        - `APPLE_PRIVATE_KEY`
        - `APPLE_REDIRECT_URI`
        """)
        return
    
    st.info(f"✅ Available providers: {', '.join(providers)}")
    
    # Microsoft/Azure AD
    if "microsoft" in providers:
        if st.button("🪟 Sign in with Microsoft", use_container_width=True):
            try:
                auth_url, state = auth_service.microsoft.get_authorization_url()
                st.session_state.oauth_state = state
                st.session_state.oauth_provider = "microsoft"
                st.markdown(f"""
                <meta http-equiv="refresh" content="0; url={auth_url}" />
                
                **Redirecting to Microsoft Sign In...**
                
                If you are not redirected automatically, [click here]({auth_url})
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error initiating Microsoft sign in: {e}")
    
    # Google OAuth
    if "google" in providers:
        if st.button("🔵 Sign in with Google", use_container_width=True):
            try:
                auth_url, state = auth_service.google.get_authorization_url()
                st.session_state.oauth_state = state
                st.session_state.oauth_provider = "google"
                st.markdown(f"""
                <meta http-equiv="refresh" content="0; url={auth_url}" />
                
                **Redirecting to Google Sign In...**
                
                If you are not redirected automatically, [click here]({auth_url})
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error initiating Google sign in: {e}")
    
    # Apple Sign In
    if "apple" in providers:
        if st.button("🍎 Sign in with Apple", use_container_width=True):
            try:
                auth_url, state = auth_service.apple.get_authorization_url()
                st.session_state.oauth_state = state
                st.session_state.oauth_provider = "apple"
                st.markdown(f"""
                <meta http-equiv="refresh" content="0; url={auth_url}" />
                
                **Redirecting to Apple Sign In...**
                
                If you are not redirected automatically, [click here]({auth_url})
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error initiating Apple sign in: {e}")


def handle_oauth_callback(auth_service: AuthenticationService) -> Optional[UserInfo]:
    """Handle OAuth callback and return user info.
    
    Args:
        auth_service: Authentication service instance
        
    Returns:
        UserInfo object if authentication successful, None otherwise
    """
    # Check for OAuth callback parameters
    query_params = st.query_params
    
    if "code" not in query_params:
        return None
    
    auth_code = query_params["code"]
    state = query_params.get("state")
    
    # Verify state parameter
    if state != st.session_state.get("oauth_state"):
        st.error("❌ Invalid OAuth state parameter. Possible CSRF attack.")
        return None
    
    provider = st.session_state.get("oauth_provider")
    
    if not provider:
        st.error("❌ Unknown OAuth provider")
        return None
    
    try:
        # Get user info based on provider
        user_info = None
        
        if provider == "microsoft":
            user_info = auth_service.microsoft.get_user_info(auth_code)
        elif provider == "google":
            user_info = auth_service.google.get_user_info(auth_code)
        elif provider == "apple":
            # Apple passes user data in the form post
            # NOTE: Apple uses response_mode=form_post, so in a production Streamlit app,
            # user data would come via POST body, not query parameters. This is a limitation
            # of Streamlit's current architecture. For production, consider using a separate
            # callback endpoint to handle Apple's POST data before redirecting to Streamlit.
            user_data = query_params.get("user")
            user_info = auth_service.apple.get_user_info(auth_code, user_data)
        
        if user_info:
            # Create session token
            session_token = auth_service.create_session_token(user_info)
            st.session_state.session_token = session_token
            st.session_state.user_info = user_info
            
            # Clear OAuth state
            del st.session_state.oauth_state
            del st.session_state.oauth_provider
            
            # Clear query parameters
            st.query_params.clear()
            
            return user_info
        else:
            st.error(f"❌ Failed to authenticate with {provider}")
            return None
            
    except Exception as e:
        st.error(f"❌ Authentication error: {e}")
        return None


def render_user_profile(user_info: UserInfo, show_logout: bool = True) -> None:
    """Render user profile information.
    
    Args:
        user_info: User information from OAuth provider
        show_logout: Whether to show logout button
    """
    st.success(f"✅ Signed in as: **{user_info.email}**")
    
    with st.expander("👤 Profile Details"):
        cols = st.columns([1, 3])
        
        with cols[0]:
            if user_info.picture:
                st.image(user_info.picture, width=80)
            else:
                st.markdown("👤")
        
        with cols[1]:
            if user_info.name:
                st.write(f"**Name:** {user_info.name}")
            st.write(f"**Email:** {user_info.email}")
            st.write(f"**Provider:** {user_info.provider.title()}")
    
    if show_logout:
        if st.button("🚪 Sign Out", use_container_width=True):
            # Clear session
            if "session_token" in st.session_state:
                del st.session_state.session_token
            if "user_info" in st.session_state:
                del st.session_state.user_info
            if "user_email" in st.session_state:
                del st.session_state.user_email
            if "user_id" in st.session_state:
                del st.session_state.user_id
            st.rerun()


def init_oauth_authentication(auth_service: AuthenticationService) -> Optional[UserInfo]:
    """Initialize OAuth authentication flow.
    
    This function should be called early in the Streamlit app to handle
    OAuth callbacks and maintain session state.
    
    Args:
        auth_service: Authentication service instance
        
    Returns:
        UserInfo object if user is authenticated, None otherwise
    """
    # Check for existing session token
    if "session_token" in st.session_state:
        payload = auth_service.verify_session_token(st.session_state.session_token)
        if payload:
            # Session is valid, return user info from session
            if "user_info" not in st.session_state:
                from python_src.services.auth_service import UserInfo
                st.session_state.user_info = UserInfo(
                    provider=payload["provider"],
                    email=payload["email"],
                    name=payload.get("name"),
                    user_id=payload.get("user_id"),
                )
            return st.session_state.user_info
        else:
            # Session expired or invalid
            del st.session_state.session_token
            if "user_info" in st.session_state:
                del st.session_state.user_info
    
    # Handle OAuth callback
    user_info = handle_oauth_callback(auth_service)
    if user_info:
        return user_info
    
    return None
