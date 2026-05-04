"""Protocol types and execution data structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


@dataclass(slots=True, kw_only=True)
class HarnessCapabilities:
    """Endpoint harness execution capabilities."""

    controllable: bool = False


@dataclass(slots=True, kw_only=True)
class ProtocolCapabilities:
    """Endpoint protocol feature capabilities."""

    bidi_stream: bool = False
    capsule: bool = False
    datagram: bool = False
    stream_reset: bool = False
    uni_stream: bool = False


@dataclass(slots=True, kw_only=True)
class ExecutionResult:
    """Endpoint execution output contract."""

    completed: bool
    details: dict[str, Any] | None = None
    error: str | None = None


@dataclass(slots=True, kw_only=True)
class ScenarioResult:
    """Standardized scenario execution verdict."""

    client_name: str
    client_version: str
    reason: str
    scenario_name: str
    server_name: str
    server_version: str
    verdict: Verdict


class Verdict(StrEnum):
    """Scenario execution status enumerations."""

    FAIL = "fail"
    PASS = "pass"
    SKIP = "skip"
