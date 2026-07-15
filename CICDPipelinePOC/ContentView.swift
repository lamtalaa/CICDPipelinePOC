//
//  ContentView.swift
//  CICDPipelinePOC
//
//  Created by Yann Lamtalaa on 7/14/26.
//

import Foundation
import SwiftUI

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

struct ContentView: View {
    @State private var selectedStageID = PipelineStage.pipeline.first?.id ?? 1

    private let metadataColumns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12)
    ]

    private var selectedStage: PipelineStage {
        PipelineStage.pipeline.first { stage in
            stage.id == selectedStageID
        } ?? PipelineStage(
            id: 1,
            title: "Source Control",
            detail: "A developer pushes code or opens a pull request.",
            systemImage: "arrow.triangle.branch"
        )
    }

    private var metadataItems: [MetadataItem] {
        [
            MetadataItem(
                title: "Environment",
                value: BuildMetadata.environment,
                systemImage: "server.rack"
            ),
            MetadataItem(
                title: "Version",
                value: BuildMetadata.version,
                systemImage: "tag.fill"
            ),
            MetadataItem(
                title: "Build",
                value: BuildMetadata.build,
                systemImage: "hammer.fill"
            ),
            MetadataItem(
                title: "Branch",
                value: BuildMetadata.branch,
                systemImage: "arrow.triangle.branch"
            ),
            MetadataItem(
                title: "Commit",
                value: BuildMetadata.commit,
                systemImage: "number"
            ),
            MetadataItem(
                title: "Workflow",
                value: BuildMetadata.workflow,
                systemImage: "point.3.connected.trianglepath.dotted"
            ),
            MetadataItem(
                title: "Run",
                value: BuildMetadata.runNumber,
                systemImage: "play.rectangle.fill"
            ),
            MetadataItem(
                title: "Built",
                value: BuildMetadata.formattedBuildDate,
                systemImage: "clock.fill"
            )
        ]
    }

    var body: some View {
        NavigationStack {
            ZStack {
                dashboardBackground

                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 28) {
                        heroSection
                        deliveryPipelineSection
                        buildDetailsSection
                        automationSection
                        footer
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

    private var dashboardBackground: some View {
        ZStack {
            Color(.systemGroupedBackground)
                .ignoresSafeArea()

            LinearGradient(
                colors: [
                    Color.indigo.opacity(0.18),
                    Color.blue.opacity(0.08),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .center
            )
            .ignoresSafeArea()

            Circle()
                .fill(Color.cyan.opacity(0.10))
                .frame(width: 260, height: 260)
                .blur(radius: 40)
                .offset(x: 150, y: -310)
        }
        .accessibilityHidden(true)
    }

    private var heroSection: some View {
        VStack(alignment: .leading, spacing: 20) {
            HStack(spacing: 12) {
                Label("iOS DELIVERY LAB", systemImage: "iphone.gen3.radiowaves.left.and.right")
                    .font(.caption.weight(.bold))
                    .tracking(0.8)

                Spacer()

                statusPill
            }

            VStack(alignment: .leading, spacing: 10) {
                Text("Ship with confidence.")
                    .font(.system(.largeTitle, design: .rounded, weight: .bold))

                Text(
                    "A production-style iOS delivery pipeline powered by "
                    + "GitHub Actions, Fastlane, XCTest, and TestFlight."
                )
                .font(.body)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
            }

            LazyVGrid(
                columns: [GridItem(.adaptive(minimum: 92), spacing: 10)],
                spacing: 10
            ) {
                HeroMetric(
                    value: "6",
                    label: "Automated stages",
                    systemImage: "point.3.connected.trianglepath.dotted"
                )
                HeroMetric(
                    value: "v\(BuildMetadata.version)",
                    label: "App version",
                    systemImage: "shippingbox.fill"
                )
                HeroMetric(
                    value: "#\(BuildMetadata.build)",
                    label: "Build number",
                    systemImage: "number.circle.fill"
                )
            }
        }
        .padding(22)
        .background(
            LinearGradient(
                colors: [
                    Color.indigo.opacity(0.22),
                    Color.blue.opacity(0.08)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ),
            in: RoundedRectangle(cornerRadius: 30, style: .continuous)
        )
        .overlay {
            RoundedRectangle(cornerRadius: 30, style: .continuous)
                .stroke(Color.primary.opacity(0.08), lineWidth: 1)
        }
        .shadow(color: Color.black.opacity(0.08), radius: 24, y: 12)
    }

    private var statusPill: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(BuildMetadata.isContinuousIntegration ? Color.green : Color.orange)
                .frame(width: 8, height: 8)

            Text(BuildMetadata.isContinuousIntegration ? "CI VERIFIED" : "PREVIEW")
                .font(.caption2.weight(.bold))
                .tracking(0.6)
        }
        .padding(.horizontal, 11)
        .padding(.vertical, 7)
        .background(.thinMaterial, in: Capsule())
        .accessibilityElement(children: .combine)
    }

    private var deliveryPipelineSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(
                title: "Delivery pipeline",
                subtitle: "Tap any stage to explore how the build moves from code to QA."
            )

            ScrollView(.horizontal) {
                HStack(spacing: 12) {
                    ForEach(PipelineStage.pipeline) { stage in
                        StageButton(
                            stage: stage,
                            isSelected: stage.id == selectedStageID
                        ) {
                            withAnimation(.snappy(duration: 0.28)) {
                                selectedStageID = stage.id
                            }
                        }
                    }
                }
                .padding(.vertical, 2)
            }
            .scrollIndicators(.hidden)

            selectedStageCard
        }
    }

    private var selectedStageCard: some View {
        HStack(alignment: .top, spacing: 16) {
            Image(systemName: selectedStage.systemImage)
                .font(.system(size: 24, weight: .semibold))
                .foregroundStyle(.white)
                .frame(width: 52, height: 52)
                .background(
                    LinearGradient(
                        colors: [.indigo, .blue],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    in: RoundedRectangle(cornerRadius: 16, style: .continuous)
                )

            VStack(alignment: .leading, spacing: 8) {
                Text("STAGE \(selectedStage.id) OF \(PipelineStage.pipeline.count)")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(.secondary)
                    .tracking(0.8)

                Text(selectedStage.title)
                    .font(.title3.weight(.bold))

                Text(selectedStage.detail)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                Label("Fully automated", systemImage: "bolt.fill")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.green)
                    .padding(.top, 2)
            }

            Spacer(minLength: 0)
        }
        .padding(18)
        .dashboardCard()
        .contentTransition(.opacity)
        .id(selectedStage.id)
        .transition(.opacity.combined(with: .scale(scale: 0.98)))
    }

    private var buildDetailsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(
                title: "Build intelligence",
                subtitle: "Traceable metadata embedded directly into this application build."
            )

            LazyVGrid(columns: metadataColumns, spacing: 12) {
                ForEach(metadataItems) { item in
                    MetadataTile(item: item)
                }
            }
        }
    }

    private var automationSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(
                title: "Automation rules",
                subtitle: "Every trigger follows a predictable, secure path."
            )

            VStack(spacing: 12) {
                AutomationRuleCard(
                    title: "Pull request validation",
                    detail: "SwiftLint, unit tests, and coverage protect the main branch.",
                    systemImage: "checkmark.shield.fill",
                    badge: "QUALITY GATE"
                )

                AutomationRuleCard(
                    title: "Main branch delivery",
                    detail: "A passing build is signed, archived, and uploaded to QA TestFlight.",
                    systemImage: "paperplane.circle.fill",
                    badge: "CONTINUOUS DELIVERY"
                )

                AutomationRuleCard(
                    title: "Secure by design",
                    detail: "Signing assets and API credentials stay protected in GitHub secrets.",
                    systemImage: "lock.shield.fill",
                    badge: "EPHEMERAL SECRETS"
                )
            }
        }
    }

    private var footer: some View {
        VStack(spacing: 8) {
            Image(systemName: "arrow.triangle.2.circlepath.circle.fill")
                .font(.title2)
                .foregroundStyle(.indigo)

            Text("Built by GitHub Actions + Fastlane")
                .font(.footnote.weight(.semibold))

            Text("From commit to TestFlight, automatically.")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 4)
    }
}

private struct MetadataItem: Identifiable {
    let title: String
    let value: String
    let systemImage: String

    var id: String {
        title
    }
}

private struct HeroMetric: View {
    let value: String
    let label: String
    let systemImage: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: systemImage)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.indigo)

            Text(value)
                .font(.title3.weight(.bold))
                .lineLimit(1)
                .minimumScaleFactor(0.75)

            Text(label)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity, minHeight: 92, alignment: .leading)
        .padding(13)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }
}

private struct StageButton: View {
    let stage: PipelineStage
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Image(systemName: stage.systemImage)
                        .font(.headline)
                    Spacer()
                    Text(String(format: "%02d", stage.id))
                        .font(.caption2.monospacedDigit().weight(.bold))
                        .foregroundStyle(.secondary)
                }

                Text(stage.title)
                    .font(.subheadline.weight(.semibold))
                    .multilineTextAlignment(.leading)
                    .lineLimit(2)
            }
            .foregroundStyle(isSelected ? Color.white : Color.primary)
            .frame(width: 132, height: 92, alignment: .leading)
            .padding(14)
            .background(stageBackground)
            .overlay {
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(
                        isSelected ? Color.clear : Color.primary.opacity(0.08),
                        lineWidth: 1
                    )
            }
            .shadow(
                color: isSelected ? Color.indigo.opacity(0.22) : Color.clear,
                radius: 16,
                y: 8
            )
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Stage \(stage.id), \(stage.title)")
        .accessibilityAddTraits(isSelected ? .isSelected : [])
    }

    @ViewBuilder
    private var stageBackground: some View {
        if isSelected {
            LinearGradient(
                colors: [.indigo, .blue],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        } else {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(.background)
        }
    }
}

private struct MetadataTile: View {
    let item: MetadataItem

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Image(systemName: item.systemImage)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.indigo)
                .frame(width: 34, height: 34)
                .background(Color.indigo.opacity(0.10), in: RoundedRectangle(cornerRadius: 10))

            VStack(alignment: .leading, spacing: 4) {
                Text(item.title.uppercased())
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(.secondary)
                    .tracking(0.6)

                Text(item.value)
                    .font(.subheadline.weight(.semibold))
                    .lineLimit(2)
                    .minimumScaleFactor(0.78)
                    .textSelection(.enabled)
            }
        }
        .frame(maxWidth: .infinity, minHeight: 120, alignment: .leading)
        .padding(16)
        .dashboardCard()
    }
}

private struct AutomationRuleCard: View {
    let title: String
    let detail: String
    let systemImage: String
    let badge: String

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: systemImage)
                .font(.title3.weight(.semibold))
                .foregroundStyle(.indigo)
                .frame(width: 44, height: 44)
                .background(Color.indigo.opacity(0.10), in: RoundedRectangle(cornerRadius: 14))

            VStack(alignment: .leading, spacing: 6) {
                Text(badge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(.indigo)
                    .tracking(0.6)

                Text(title)
                    .font(.headline)

                Text(detail)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 0)
        }
        .padding(16)
        .dashboardCard()
    }
}

private struct SectionHeader: View {
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(title)
                .font(.title2.weight(.bold))

            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

private extension View {
    func dashboardCard() -> some View {
        background(
            Color(.secondarySystemGroupedBackground),
            in: RoundedRectangle(cornerRadius: 22, style: .continuous)
        )
        .overlay {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(Color.primary.opacity(0.07), lineWidth: 1)
        }
        .shadow(color: Color.black.opacity(0.04), radius: 12, y: 6)
    }
}

#Preview {
    ContentView()
}
