import Foundation
import AuthenticationServices

/// Authentication service for managing user authentication across multiple providers
@MainActor
class AuthenticationService: NSObject, ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var authToken: String?
    @Published var errorMessage: String?
    
    static let shared = AuthenticationService()
    
    private let keychainService = KeychainService.shared
    private let msalService = MicrosoftAuthService.shared
    private let googleAuthService = GoogleAuthService.shared
    
    private override init() {
        super.init()
        checkAuthenticationStatus()
    }
    
    // MARK: - Authentication Status
    
    func checkAuthenticationStatus() {
        // Check if we have a valid token in keychain
        if let token = keychainService.getToken(for: "access_token"),
           let expirationDate = keychainService.getTokenExpiration(for: "access_token"),
           expirationDate > Date() {
            self.authToken = token
            self.isAuthenticated = true
            loadUserInfo()
        } else {
            self.isAuthenticated = false
            self.currentUser = nil
            self.authToken = nil
        }
    }
    
    // MARK: - Sign In with Apple
    
    func signInWithApple() {
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]
        
        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.performRequests()
    }
    
    // MARK: - Sign In with Microsoft
    
    func signInWithMicrosoft() async throws {
        do {
            let result = try await msalService.signIn()
            self.authToken = result.accessToken
            self.isAuthenticated = true
            
            // Save token to keychain
            keychainService.saveToken(result.accessToken, for: "access_token")
            if let expiration = result.expiresOn {
                keychainService.saveTokenExpiration(expiration, for: "access_token")
            }
            
            // Load user info
            loadUserInfo()
        } catch {
            self.errorMessage = "Microsoft sign-in failed: \(error.localizedDescription)"
            throw error
        }
    }
    
    // MARK: - Sign In with Google
    
    func signInWithGoogle() async throws {
        do {
            let result = try await googleAuthService.signIn()
            self.authToken = result.accessToken
            self.isAuthenticated = true
            
            // Save token to keychain
            keychainService.saveToken(result.accessToken, for: "access_token")
            if let expiration = result.expiresOn {
                keychainService.saveTokenExpiration(expiration, for: "access_token")
            }
            
            // Load user info
            loadUserInfo()
        } catch {
            self.errorMessage = "Google sign-in failed: \(error.localizedDescription)"
            throw error
        }
    }
    
    // MARK: - Sign Out
    
    func signOut() async {
        // Clear tokens from keychain
        keychainService.deleteToken(for: "access_token")
        keychainService.deleteToken(for: "refresh_token")
        
        // Sign out from providers
        await msalService.signOut()
        googleAuthService.signOut()
        
        // Reset state
        self.isAuthenticated = false
        self.currentUser = nil
        self.authToken = nil
    }
    
    // MARK: - Token Refresh
    
    func refreshTokenIfNeeded() async throws {
        guard let expiration = keychainService.getTokenExpiration(for: "access_token") else {
            return
        }
        
        // Refresh if token expires in less than 5 minutes
        if expiration.timeIntervalSinceNow < 300 {
            try await refreshToken()
        }
    }
    
    private func refreshToken() async throws {
        guard let refreshToken = keychainService.getToken(for: "refresh_token") else {
            throw AuthError.noRefreshToken
        }
        
        // Try to refresh with the appropriate provider
        // This is a simplified version - in production, track which provider was used
        if let result = try? await msalService.refreshToken(refreshToken) {
            keychainService.saveToken(result.accessToken, for: "access_token")
            if let expiration = result.expiresOn {
                keychainService.saveTokenExpiration(expiration, for: "access_token")
            }
            self.authToken = result.accessToken
        }
    }
    
    // MARK: - User Info
    
    private func loadUserInfo() {
        // In production, fetch user info from backend API using the token
        // For now, decode token to get basic info (if JWT)
        if let token = authToken {
            // Decode JWT token (simplified - use proper JWT library in production)
            self.currentUser = User(
                id: "user_id",
                email: "user@example.com",
                name: "User Name",
                provider: "microsoft"
            )
        }
    }
}

// MARK: - ASAuthorizationControllerDelegate

extension AuthenticationService: ASAuthorizationControllerDelegate {
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let userIdentifier = appleIDCredential.user
            let identityToken = appleIDCredential.identityToken
            let authorizationCode = appleIDCredential.authorizationCode
            
            // Send to backend for validation and JWT generation
            Task {
                do {
                    if let tokenData = identityToken,
                       let tokenString = String(data: tokenData, encoding: .utf8) {
                        // Exchange Apple token with backend
                        try await exchangeAppleToken(tokenString)
                    }
                } catch {
                    self.errorMessage = "Apple sign-in failed: \(error.localizedDescription)"
                }
            }
        }
    }
    
    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        self.errorMessage = "Apple sign-in failed: \(error.localizedDescription)"
    }
    
    private func exchangeAppleToken(_ token: String) async throws {
        // Call backend API to exchange Apple token for our JWT
        let url = URL(string: "\(APIClient.shared.baseURL)/auth/apple/callback")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["id_token": token]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(AuthResponse.self, from: data)
        
        // Save tokens
        keychainService.saveToken(response.accessToken, for: "access_token")
        keychainService.saveToken(response.refreshToken, for: "refresh_token")
        
        self.authToken = response.accessToken
        self.isAuthenticated = true
        loadUserInfo()
    }
}

// MARK: - Models

struct User {
    let id: String
    let email: String
    let name: String
    let provider: String
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let expiresIn: Int
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case expiresIn = "expires_in"
    }
}

enum AuthError: Error {
    case noRefreshToken
    case invalidToken
    case networkError
}
