"""Harness blueprint for protocol execution scenarios."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import fields

from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.types import (
    ExecutionResult,
    HarnessCapabilities,
    ProtocolCapabilities,
    ScenarioResult,
    Verdict,
)


class BaseScenario(ABC):
    """Blueprint for protocol interoperability test cases."""

    @property
    @abstractmethod
    def default_error_message(self) -> str:
        """Fallback diagnostic message for execution failures."""
        ...

    @property
    @abstractmethod
    def harness_requirements(self) -> HarnessCapabilities:
        """Minimum execution privileges required by the scenario."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Harness registration identity."""
        ...

    @property
    @abstractmethod
    def protocol_requirements(self) -> ProtocolCapabilities:
        """Minimum protocol features required by the scenario."""
        ...

    @property
    @abstractmethod
    def success_message(self) -> str:
        """Diagnostic message for execution success."""
        ...

    def check_capabilities(self, *, client: BaseEndpoint, server: BaseEndpoint) -> bool:
        """Evaluate if endpoints satisfy protocol and harness capability constraints."""
        for field in fields(class_or_instance=self.harness_requirements):
            if getattr(self.harness_requirements, field.name):
                if not getattr(client.harness_capabilities, field.name) or not getattr(
                    server.harness_capabilities, field.name
                ):
                    return False

        for field in fields(class_or_instance=self.protocol_requirements):
            if getattr(self.protocol_requirements, field.name):
                if not getattr(client.protocol_capabilities, field.name) or not getattr(
                    server.protocol_capabilities, field.name
                ):
                    return False

        return True

    async def execute(self, *, client: BaseEndpoint, server: BaseEndpoint) -> ScenarioResult:
        """Orchestrate execution and synthesize factual observations."""
        client_version = client.version
        server_version = server.version

        execution_result = await self._execute_workload(client=client, server=server)

        if not execution_result.completed:
            return ScenarioResult(
                client_name=client.name,
                client_version=client_version,
                reason=execution_result.error or self.default_error_message,
                scenario_name=self.name,
                server_name=server.name,
                server_version=server_version,
                verdict=Verdict.FAIL,
            )

        return ScenarioResult(
            client_name=client.name,
            client_version=client_version,
            reason=self.success_message,
            scenario_name=self.name,
            server_name=server.name,
            server_version=server_version,
            verdict=Verdict.PASS,
        )

    @abstractmethod
    async def _execute_workload(self, *, client: BaseEndpoint, server: BaseEndpoint) -> ExecutionResult:
        """Execute the core scenario logic and yield raw execution facts."""
        ...
