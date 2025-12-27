import SwiftUI

struct DeepSessionView: View {
    @StateObject private var viewModel = SessionViewModel()
    @State private var stress: Double = 5
    @State private var confidence: Double = 5
    @State private var motivation: Double = 5
    @State private var recentResults = ""
    @State private var lifeContext = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Emotional State")) {
                    VStack(alignment: .leading) {
                        Text("Stress: \(Int(stress))/10")
                        Slider(value: $stress, in: 1...10, step: 1)
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Confidence: \(Int(confidence))/10")
                        Slider(value: $confidence, in: 1...10, step: 1)
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Motivation: \(Int(motivation))/10")
                        Slider(value: $motivation, in: 1...10, step: 1)
                    }
                }
                
                Section(header: Text("Context")) {
                    TextEditor(text: $recentResults)
                        .frame(height: 100)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                        )
                    
                    TextEditor(text: $lifeContext)
                        .frame(height: 80)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                        )
                }
                
                Section {
                    Button(action: startSession) {
                        HStack {
                            Spacer()
                            if viewModel.isLoading {
                                ProgressView()
                            } else {
                                Text("Start Deep Session")
                                    .font(.headline)
                            }
                            Spacer()
                        }
                    }
                    .disabled(recentResults.isEmpty || viewModel.isLoading)
                }
                
                if let result = viewModel.sessionResult {
                    Section(header: Text("Session Summary")) {
                        Text(result.sessionSummary)
                            .font(.body)
                    }
                    
                    if !result.cognitiveReframes.isEmpty {
                        Section(header: Text("Cognitive Reframes")) {
                            ForEach(result.cognitiveReframes, id: \.self) { reframe in
                                Text("• \(reframe)")
                            }
                        }
                    }
                }
            }
            .navigationTitle("Deep Session")
        }
    }
    
    private func startSession() {
        viewModel.startDeepSession(
            stress: Int(stress),
            confidence: Int(confidence),
            motivation: Int(motivation),
            recentResults: recentResults,
            lifeContext: lifeContext
        )
    }
}

#Preview {
    DeepSessionView()
}
