"""Pure function reporting layer for serializing execution outcomes."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from webtransport_interop.config import HarnessConfig
from webtransport_interop.types import ScenarioResult


def write_report(*, output_file: str = "matrix_result.json", results: list[ScenarioResult]) -> Path:
    """Serialize scenario outcomes into a versioned JSON report."""
    sorted_results = sorted(
        results,
        key=lambda x: (x.scenario_name, x.client_name, x.server_name),
    )

    raw_data: list[dict[str, Any]] = [asdict(obj=result) for result in sorted_results]

    report_envelope = {
        "meta": {
            "protocol": HarnessConfig.PROTOCOL_VERSION,
            "timestamp": int(datetime.now(tz=timezone.utc).timestamp()),
            "version": HarnessConfig.VERSION,
        },
        "results": raw_data,
    }

    out_path = Path(output_file).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file=out_path, mode="w", encoding="utf-8") as f:
        json.dump(obj=report_envelope, fp=f, ensure_ascii=False, indent=2)

    return out_path
