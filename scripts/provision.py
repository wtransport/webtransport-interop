"""Dynamic environment provisioning driven by the framework registry."""

from __future__ import annotations

import subprocess

from webtransport_interop.registry import CLIENT_REGISTRY


def provision_browsers() -> None:
    """Install official stable browser binaries for registered clients."""
    targets = []

    if "chrome" in CLIENT_REGISTRY:
        targets.append("chrome")
    if "edge" in CLIENT_REGISTRY:
        targets.append("msedge")
    if "firefox" in CLIENT_REGISTRY:
        targets.append("firefox")

    if not targets:
        return

    cmd = ["playwright", "install", "--with-deps", "--force"] + targets
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    provision_browsers()
