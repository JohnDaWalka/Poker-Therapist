import SwiftUI

struct QuickTriageView: View {
    @StateObject private var viewModel = TriageViewModel()
    @State private var situation = ""
    @State private var emotion = "Frustration"
    @State private var intensity: Double = 5
    @State private var bodySensation = ""
    @State private var stillPlaying = false
    @State private var showBreathing = false
    
    let emotions = ["Anger", "Shame", "Fear", "Frustration", "Entitlement", "Boredom"]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Current Situation")) {
                    TextEditor(text: $situation)
                        .frame(height: 100)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                        )
                }
                
                Section(header: Text("Emotional State")) {
                    Picker("Emotion", selection: $emotion) {
                        ForEach(emotions, id: \.self) { emotion in
                            Text(emotion).tag(emotion)
                        }
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Intensity: \(Int(intensity))/10")
                        Slider(value: $intensity, in: 1...10, step: 1)
                            .accentColor(intensityColor)
                    }
                    
                    TextField("Physical sensations (optional)", text: $bodySensation)
                }
                
                Section {
                    Toggle("Still playing?", isOn: $stillPlaying)
                        .tint(.red)
                }
                
                Section {
                    Button(action: analyzeTriage) {
                        HStack {
                            Spacer()
                            if viewModel.isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle())
                            } else {
                                Text("Analyze")
                                    .font(.headline)
                            }
                            Spacer()
                        }
                    }
                    .disabled(situation.isEmpty || viewModel.isLoading)
                }
                
                if let result = viewModel.triageResult {
                    Section(header: Text("Results")) {
                        HStack {
                            Text("Severity:")
                            Spacer()
                            Text("\(result.severity)/10")
                                .font(.headline)
                                .foregroundColor(severityColor(result.severity))
                        }
                        
                        if result.shouldStop {
                            Text("🛑 STOP PLAYING NOW")
                                .font(.headline)
                                .foregroundColor(.red)
                        }
                        
                        if !result.aiGuidance.isEmpty {
                            Text(result.aiGuidance)
                                .font(.body)
                        }
                        
                        Button("Practice Breathing") {
                            showBreathing = true
                        }
                    }
                }
            }
            .navigationTitle("Quick Triage")
            .sheet(isPresented: $showBreathing) {
                BreathingExerciseView(exercise: viewModel.triageResult?.breathingExercise ?? "4-7-8")
            }
        }
    }
    
    private var intensityColor: Color {
        switch intensity {
        case 1..<4: return .green
        case 4..<7: return .orange
        case 7..<9: return .red
        default: return .purple
        }
    }
    
    private func severityColor(_ severity: Int) -> Color {
        switch severity {
        case 0..<4: return .green
        case 4..<7: return .orange
        case 7..<9: return .red
        default: return .purple
        }
    }
    
    private func analyzeTriage() {
        viewModel.analyzeTriage(
            situation: situation,
            emotion: emotion,
            intensity: Int(intensity),
            bodySensation: bodySensation,
            stillPlaying: stillPlaying
        )
    }
}

#Preview {
    QuickTriageView()
}
