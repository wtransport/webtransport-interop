"""Command-line entry point for the interoperability test runner."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import cast

from webtransport_interop.config import HarnessConfig
from webtransport_interop.matrix import ClientEndpointFactory, MatrixRunner, ServerEndpointFactory
from webtransport_interop.registry import CLIENT_REGISTRY, SCENARIO_REGISTRY, SERVER_REGISTRY
from webtransport_interop.reporter import write_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

_logger = logging.getLogger(name=__name__)


async def main() -> None:
    """Parse arguments and orchestrate the interoperability test suite."""
    parser = argparse.ArgumentParser(description="WebTransport Interop")

    parser.add_argument(
        "--client",
        type=str,
        nargs="*",
        default=list(CLIENT_REGISTRY.keys()),
        help="clients to test",
    )
    parser.add_argument(
        "--server",
        type=str,
        nargs="*",
        default=list(SERVER_REGISTRY.keys()),
        help="servers to test",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        nargs="*",
        default=list(SCENARIO_REGISTRY.keys()),
        help="scenarios to run",
    )
    parser.add_argument("--target", type=str, default="https://127.0.0.1:4433", help="target server url")
    parser.add_argument("--output", type=str, default="matrix_result.json", help="report output path")

    args = parser.parse_args()

    _logger.info(f"starting wtransport interop runner: version={HarnessConfig.VERSION}")

    scenarios = [SCENARIO_REGISTRY[s] for s in args.scenario if s in SCENARIO_REGISTRY]
    clients = cast(list[ClientEndpointFactory], [CLIENT_REGISTRY[c] for c in args.client if c in CLIENT_REGISTRY])
    servers = cast(list[ServerEndpointFactory], [SERVER_REGISTRY[s] for s in args.server if s in SERVER_REGISTRY])

    if not (scenarios and clients and servers):
        _logger.error("invalid selection: matrix must contain at least one client, server, and scenario")
        sys.exit(1)

    runner = MatrixRunner(scenarios=scenarios, clients=clients, servers=servers)

    results = await runner.execute_all(target_url=args.target)

    report_path = write_report(output_file=args.output, results=results)

    _logger.info(f"interop testing complete: report_path={report_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("test execution interrupted by user")
        sys.exit(0)
