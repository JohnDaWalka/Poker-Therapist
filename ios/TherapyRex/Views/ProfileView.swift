import SwiftUI

struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()
    
    var body: some View {
        NavigationView {
            List {
                Section(header: Text("A-Game Characteristics")) {
                    ForEach(viewModel.aGameCharacteristics, id: \.key) { item in
                        HStack {
                            Text(item.key)
                            Spacer()
                            Image(systemName: item.value ? "checkmark.circle.fill" : "circle")
                                .foregroundColor(item.value ? .green : .gray)
                        }
                    }
                }
                
                Section(header: Text("Red Flags")) {
                    ForEach(viewModel.redFlags, id: \.self) { flag in
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.yellow)
                            Text(flag)
                        }
                    }
                }
                
                Section(header: Text("Recurring Patterns")) {
                    ForEach(viewModel.recurringPatterns, id: \.self) { pattern in
                        Text(pattern)
                    }
                }
                
                Section(header: Text("Mental Game Stats")) {
                    HStack {
                        Text("Tilt Frequency")
                        Spacer()
                        Text("2.3/week")
                            .foregroundColor(.gray)
                    }
                    HStack {
                        Text("Average Severity")
                        Spacer()
                        Text("5.2/10")
                            .foregroundColor(.orange)
                    }
                    HStack {
                        Text("A-Game %")
                        Spacer()
                        Text("68%")
                            .foregroundColor(.green)
                    }
                }
            }
            .navigationTitle("Profile")
            .onAppear {
                viewModel.loadProfile()
            }
        }
    }
}

#Preview {
    ProfileView()
}
