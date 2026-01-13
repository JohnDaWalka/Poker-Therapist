// Authentication service for Windows desktop app
import { PublicClientApplication } from '@azure/msal-browser'
import { GoogleAuth } from 'google-auth-library'

class AuthService {
  constructor() {
    this.msalInstance = null
    this.googleAuth = null
    this.currentUser = null
    this.accessToken = null
    
    this.initMicrosoft()
    this.initGoogle()
  }
  
  // MARK: - Microsoft Authentication (MSAL)
  
  initMicrosoft() {
    const msalConfig = {
      auth: {
        clientId: process.env.AZURE_CLIENT_ID || '',
        authority: process.env.AZURE_AUTHORITY || 'https://login.microsoftonline.com/common',
        redirectUri: process.env.AZURE_REDIRECT_URI_WINDOWS || 'http://localhost:3000/auth/callback'
      },
      cache: {
        cacheLocation: 'localStorage',
        storeAuthStateInCookie: false
      }
    }
    
    if (msalConfig.auth.clientId) {
      this.msalInstance = new PublicClientApplication(msalConfig)
    }
  }
  
  async signInWithMicrosoft() {
    if (!this.msalInstance) {
      throw new Error('Microsoft authentication not configured')
    }
    
    const loginRequest = {
      scopes: ['User.Read', 'email', 'profile', 'openid']
    }
    
    try {
      const response = await this.msalInstance.loginPopup(loginRequest)
      this.accessToken = response.accessToken
      this.currentUser = {
        id: response.account.localAccountId,
        email: response.account.username,
        name: response.account.name,
        provider: 'microsoft'
      }
      
      // Store token securely in electron's safeStorage
      this.storeToken(response.accessToken, 'access_token')
      
      return this.currentUser
    } catch (error) {
      console.error('Microsoft sign-in failed:', error)
      throw error
    }
  }
  
  async signInSilentlyWithMicrosoft() {
    if (!this.msalInstance) {
      throw new Error('Microsoft authentication not configured')
    }
    
    const accounts = this.msalInstance.getAllAccounts()
    if (accounts.length === 0) {
      throw new Error('No accounts found')
    }
    
    const silentRequest = {
      scopes: ['User.Read', 'email', 'profile', 'openid'],
      account: accounts[0]
    }
    
    try {
      const response = await this.msalInstance.acquireTokenSilent(silentRequest)
      this.accessToken = response.accessToken
      this.currentUser = {
        id: response.account.localAccountId,
        email: response.account.username,
        name: response.account.name,
        provider: 'microsoft'
      }
      
      return this.currentUser
    } catch {
      // If silent sign-in fails, fall back to interactive
      return await this.signInWithMicrosoft()
    }
  }
  
  // MARK: - Google Authentication
  
  initGoogle() {
    const clientId = process.env.GOOGLE_CLIENT_ID
    if (clientId) {
      this.googleAuth = new GoogleAuth({
        clientId: clientId,
        scopes: [
          'openid',
          'email',
          'profile',
          'https://www.googleapis.com/auth/devstorage.read_write'
        ]
      })
    }
  }
  
  async signInWithGoogle() {
    // For Electron apps, use OAuth flow with system browser
    // This is a simplified version - in production, use proper OAuth PKCE flow
    const authUrl = this.getGoogleAuthUrl()
    
    // Open auth URL in system browser
    const { shell } = require('electron')
    await shell.openExternal(authUrl)
    
    // Listen for callback (implement callback handler in main process)
    return new Promise((resolve, reject) => {
      // Set up IPC listener for auth callback
      window.api.onAuthCallback((provider, code) => {
        if (provider === 'google') {
          this.handleGoogleCallback(code)
            .then(resolve)
            .catch(reject)
        }
      })
    })
  }
  
  getGoogleAuthUrl() {
    const clientId = process.env.GOOGLE_CLIENT_ID
    const redirectUri = process.env.GOOGLE_REDIRECT_URI_WINDOWS || 'http://localhost:3000/google/callback'
    const scopes = encodeURIComponent('openid email profile https://www.googleapis.com/auth/devstorage.read_write')
    
    return `https://accounts.google.com/o/oauth2/v2/auth?` +
           `client_id=${clientId}&` +
           `redirect_uri=${redirectUri}&` +
           `response_type=code&` +
           `scope=${scopes}&` +
           `access_type=offline&` +
           `prompt=consent`
  }
  
  async handleGoogleCallback(authorizationCode) {
    const response = await fetch('http://localhost:8000/auth/google/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        code: authorizationCode,
        redirect_uri: process.env.GOOGLE_REDIRECT_URI_WINDOWS
      })
    })
    
    if (!response.ok) {
      throw new Error('Google authentication failed')
    }
    
    const data = await response.json()
    this.accessToken = data.access_token
    
    // Get user info
    const userInfo = await this.getGoogleUserInfo(data.access_token)
    this.currentUser = {
      id: userInfo.sub,
      email: userInfo.email,
      name: userInfo.name,
      provider: 'google'
    }
    
    this.storeToken(data.access_token, 'access_token')
    
    return this.currentUser
  }
  
  async getGoogleUserInfo(accessToken) {
    const response = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    })
    
    return await response.json()
  }
  
  // MARK: - Common Methods
  
  async signOut() {
    // Sign out from Microsoft
    if (this.msalInstance && this.currentUser?.provider === 'microsoft') {
      const accounts = this.msalInstance.getAllAccounts()
      if (accounts.length > 0) {
        await this.msalInstance.logoutPopup({
          account: accounts[0]
        })
      }
    }
    
    // Clear stored tokens
    this.clearTokens()
    
    this.currentUser = null
    this.accessToken = null
  }
  
  getAccessToken() {
    return this.accessToken || this.getStoredToken('access_token')
  }
  
  getCurrentUser() {
    return this.currentUser
  }
  
  isAuthenticated() {
    return !!this.getAccessToken()
  }
  
  // MARK: - Secure Storage (Electron safeStorage)
  
  storeToken(token, key) {
    if (window.api && window.api.safeStorage) {
      window.api.safeStorage.set(key, token)
    } else {
      // Fallback to localStorage (less secure)
      localStorage.setItem(key, token)
    }
  }
  
  getStoredToken(key) {
    if (window.api && window.api.safeStorage) {
      return window.api.safeStorage.get(key)
    } else {
      return localStorage.getItem(key)
    }
  }
  
  clearTokens() {
    if (window.api && window.api.safeStorage) {
      window.api.safeStorage.delete('access_token')
      window.api.safeStorage.delete('refresh_token')
    } else {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }
}

export default new AuthService()
