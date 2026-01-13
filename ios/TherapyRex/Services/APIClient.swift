import Foundation

class APIClient {
    static let shared = APIClient()
    
    private let baseURL = "http://localhost:8000"
    private let userId = "default"
    
    // Make baseURL public for authentication service
    var publicBaseURL: String {
        return baseURL
    }
    
    private init() {}
    
    // MARK: - Authentication Headers
    
    private func getAuthHeaders() -> [String: String] {
        var headers = [
            "Content-Type": "application/json"
        ]
        
        // Add authentication token if available
        if let token = KeychainService.shared.getToken(for: "access_token") {
            headers["Authorization"] = "Bearer \(token)"
        }
        
        return headers
    }
    
    private func createRequest(url: URL, method: String = "POST", body: [String: Any]? = nil) throws -> URLRequest {
        var request = URLRequest(url: url)
        request.httpMethod = method
        
        // Set headers
        for (key, value) in getAuthHeaders() {
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        // Set body if provided
        if let body = body {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }
        
        return request
    }
    
    func analyzeTriage(situation: String, emotion: String, intensity: Int, bodySensation: String, stillPlaying: Bool) async throws -> TriageResult {
        let url = URL(string: "\(baseURL)/api/triage")!
        
        let body = [
            "situation": situation,
            "emotion": emotion,
            "intensity": intensity,
            "body_sensation": bodySensation,
            "still_playing": stillPlaying,
            "user_id": userId
        ] as [String : Any]
        
        let request = try createRequest(url: url, body: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TriageResult.self, from: data)
    }
    
    func startDeepSession(stress: Int, confidence: Int, motivation: Int, recentResults: String, lifeContext: String) async throws -> DeepSessionResult {
        let url = URL(string: "\(baseURL)/api/deep-session")!
        
        let body = [
            "emotional_state": ["stress": stress, "confidence": confidence, "motivation": motivation],
            "recent_results": recentResults,
            "life_context": lifeContext,
            "recurring_themes": "",
            "user_id": userId
        ] as [String : Any]
        
        let request = try createRequest(url: url, body: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DeepSessionResult.self, from: data)
    }
}
