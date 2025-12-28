import Foundation
import AVFoundation

struct Recording {
    let fileName: String
    let createdAt: Date
}

class VoiceRecorder: ObservableObject {
    @Published var isRecording = false
    @Published var recordings: [Recording] = []
    @Published var recordingTime = "00:00"
    
    func startRecording() {
        isRecording = true
    }
    
    func stopRecording() {
        isRecording = false
        recordings.append(Recording(fileName: "Recording \(recordings.count + 1)", createdAt: Date()))
    }
}
