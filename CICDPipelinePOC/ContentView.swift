//
//  ContentView.swift
//  CICDPipelinePOC
//
//  Created by Yann Lamtalaa on 7/14/26.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            ZStack {
                DashboardBackground()

                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 28) {
                        DashboardHeroView()
                        PipelineExplorerView()
                        BuildDetailsView()
                        AutomationRulesView()
                        DashboardFooter()
                    }
                    .padding(.horizontal, 18)
                    .padding(.top, 12)
                    .padding(.bottom, 32)
                }
                .scrollIndicators(.hidden)
            }
            .toolbar(.hidden, for: .navigationBar)
        }
        .tint(.indigo)
    }
}

#Preview {
    ContentView()
}
