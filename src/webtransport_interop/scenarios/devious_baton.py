"""Devious Baton protocol state machine validation scenario."""

from __future__ import annotations

from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.scenarios.base_scenario import BaseScenario
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities


class DeviousBatonScenario(BaseScenario):
    """Exercises the Devious Baton protocol to verify complex state transitions."""

    @property
    def default_error_message(self) -> str:
        """Fallback diagnostic message for execution failures."""
        return "validation failed"

    @property
    def harness_requirements(self) -> HarnessCapabilities:
        """Minimum execution privileges required by the scenario."""
        return HarnessCapabilities(controllable=True)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "devious_baton"

    @property
    def protocol_requirements(self) -> ProtocolCapabilities:
        """Minimum protocol features required by the scenario."""
        return ProtocolCapabilities(bidi_stream=True, capsule=True, datagram=True, stream_reset=True, uni_stream=True)

    @property
    def success_message(self) -> str:
        """Diagnostic message for execution success."""
        return "execution completed and validation passed"

    async def _execute_workload(self, *, client: BaseEndpoint, server: BaseEndpoint) -> ExecutionResult:
        """Delegate execution to the client endpoint."""
        return await client.run_scenario(name=self.name)
