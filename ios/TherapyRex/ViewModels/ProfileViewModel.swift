import Foundation

class ProfileViewModel: ObservableObject {
    @Published var aGameCharacteristics: [(key: String, value: Bool)] = []
    @Published var redFlags: [String] = []
    @Published var recurringPatterns: [String] = []
    
    func loadProfile() {
        aGameCharacteristics = [
            ("Patient", true),
            ("Focused", true),
            ("Confident", true)
        ]
        redFlags = ["Anger", "Revenge thoughts", "Chasing losses"]
        recurringPatterns = ["Variance tilt", "Mistake tilt"]
    }
}
