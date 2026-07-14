//
//  ContentView.swift
//  CICDPipelinePOC
//
//  Created by Yann Lamtalaa on 7/14/26.
//

import SwiftUI

struct PipelineStage: Identifiable, Equatable {
    let id: Int
    let title: String
    let detail: String
    let systemImage: String

    static let pipeline: [PipelineStage] = [
        PipelineStage(id: 1, title: "Source Control", detail: "A developer pushes code or opens a pull request.", systemImage: "arrow.triangle.branch"),
        PipelineStage(id: 2, title: "GitHub Actions", detail: "GitHub creates a clean macOS build runner.", systemImage: "play.circle"),
        PipelineStage(id: 3, title: "Automated Tests", detail: "Fastlane builds the app and runs the XCTest suite.", systemImage: "checkmark.seal"),
        PipelineStage(id: 4, title: "Build and Archive", detail: "Fastlane creates a Release archive and IPA.", systemImage: "shippingbox"),
        PipelineStage(id: 5, title: "Code Signing", detail: "GitHub installs temporary Apple signing credentials.", systemImage: "signature"),
        PipelineStage(id: 6, title: "TestFlight", detail: "Fastlane uploads the signed build to App Store Connect.", systemImage: "paperplane")
    ]
}

enum BuildMetadata {
    static let version = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "Unknown"
    static let build = Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? "Unknown"
    static let commit = infoValue(key: "CI_COMMIT_SHA", fallback: "Local build")
    static let branch = infoValue(key: "CI_BRANCH", fallback: "Local")
    static let workflow = infoValue(key: "CI_WORKFLOW", fallback: "Xcode")
    static let runNumber = infoValue(key: "CI_RUN_NUMBER", fallback: "Local")
    static let buildDate = infoValue(key: "CI_BUILD_DATE", fallback: "Not supplied")
    static let environment = infoValue(key: "CI_ENVIRONMENT", fallback: "Local Development")

    private static func infoValue(key: String, fallback: String) -> String {
        guard let value = Bundle.main.object(forInfoDictionaryKey: key) as? String,
              !value.isEmpty,
              !value.contains("$(") else {
            return fallback
        }
        return value
    }
}

struct ContentView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    header
                    pipelineFlow
                    buildInformation
                    triggerInformation
                }
                .padding()
            }
            .navigationTitle("CI/CD POC")
        }
    }

    private var header: some View {
        VStack(spacing: 12) {
            Image(systemName: "arrow.triangle.2.circlepath.circle.fill")
                .font(.system(size: 58))
            Text("GitHub Actions + Fastlane")
                .font(.title2.bold())
            Text("Automated through GitHub Actions and Fastlane")
                .font(.subheadline)
            Text("An end-to-end iOS pipeline that tests, signs, builds, and uploads the application to TestFlight.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical)
    }

    private var pipelineFlow: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 0) {
                ForEach(PipelineStage.pipeline) { stage in
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: stage.systemImage)
                            .frame(width: 28)
                            .font(.title3)
                        VStack(alignment: .leading, spacing: 4) {
                            Text("\(stage.id). \(stage.title)")
                                .font(.headline)
                            Text(stage.detail)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                    }
                    .padding(.vertical, 10)
                    if stage.id != PipelineStage.pipeline.last?.id {
                        Divider()
                    }
                }
            }
        } label: {
            Label("Pipeline Flow", systemImage: "point.3.connected.trianglepath.dotted")
        }
    }

    private var buildInformation: some View {
        GroupBox {
            VStack(spacing: 0) {
                MetadataRow(title: "Environment", value: BuildMetadata.environment)
                Divider()
                MetadataRow(title: "Version", value: BuildMetadata.version)
                Divider()
                MetadataRow(title: "Build", value: BuildMetadata.build)
                Divider()
                MetadataRow(title: "Branch", value: BuildMetadata.branch)
                Divider()
                MetadataRow(title: "Commit", value: BuildMetadata.commit)
                Divider()
                MetadataRow(title: "Workflow", value: BuildMetadata.workflow)
                Divider()
                MetadataRow(title: "Run", value: BuildMetadata.runNumber)
                Divider()
                MetadataRow(title: "Built", value: BuildMetadata.buildDate)
            }
        } label: {
            Label("This Build", systemImage: "info.circle")
        }
    }

    private var triggerInformation: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 12) {
                Label("Pull request: build and unit tests", systemImage: "checkmark.circle")
                Label("Push to main: test, sign, build, and upload", systemImage: "paperplane.circle")
                Label("Secrets remain in GitHub Actions", systemImage: "lock.shield")
            }
            .font(.subheadline)
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Automation Rules", systemImage: "gearshape.2")
        }
    }
}

private struct MetadataRow: View {
    let title: String
    let value: String

    var body: some View {
        HStack(alignment: .firstTextBaseline) {
            Text(title)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .fontWeight(.medium)
                .multilineTextAlignment(.trailing)
                .textSelection(.enabled)
        }
        .padding(.vertical, 9)
    }
}

#Preview {
    ContentView()
}
