//
//  CICDPipelinePOCTests.swift
//  CICDPipelinePOCTests
//
//  Created by Yann Lamtalaa on 7/14/26.
//

@testable import CICDPipelinePOC
import XCTest

final class CICDPipelinePOCTests: XCTestCase {
    func testPipelineContainsEveryMajorStage() {
        XCTAssertEqual(PipelineStage.pipeline.count, 6)
    }

    func testPipelineStartsWithSourceControl() {
        XCTAssertEqual(
            PipelineStage.pipeline.first?.title,
            "Source Control"
        )
    }

    func testPipelineEndsWithTestFlight() {
        XCTAssertEqual(
            PipelineStage.pipeline.last?.title,
            "TestFlight"
        )
    }

    func testPipelineStageIdentifiersAreUnique() {
        let identifiers = PipelineStage.pipeline.map(\.id)

        XCTAssertEqual(
            identifiers.count,
            Set(identifiers).count
        )
    }
}
