//
//  DashboardSections.swift
//  CICDPipelinePOC
//

import SwiftUI

struct DashboardBackground: View {
    var body: some View {
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
}

struct DashboardHeroView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            HStack(spacing: 12) {
                Label("iOS DELIVERY LAB", systemImage: "iphone.radiowaves.left.and.right")
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
}

struct PipelineExplorerView: View {
    @State private var selectedStageID = PipelineStage.pipeline.first?.id ?? 1

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

    var body: some View {
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
}

struct BuildDetailsView: View {
    private let metadataColumns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12)
    ]

    private let metadataItems = [
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

    var body: some View {
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
}

struct AutomationRulesView: View {
    var body: some View {
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
}

struct DashboardFooter: View {
    var body: some View {
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
