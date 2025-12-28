import Foundation
import Combine

class TriageViewModel: ObservableObject {
    @Published var triageResult: TriageResult?
    @Published var isLoading = false
    @Published var error: String?
    
    private let apiClient = APIClient.shared
    
    func analyzeTriage(situation: String, emotion: String, intensity: Int, bodySensation: String, stillPlaying: Bool) {
        isLoading = true
        error = nil
        
        Task {
            do {
                let result = try await apiClient.analyzeTriage(
                    situation: situation,
                    emotion: emotion,
                    intensity: intensity,
                    bodySensation: bodySensation,
                    stillPlaying: stillPlaying
                )
                await MainActor.run {
                    self.triageResult = result
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.error = error.localizedDescription
                    self.isLoading = false
                }
            }
        }
    }
}
