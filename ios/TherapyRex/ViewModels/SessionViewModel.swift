import Foundation

class SessionViewModel: ObservableObject {
    @Published var sessionResult: DeepSessionResult?
    @Published var isLoading = false
    
    private let apiClient = APIClient.shared
    
    func startDeepSession(stress: Int, confidence: Int, motivation: Int, recentResults: String, lifeContext: String) {
        isLoading = true
        Task {
            do {
                let result = try await apiClient.startDeepSession(
                    stress: stress, confidence: confidence, motivation: motivation,
                    recentResults: recentResults, lifeContext: lifeContext
                )
                await MainActor.run {
                    self.sessionResult = result
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                }
            }
        }
    }
}
