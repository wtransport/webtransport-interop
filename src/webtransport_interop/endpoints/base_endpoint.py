"""Endpoint abstractions for the interoperability harness."""

from __future__ import annotations

from abc import ABC, abstractmethod

from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities


class BaseEndpoint(ABC):
    """Interface for protocol execution endpoints."""

    @property
    @abstractmethod
    def harness_capabilities(self) -> HarnessCapabilities:
        """Endpoint harness execution capabilities."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Harness registration identity."""
        ...

    @property
    @abstractmethod
    def protocol_capabilities(self) -> ProtocolCapabilities:
        """Endpoint protocol feature capabilities."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Implementation version identifier."""
        ...

    @abstractmethod
    def get_logs(self) -> str:
        """Retrieve execution diagnostic logs."""
        ...

    @abstractmethod
    async def run_scenario(self, *, name: str) -> ExecutionResult:
        """Execute scenario workload."""
        ...

    @abstractmethod
    async def start(self) -> None:
        """Initialize endpoint runtime."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Terminate endpoint resources."""
        ...
