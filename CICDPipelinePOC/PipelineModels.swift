//
//  PipelineModels.swift
//  CICDPipelinePOC
//

import Foundation

struct PipelineStage: Identifiable, Equatable {
    let id: Int
    let title: String
    let detail: String
    let systemImage: String

    static let pipeline: [PipelineStage] = [
        PipelineStage(
            id: 1,
            title: "Source Control",
            detail: "A developer pushes code or opens a pull request.",
            systemImage: "arrow.triangle.branch"
        ),
        PipelineStage(
            id: 2,
            title: "GitHub Actions",
            detail: "GitHub creates a clean macOS build runner.",
            systemImage: "play.circle.fill"
        ),
        PipelineStage(
            id: 3,
            title: "Automated Tests",
            detail: "Fastlane builds the app and runs the XCTest suite.",
            systemImage: "checkmark.seal.fill"
        ),
        PipelineStage(
            id: 4,
            title: "Build and Archive",
            detail: "Fastlane creates a Release archive and IPA.",
            systemImage: "shippingbox.fill"
        ),
        PipelineStage(
            id: 5,
            title: "Code Signing",
            detail: "GitHub installs temporary Apple signing credentials.",
            systemImage: "signature"
        ),
        PipelineStage(
            id: 6,
            title: "TestFlight",
            detail: "Fastlane uploads the signed build to App Store Connect.",
            systemImage: "paperplane.fill"
        )
    ]
}

enum BuildMetadata {
    static let version = Bundle.main.object(
        forInfoDictionaryKey: "CFBundleShortVersionString"
    ) as? String ?? "Unknown"

    static let build = Bundle.main.object(
        forInfoDictionaryKey: "CFBundleVersion"
    ) as? String ?? "Unknown"

    static let commit = infoValue(key: "CI_COMMIT_SHA", fallback: "Local build")
    static let branch = infoValue(key: "CI_BRANCH", fallback: "Local")
    static let workflow = infoValue(key: "CI_WORKFLOW", fallback: "Xcode")
    static let runNumber = infoValue(key: "CI_RUN_NUMBER", fallback: "Local")
    static let buildDate = infoValue(key: "CI_BUILD_DATE", fallback: "Not supplied")
    static let environment = infoValue(
        key: "CI_ENVIRONMENT",
        fallback: "Local Development"
    )

    static let formattedBuildDate = formattedDate(from: buildDate)
    static let isContinuousIntegration = environment != "Local Development"

    private static func infoValue(key: String, fallback: String) -> String {
        guard let value = Bundle.main.object(forInfoDictionaryKey: key) as? String,
              !value.isEmpty,
              !value.contains("$(") else {
            return fallback
        }
        return value
    }

    private static func formattedDate(from value: String) -> String {
        guard let date = ISO8601DateFormatter().date(from: value) else {
            return value
        }

        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "America/New_York")
        formatter.dateFormat = "MMM d, yyyy · h:mm a zzz"
        return formatter.string(from: date)
    }
}

struct MetadataItem: Identifiable {
    let title: String
    let value: String
    let systemImage: String

    var id: String {
        title
    }
}
