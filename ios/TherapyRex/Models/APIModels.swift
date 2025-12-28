import Foundation

struct TriageResult: Codable {
    let severity: Int
    let shouldStop: Bool
    let aiGuidance: String
    let breathingExercise: String
    let microPlan: [String]
    
    enum CodingKeys: String, CodingKey {
        case severity
        case shouldStop = "should_stop"
        case aiGuidance = "ai_guidance"
        case breathingExercise = "breathing_exercise"
        case microPlan = "micro_plan"
    }
}

struct DeepSessionResult: Codable {
    let sessionSummary: String
    let cognitiveReframes: [String]
    let actionPlan: [ActionItem]
    
    enum CodingKeys: String, CodingKey {
        case sessionSummary = "session_summary"
        case cognitiveReframes = "cognitive_reframes"
        case actionPlan = "action_plan"
    }
}

struct ActionItem: Codable {
    let category: String
    let action: String
    let timeline: String
}
