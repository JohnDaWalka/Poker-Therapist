import Foundation

class APIClient {
    static let shared = APIClient()
    
    private let baseURL = "http://localhost:8000"
    private let userId = "default"
    
    private init() {}
    
    func analyzeTriage(situation: String, emotion: String, intensity: Int, bodySensation: String, stillPlaying: Bool) async throws -> TriageResult {
        let url = URL(string: "\(baseURL)/api/triage")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "situation": situation,
            "emotion": emotion,
            "intensity": intensity,
            "body_sensation": bodySensation,
            "still_playing": stillPlaying,
            "user_id": userId
        ] as [String : Any]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TriageResult.self, from: data)
    }
    
    func startDeepSession(stress: Int, confidence: Int, motivation: Int, recentResults: String, lifeContext: String) async throws -> DeepSessionResult {
        let url = URL(string: "\(baseURL)/api/deep-session")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "emotional_state": ["stress": stress, "confidence": confidence, "motivation": motivation],
            "recent_results": recentResults,
            "life_context": lifeContext,
            "recurring_themes": "",
            "user_id": userId
        ] as [String : Any]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DeepSessionResult.self, from: data)
    }
}
