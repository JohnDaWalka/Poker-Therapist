import SwiftUI
import AVFoundation

struct VoiceRantView: View {
    @StateObject private var recorder = VoiceRecorder()
    @State private var showingAnalysis = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                Spacer()
                
                Text(recorder.isRecording ? "Recording..." : "Ready to record")
                    .font(.title2)
                    .foregroundColor(recorder.isRecording ? .red : .primary)
                
                if recorder.isRecording {
                    Text(recorder.recordingTime)
                        .font(.system(.largeTitle, design: .monospaced))
                        .foregroundColor(.red)
                }
                
                Button(action: toggleRecording) {
                    Circle()
                        .fill(recorder.isRecording ? Color.red : Color.blue)
                        .frame(width: 100, height: 100)
                        .overlay(
                            Image(systemName: recorder.isRecording ? "stop.fill" : "mic.fill")
                                .font(.system(size: 40))
                                .foregroundColor(.white)
                        )
                }
                
                if !recorder.recordings.isEmpty {
                    List {
                        ForEach(recorder.recordings, id: \.createdAt) { recording in
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(recording.fileName)
                                        .font(.headline)
                                    Text(formatDate(recording.createdAt))
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                                Spacer()
                                Button("Analyze") {
                                    // TODO: Implement analysis
                                    showingAnalysis = true
                                }
                                .buttonStyle(.bordered)
                            }
                        }
                    }
                }
                
                Spacer()
            }
            .navigationTitle("Voice Rant")
            .padding()
            .alert("Analysis", isPresented: $showingAnalysis) {
                Button("OK", role: .cancel) { }
            } message: {
                Text("Voice analysis coming soon!")
            }
        }
    }
    
    private func toggleRecording() {
        if recorder.isRecording {
            recorder.stopRecording()
        } else {
            recorder.startRecording()
        }
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

#Preview {
    VoiceRantView()
}
