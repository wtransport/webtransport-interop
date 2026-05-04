"""Bidirectional stream and datagram echo scenario."""

from __future__ import annotations

from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.scenarios.base_scenario import BaseScenario
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities


class EchoScenario(BaseScenario):
    """Verifies that the server correctly reflects streams and datagrams."""

    @property
    def default_error_message(self) -> str:
        """Fallback diagnostic message for execution failures."""
        return "validation failed"

    @property
    def harness_requirements(self) -> HarnessCapabilities:
        """Minimum execution privileges required by the scenario."""
        return HarnessCapabilities(controllable=False)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "echo"

    @property
    def protocol_requirements(self) -> ProtocolCapabilities:
        """Minimum protocol features required by the scenario."""
        return ProtocolCapabilities(bidi_stream=True, datagram=True)

    @property
    def success_message(self) -> str:
        """Diagnostic message for execution success."""
        return "execution completed and validation passed"

    async def _execute_workload(self, *, client: BaseEndpoint, server: BaseEndpoint) -> ExecutionResult:
        """Delegate execution to the client endpoint."""
        return await client.run_scenario(name=self.name)
