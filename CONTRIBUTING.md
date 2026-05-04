# Contributing to WebTransport Interop

Thank you for your interest in contributing to WebTransport Interop. This document defines the technical standards for contributors.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Security Vulnerabilities

Please **do not** report security vulnerabilities via public GitHub issues. For reporting instructions and disclosure policies, consult the **[Security Policy](SECURITY.md)**.

## Developer Certificate of Origin (DCO)

To ensure legal compliance, we enforce the **[Developer Certificate of Origin (DCO) 1.1](https://developercertificate.org/)**. By contributing, you certify that you have the right to submit the patch. You **must** sign off every commit by adding a `Signed-off-by` line.

## Extensibility Model

The harness employs a contract-driven registry architecture. Matrix extensions must satisfy the following structural constraints:

- **Endpoints**: Inherit from `BaseEndpoint`. Declare execution configurations in `config.py` and register the adapter in `registry.py`.
- **Scenarios**: Inherit from `BaseScenario`. Expose `HarnessCapabilities` and `ProtocolCapabilities` for capability negotiation and register the scenario in `registry.py`.

## Development Environment

### Prerequisites

- **Docker**: Container runtime management.
- **Git**: Version control.
- **pyenv**: Python version management.

### Setup

1.  **Fork and Clone**:

    ```bash
    git clone https://github.com/<your-username>/webtransport-interop.git
    cd webtransport-interop
    git remote add upstream https://github.com/wtransport/webtransport-interop.git
    ```

2.  **Environment**:

    ```bash
    pyenv install
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Dependencies**:

    ```bash
    pip install -r dev-requirements.txt
    pip install -e .
    python scripts/provision.py
    ```

## Execution

Validate contributions by executing the matrix orchestrator:

```bash
python -m webtransport_interop.main
```

## Coding Standards

All contributions must adhere to the following style requirements:

- **formatting**: `black`
- **imports**: `isort`
- **linting**: `flake8`
- **typing**: `mypy`
- **documentation**: Concise single-line English docstrings.

## Commit & PR Process

1.  **Commit**: Sign-off is mandatory (`git commit -s`). Follow **Conventional Commits**.
2.  **Changelog**: Add a user-facing entry to `CHANGELOG.md` under `Unreleased`.
3.  **Submission**: Open a PR against `main` with technical rationale.

## Release Process

_(Maintainers Only)_

Releases follow **Semantic Versioning**. Update `HarnessConfig.VERSION` and finalize `CHANGELOG.md` before merging to `main`.

## Protocol Compliance

Contributions must adhere to the IETF WebTransport specifications:

- **[WebTransport over HTTP/3](https://datatracker.ietf.org/doc/draft-ietf-webtrans-http3/)**
- **[RFC 9000 (QUIC)](https://www.rfc-editor.org/rfc/rfc9000.txt)**
- **[RFC 9114 (HTTP/3)](https://www.rfc-editor.org/rfc/rfc9114.txt)**
- **[RFC 9297 (HTTP Datagrams)](https://www.rfc-editor.org/rfc/rfc9297.txt)**
