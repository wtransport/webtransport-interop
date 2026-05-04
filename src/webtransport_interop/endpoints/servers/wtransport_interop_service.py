"""WTransport interop service server endpoint."""

from __future__ import annotations

import asyncio
import json
import urllib.request

from webtransport_interop.config import WTransportInteropServiceConfig
from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities


class WTransportInteropServiceServer(BaseEndpoint):
    """Server adapter for WTransport interop service."""

    def __init__(self) -> None:
        """Initialize remote endpoint state."""
        self._version: str = "unknown"

    @property
    def harness_capabilities(self) -> HarnessCapabilities:
        """Endpoint harness execution capabilities."""
        return HarnessCapabilities(controllable=True)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "wtransport_interop_service"

    @property
    def protocol_capabilities(self) -> ProtocolCapabilities:
        """Endpoint protocol feature capabilities."""
        return ProtocolCapabilities(bidi_stream=True, capsule=True, datagram=True, stream_reset=True, uni_stream=True)

    @property
    def version(self) -> str:
        """Implementation version identifier."""
        return self._version

    def get_logs(self) -> str:
        """Retrieve execution diagnostic logs."""
        return "Remote instance: logs unavailable."

    async def run_scenario(self, *, name: str) -> ExecutionResult:
        """Execute scenario workload."""
        return ExecutionResult(completed=True)

    async def start(self) -> None:
        """Initialize endpoint runtime."""
        try:
            self._version = await asyncio.to_thread(self._fetch_version)
        except Exception:
            self._version = "unknown"

    async def stop(self) -> None:
        """Terminate endpoint resources."""
        pass

    def _fetch_version(self) -> str:
        """Synchronously fetch remote version status."""
        url = f"{WTransportInteropServiceConfig.BASE_URL}{WTransportInteropServiceConfig.STATUS_PATH}"
        req = urllib.request.Request(url=url, method="GET")
        with urllib.request.urlopen(url=req, timeout=5.0) as response:
            return str(json.loads(s=response.read().decode(encoding="utf-8")).get("version", "unknown"))
