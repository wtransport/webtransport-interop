"""PyWebTransport server endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import docker
from pywebtransport import __version__ as LIB_VERSION

from webtransport_interop.config import PyWebTransportConfig
from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities

if TYPE_CHECKING:
    from docker.models.containers import Container


class PyWebTransportServer(BaseEndpoint):
    """Server adapter for PyWebTransport."""

    def __init__(self) -> None:
        """Initialize docker client."""
        self._container: Container | None = None
        self._docker: Any = docker.from_env()

    @property
    def harness_capabilities(self) -> HarnessCapabilities:
        """Endpoint harness execution capabilities."""
        return HarnessCapabilities(controllable=True)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "pywebtransport"

    @property
    def protocol_capabilities(self) -> ProtocolCapabilities:
        """Endpoint protocol feature capabilities."""
        return ProtocolCapabilities(bidi_stream=True, capsule=True, datagram=True, stream_reset=True, uni_stream=True)

    @property
    def version(self) -> str:
        """Implementation version identifier."""
        return LIB_VERSION

    def get_logs(self) -> str:
        """Retrieve execution diagnostic logs."""
        return self._container.logs().decode(encoding="utf-8") if self._container else ""

    async def run_scenario(self, *, name: str) -> ExecutionResult:
        """Execute scenario workload."""
        return ExecutionResult(completed=True)

    async def start(self) -> None:
        """Initialize endpoint runtime."""
        self._docker.images.pull(PyWebTransportConfig.IMAGE)
        self._container = self._docker.containers.run(
            image=PyWebTransportConfig.IMAGE,
            detach=True,
            ports={f"{PyWebTransportConfig.PORT}/udp": PyWebTransportConfig.PORT},
        )

    async def stop(self) -> None:
        """Terminate endpoint resources."""
        if self._container:
            self._container.stop()
            self._container.remove()
            self._container = None
