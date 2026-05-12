# Changelog

All notable changes to WebTransport Interop will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for future release

_(No planned changes for the next release yet.)_

## [0.2.0] - 2026-05-12

### Added

- **Endpoint Registry**: Integrated Mozilla Firefox as a client endpoint, utilizing Selenium WebDriver to execute against stable browser binaries.
- **Automated Provisioning**: Added the `selenium` package to project dependencies to support dynamic environment provisioning for WebDriver-based endpoints.

### Changed

- **Endpoint Registry**: Refactored Chrome and Edge execution handlers to catch JavaScript promise rejections natively, enabling direct propagation of protocol-level exceptions.
- **Visualization Layer**: Integrated Firefox identity mappings into the frontend registry and condensed vertical spacing metrics to maintain optimal information density.

## [0.1.1] - 2026-05-10

### Changed

- **CI Infrastructure**: Shifted automated matrix execution schedules to off-peak hours to mitigate upstream resource contention.
- **Visualization Layer**: Decoupled harness version metadata into an isolated DOM element and enforced structural width constraints to optimize high-resolution layout.
- **Visualization Layer**: Condensed footer navigation nomenclature and normalized network exception status strings to strict lowercase.

## [0.1.0] - 2026-05-04

This is the initial release of WebTransport Interop. It establishes a deterministic execution framework for validating protocol conformance across WebTransport implementations. The system employs a contract-driven registry architecture to orchestrate star-topology interoperability tests against controlled baselines.

### Added

- **Contract-Driven Architecture**: Introduced `BaseEndpoint` and `BaseScenario` abstractions utilizing `HarnessCapabilities` and `ProtocolCapabilities` for strict capability negotiation and execution isolation.
- **Execution Orchestrator**: Implemented `MatrixRunner` to enforce star-topology execution against baseline implementations (`pywebtransport` for clients, `wtransport_interop_service` for servers).
- **Runtime Engine**: Implemented `TestRuntime` for deterministic orchestration of endpoint lifecycles, incorporating automated startup delays and two-phase teardown mechanisms.
- **Endpoint Registry**:
  - Integrated browser-based client endpoints (Google Chrome, Microsoft Edge) via Playwright.
  - Integrated native library endpoints (`pywebtransport` client and server).
  - Added a remote endpoint proxy (`wtransport_interop_service`) for fetching status from the public interoperability service.
- **Scenario Registry**: Established the initial conformance matrix comprising `echo` (bidirectional stream and datagram reflection) and `devious_baton` (complex protocol state machine validation).
- **Semantic Reporting**: Implemented a reporting layer that serializes execution outcomes into a versioned, timestamped `matrix_result.json` artifact.
- **Visualization Layer**: Introduced an HTML/JS/CSS frontend to parse and render `matrix_result.json` into an interactive interoperability status matrix.
- **Automated Provisioning**: Added the `provision.py` utility for dynamic resolution and installation of stable browser binaries based on the active registry.
- **CI/CD Infrastructure**:
  - Configured GitHub Actions for automated matrix execution and deployment of the visualization layer to GitHub Pages.
  - Configured GitLab CI for multi-stage static analysis (linting, typing) and repository synchronization.
- **Engineering Standards**: Established full compliance with Python 3.12+ strict typing, Conventional Commits, and Developer Certificate of Origin (DCO) requirements.

[Unreleased]: https://github.com/wtransport/webtransport-interop/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/wtransport/webtransport-interop/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/wtransport/webtransport-interop/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/wtransport/webtransport-interop/releases/tag/v0.1.0
