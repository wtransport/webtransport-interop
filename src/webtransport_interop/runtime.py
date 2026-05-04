"""Execution runtime engine for orchestrating interoperability tests."""

from __future__ import annotations

import asyncio
from contextlib import suppress

from webtransport_interop.config import HarnessConfig
from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.scenarios.base_scenario import BaseScenario
from webtransport_interop.types import ScenarioResult, Verdict


class TestRuntime:
    """Manages the lifecycle and orchestration of a test matrix execution."""

    async def execute_matrix(
        self, *, scenario: BaseScenario, client: BaseEndpoint, server: BaseEndpoint
    ) -> ScenarioResult:
        """Executes a single combination of scenario, client, and server."""
        client_version = client.version
        server_version = server.version

        if not scenario.check_capabilities(client=client, server=server):
            return ScenarioResult(
                client_name=client.name,
                client_version=client_version,
                reason="capability mismatch",
                scenario_name=scenario.name,
                server_name=server.name,
                server_version=server_version,
                verdict=Verdict.SKIP,
            )

        try:
            await server.start()
            await asyncio.sleep(delay=HarnessConfig.RUNTIME_STARTUP_DELAY)
            await client.start()
            return await scenario.execute(client=client, server=server)
        except Exception as e:
            return ScenarioResult(
                client_name=client.name,
                client_version=client_version,
                reason=f"runtime error: {e}",
                scenario_name=scenario.name,
                server_name=server.name,
                server_version=server_version,
                verdict=Verdict.FAIL,
            )
        finally:
            await self._teardown(client=client, server=server)

    async def _teardown(self, *, client: BaseEndpoint, server: BaseEndpoint) -> None:
        """Ensures both endpoints are stopped cleanly."""
        with suppress(Exception):
            await client.stop()
        with suppress(Exception):
            await server.stop()
