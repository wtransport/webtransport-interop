"""Execution matrix orchestrator for Cartesian product testing."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Protocol

from webtransport_interop.config import PyWebTransportConfig, WTransportInteropServiceConfig
from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.runtime import TestRuntime
from webtransport_interop.scenarios.base_scenario import BaseScenario
from webtransport_interop.types import ScenarioResult

_logger = logging.getLogger(name=__name__)


class ClientEndpointFactory(Protocol):
    """Type contract for client endpoint constructors."""

    def __call__(self, *, target_url: str) -> BaseEndpoint:
        """Instantiate a client endpoint."""
        ...


class ServerEndpointFactory(Protocol):
    """Type contract for server endpoint constructors."""

    def __call__(self) -> BaseEndpoint:
        """Instantiate a server endpoint."""
        ...


class MatrixRunner:
    """Generates combinations of implementations and orchestrates execution."""

    def __init__(
        self,
        *,
        scenarios: Sequence[type[BaseScenario]],
        clients: Sequence[ClientEndpointFactory],
        servers: Sequence[ServerEndpointFactory],
    ) -> None:
        """Initialize the matrix with component classes."""
        self._scenarios = scenarios
        self._clients = clients
        self._servers = servers

        self._runtime = TestRuntime()

    async def execute_all(self, *, target_url: str) -> list[ScenarioResult]:
        """Execute the star-topology combination of components."""
        all_results: list[ScenarioResult] = []

        for server_cls in self._servers:
            server_instance = server_cls()

            if server_instance.name == "wtransport_interop_service":
                actual_target = WTransportInteropServiceConfig.BASE_URL
            elif server_instance.name == "pywebtransport":
                actual_target = f"https://127.0.0.1:{PyWebTransportConfig.PORT}"
            else:
                actual_target = target_url

            is_baseline_server = server_instance.name == "wtransport_interop_service"

            for client_cls in self._clients:
                client_instance = client_cls(target_url=actual_target)

                is_baseline_client = client_instance.name == "pywebtransport"

                if not (is_baseline_server or is_baseline_client):
                    continue

                for scenario_cls in self._scenarios:
                    scenario_instance = scenario_cls()

                    _logger.info(
                        f"matrix execution: scenario={scenario_instance.name} "
                        f"client={client_instance.name} server={server_instance.name}"
                    )

                    result = await self._runtime.execute_matrix(
                        scenario=scenario_instance,
                        client=client_instance,
                        server=server_instance,
                    )

                    all_results.append(result)

        return all_results
