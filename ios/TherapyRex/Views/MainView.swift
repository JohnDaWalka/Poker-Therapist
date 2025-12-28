import SwiftUI

struct MainView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            QuickTriageView()
                .tabItem {
                    Label("Triage", systemImage: "cross.case.fill")
                }
                .tag(0)
            
            DeepSessionView()
                .tabItem {
                    Label("Deep Session", systemImage: "brain.head.profile")
                }
                .tag(1)
            
            VoiceRantView()
                .tabItem {
                    Label("Voice", systemImage: "mic.fill")
                }
                .tag(2)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(3)
        }
        .accentColor(.blue)
    }
}

#Preview {
    MainView()
}
