import Foundation
import GoogleSignIn

/// Google authentication service using Google Sign-In SDK
class GoogleAuthService {
    static let shared = GoogleAuthService()
    
    private var currentUser: GIDGoogleUser?
    
    // Configuration from environment or Info.plist
    private let clientId: String
    
    private init() {
        // Load configuration
        // In production, this should be loaded from Info.plist
        self.clientId = Bundle.main.object(forInfoDictionaryKey: "GOOGLE_CLIENT_ID") as? String ?? ""
        
        // Configure Google Sign-In
        let configuration = GIDConfiguration(clientID: clientId)
        GIDSignIn.sharedInstance.configuration = configuration
    }
    
    // MARK: - Sign In
    
    func signIn() async throws -> GoogleAuthResult {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let rootViewController = windowScene.windows.first?.rootViewController else {
            throw GoogleAuthError.noRootViewController
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            GIDSignIn.sharedInstance.signIn(withPresenting: rootViewController) { result, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }
                
                guard let result = result else {
                    continuation.resume(throwing: GoogleAuthError.noResult)
                    return
                }
                
                self.currentUser = result.user
                
                guard let idToken = result.user.idToken?.tokenString,
                      let accessToken = result.user.accessToken.tokenString else {
                    continuation.resume(throwing: GoogleAuthError.noToken)
                    return
                }
                
                let authResult = GoogleAuthResult(
                    accessToken: accessToken,
                    idToken: idToken,
                    refreshToken: result.user.refreshToken.tokenString,
                    expiresOn: result.user.accessToken.expirationDate,
                    user: result.user
                )
                
                continuation.resume(returning: authResult)
            }
        }
    }
    
    // MARK: - Sign In Silently
    
    func signInSilently() async throws -> GoogleAuthResult {
        return try await withCheckedThrowingContinuation { continuation in
            GIDSignIn.sharedInstance.restorePreviousSignIn { user, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }
                
                guard let user = user else {
                    continuation.resume(throwing: GoogleAuthError.noUser)
                    return
                }
                
                self.currentUser = user
                
                guard let idToken = user.idToken?.tokenString,
                      let accessToken = user.accessToken.tokenString else {
                    continuation.resume(throwing: GoogleAuthError.noToken)
                    return
                }
                
                let authResult = GoogleAuthResult(
                    accessToken: accessToken,
                    idToken: idToken,
                    refreshToken: user.refreshToken.tokenString,
                    expiresOn: user.accessToken.expirationDate,
                    user: user
                )
                
                continuation.resume(returning: authResult)
            }
        }
    }
    
    // MARK: - Refresh Token
    
    func refreshToken(_ refreshToken: String) async throws -> GoogleAuthResult {
        guard let currentUser = currentUser else {
            throw GoogleAuthError.noUser
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            currentUser.refreshTokensIfNeeded { user, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }
                
                guard let user = user else {
                    continuation.resume(throwing: GoogleAuthError.noUser)
                    return
                }
                
                guard let idToken = user.idToken?.tokenString,
                      let accessToken = user.accessToken.tokenString else {
                    continuation.resume(throwing: GoogleAuthError.noToken)
                    return
                }
                
                let authResult = GoogleAuthResult(
                    accessToken: accessToken,
                    idToken: idToken,
                    refreshToken: user.refreshToken.tokenString,
                    expiresOn: user.accessToken.expirationDate,
                    user: user
                )
                
                continuation.resume(returning: authResult)
            }
        }
    }
    
    // MARK: - Sign Out
    
    func signOut() {
        GIDSignIn.sharedInstance.signOut()
        currentUser = nil
    }
    
    // MARK: - Get Current User
    
    func getCurrentUser() -> GIDGoogleUser? {
        return currentUser ?? GIDSignIn.sharedInstance.currentUser
    }
    
    // MARK: - Handle URL
    
    func handleURL(_ url: URL) -> Bool {
        return GIDSignIn.sharedInstance.handle(url)
    }
}

// MARK: - Models

struct GoogleAuthResult {
    let accessToken: String
    let idToken: String
    let refreshToken: String
    let expiresOn: Date?
    let user: GIDGoogleUser
}

enum GoogleAuthError: Error {
    case noRootViewController
    case noResult
    case noToken
    case noUser
    
    var localizedDescription: String {
        switch self {
        case .noRootViewController:
            return "No root view controller found"
        case .noResult:
            return "No result from Google Sign-In"
        case .noToken:
            return "No token received from Google"
        case .noUser:
            return "No user signed in"
        }
    }
}
