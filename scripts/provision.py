"""Dynamic environment provisioning driven by the framework registry."""

from __future__ import annotations

import subprocess

from selenium.webdriver.common.selenium_manager import SeleniumManager

from webtransport_interop.registry import CLIENT_REGISTRY


def provision_browsers() -> None:
    """Install official stable browser binaries for registered clients."""
    playwright_targets = []

    if "chrome" in CLIENT_REGISTRY:
        playwright_targets.append("chrome")
    if "edge" in CLIENT_REGISTRY:
        playwright_targets.append("msedge")

    if playwright_targets:
        cmd = ["playwright", "install", "--with-deps", "--force"] + playwright_targets
        subprocess.run(cmd, check=True)

    if "firefox" in CLIENT_REGISTRY:
        SeleniumManager().binary_paths(["--browser", "firefox"])


if __name__ == "__main__":
    provision_browsers()
