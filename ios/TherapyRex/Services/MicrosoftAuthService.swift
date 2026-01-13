import Foundation
import MSAL

/// Microsoft authentication service using MSAL (Microsoft Authentication Library)
class MicrosoftAuthService {
    static let shared = MicrosoftAuthService()
    
    private var applicationContext: MSALPublicClientApplication?
    private var currentAccount: MSALAccount?
    
    // Configuration from environment or Info.plist
    private let clientId: String
    private let authority: String
    private let redirectUri: String
    private let scopes = ["User.Read", "email", "profile", "openid"]
    
    private init() {
        // Load configuration
        // In production, these should be loaded from Info.plist or environment
        self.clientId = Bundle.main.object(forInfoDictionaryKey: "AZURE_CLIENT_ID") as? String ?? ""
        self.authority = Bundle.main.object(forInfoDictionaryKey: "AZURE_AUTHORITY") as? String ?? "https://login.microsoftonline.com/common"
        self.redirectUri = Bundle.main.object(forInfoDictionaryKey: "AZURE_REDIRECT_URI_IOS") as? String ?? "msauth.com.therapyrex.app://auth"
        
        setupMSAL()
    }
    
    // MARK: - Setup
    
    private func setupMSAL() {
        do {
            guard let authorityURL = URL(string: authority) else {
                print("Invalid authority URL")
                return
            }
            
            let authority = try MSALAuthority(url: authorityURL)
            
            let msalConfiguration = MSALPublicClientApplicationConfig(
                clientId: clientId,
                redirectUri: redirectUri,
                authority: authority
            )
            
            self.applicationContext = try MSALPublicClientApplication(configuration: msalConfiguration)
        } catch {
            print("Unable to create MSAL application: \(error)")
        }
    }
    
    // MARK: - Sign In
    
    func signIn() async throws -> MSALResult {
        guard let applicationContext = applicationContext else {
            throw MSALError.init(.internalError, userInfo: ["error": "Application context not initialized"])
        }
        
        let parameters = MSALInteractiveTokenParameters(scopes: scopes)
        
        // Get the current view controller for presenting the authentication UI
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let rootViewController = windowScene.windows.first?.rootViewController {
            parameters.parentViewController = rootViewController
        }
        
        parameters.promptType = .selectAccount
        
        return try await withCheckedThrowingContinuation { continuation in
            applicationContext.acquireToken(with: parameters) { result, error in
                if let error = error {
                    continuation.resume(throwing: error)
                } else if let result = result {
                    self.currentAccount = result.account
                    continuation.resume(returning: result)
                } else {
                    continuation.resume(throwing: MSALError.init(.internalError, userInfo: ["error": "No result"]))
                }
            }
        }
    }
    
    // MARK: - Sign In Silently
    
    func signInSilently() async throws -> MSALResult {
        guard let applicationContext = applicationContext else {
            throw MSALError.init(.internalError, userInfo: ["error": "Application context not initialized"])
        }
        
        guard let account = currentAccount else {
            throw MSALError.init(.internalError, userInfo: ["error": "No current account"])
        }
        
        let parameters = MSALSilentTokenParameters(scopes: scopes, account: account)
        
        return try await withCheckedThrowingContinuation { continuation in
            applicationContext.acquireTokenSilent(with: parameters) { result, error in
                if let error = error {
                    continuation.resume(throwing: error)
                } else if let result = result {
                    continuation.resume(returning: result)
                } else {
                    continuation.resume(throwing: MSALError.init(.internalError, userInfo: ["error": "No result"]))
                }
            }
        }
    }
    
    // MARK: - Refresh Token
    
    func refreshToken(_ refreshToken: String) async throws -> MSALResult {
        // MSAL handles token refresh internally with acquireTokenSilent
        return try await signInSilently()
    }
    
    // MARK: - Sign Out
    
    func signOut() async {
        guard let applicationContext = applicationContext,
              let account = currentAccount else {
            return
        }
        
        do {
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
                applicationContext.remove(account) { success, error in
                    if let error = error {
                        continuation.resume(throwing: error)
                    } else {
                        self.currentAccount = nil
                        continuation.resume()
                    }
                }
            }
        } catch {
            print("Error signing out: \(error)")
        }
    }
    
    // MARK: - Get Current Account
    
    func getCurrentAccount() async -> MSALAccount? {
        guard let applicationContext = applicationContext else {
            return nil
        }
        
        do {
            let accounts = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[MSALAccount], Error>) in
                applicationContext.allAccounts { accounts, error in
                    if let error = error {
                        continuation.resume(throwing: error)
                    } else {
                        continuation.resume(returning: accounts ?? [])
                    }
                }
            }
            
            self.currentAccount = accounts.first
            return accounts.first
        } catch {
            print("Error getting accounts: \(error)")
            return nil
        }
    }
}

// MARK: - UIApplication Extension

#if canImport(UIKit)
import UIKit

extension UIApplication {
    var currentKeyWindow: UIWindow? {
        connectedScenes
            .filter { $0.activationState == .foregroundActive }
            .first(where: { $0 is UIWindowScene })
            .flatMap({ $0 as? UIWindowScene })?.windows
            .first(where: \.isKeyWindow)
    }
}
#endif
