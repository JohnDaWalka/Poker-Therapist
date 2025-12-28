import SwiftUI

struct BreathingExerciseView: View {
    let exercise: String
    @State private var phase = 0
    @State private var countdown = 4
    @State private var isActive = false
    @Environment(\.dismiss) var dismiss
    
    let phases = ["Breathe IN", "HOLD", "Breathe OUT"]
    let durations = [4, 7, 8]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 40) {
                Text(exercise)
                    .font(.title)
                    .padding()
                
                ZStack {
                    Circle()
                        .stroke(lineWidth: 8)
                        .foregroundColor(.gray.opacity(0.3))
                        .frame(width: 200, height: 200)
                    
                    VStack {
                        Text(phases[phase])
                            .font(.title2)
                        Text("\(countdown)")
                            .font(.system(size: 60))
                    }
                }
                
                Button(action: toggleExercise) {
                    Text(isActive ? "Stop" : "Start")
                        .font(.headline)
                        .padding()
                }
                
                Spacer()
            }
            .padding()
            .navigationTitle("Breathing Exercise")
        }
    }
    
    private func toggleExercise() {
        isActive.toggle()
    }
}
