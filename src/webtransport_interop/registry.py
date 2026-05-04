"""Harness component registries."""

from __future__ import annotations

from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.endpoints.clients.chrome import ChromeClient
from webtransport_interop.endpoints.clients.edge import EdgeClient
from webtransport_interop.endpoints.clients.pywebtransport import PyWebTransportClient
from webtransport_interop.endpoints.servers.pywebtransport import PyWebTransportServer
from webtransport_interop.endpoints.servers.wtransport_interop_service import WTransportInteropServiceServer
from webtransport_interop.scenarios.base_scenario import BaseScenario
from webtransport_interop.scenarios.devious_baton import DeviousBatonScenario
from webtransport_interop.scenarios.echo import EchoScenario

CLIENT_REGISTRY: dict[str, type[BaseEndpoint]] = {
    "chrome": ChromeClient,
    "edge": EdgeClient,
    "pywebtransport": PyWebTransportClient,
}

SCENARIO_REGISTRY: dict[str, type[BaseScenario]] = {
    "devious_baton": DeviousBatonScenario,
    "echo": EchoScenario,
}

SERVER_REGISTRY: dict[str, type[BaseEndpoint]] = {
    "pywebtransport": PyWebTransportServer,
    "wtransport_interop_service": WTransportInteropServiceServer,
}
