"""Harness and endpoint configurations."""

from __future__ import annotations

import importlib.metadata


class HarnessConfig:
    """Harness operational constants."""

    CLIENT_RETRY_COUNT: int = 3
    PROTOCOL_VERSION: str = "Draft-15"
    RUNTIME_STARTUP_DELAY: float = 2.0
    VERSION: str = importlib.metadata.version("webtransport-interop")


class PyWebTransportConfig:
    """PyWebTransport harness configuration."""

    IMAGE: str = "ghcr.io/wtransport/interop-server:latest"
    PORT: int = 4433


class WTransportInteropServiceConfig:
    """WTransport service harness configuration."""

    BASE_URL: str = "https://interop.wtransport.org"
    STATUS_PATH: str = "/status.json"
