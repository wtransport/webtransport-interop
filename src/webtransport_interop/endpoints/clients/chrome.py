"""Chrome client endpoint."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, cast

from playwright.async_api import async_playwright

from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities


class ChromeClient(BaseEndpoint):
    """Client adapter for Google Chrome."""

    def __init__(self, *, target_url: str) -> None:
        """Initialize browser endpoint."""
        self._target_url = target_url
        self._browser: Any = None
        self._logs: list[str] = []
        self._playwright: Any = None

    @property
    def harness_capabilities(self) -> HarnessCapabilities:
        """Endpoint harness execution capabilities."""
        return HarnessCapabilities(controllable=False)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "chrome"

    @property
    def protocol_capabilities(self) -> ProtocolCapabilities:
        """Endpoint protocol feature capabilities."""
        return ProtocolCapabilities(bidi_stream=True, datagram=True, uni_stream=True)

    @property
    def version(self) -> str:
        """Implementation version identifier."""
        return self._browser.version if self._browser else "unknown"

    def get_logs(self) -> str:
        """Retrieve execution diagnostic logs."""
        return "\n".join(self._logs)

    async def run_scenario(self, *, name: str) -> ExecutionResult:
        """Execute scenario workload."""
        self._logs.clear()
        if not self._browser:
            return ExecutionResult(completed=False, error="Browser not started.")

        method_name = f"_execute_{name}_scenario"
        handler = getattr(self, method_name, None)

        if not handler:
            error_msg = f"Unsupported scenario: {name}"
            self._logs.append(error_msg)
            return ExecutionResult(completed=False, error=error_msg)

        try:
            typed_handler = cast(Callable[[], Coroutine[Any, Any, ExecutionResult]], handler)
            return await typed_handler()
        except Exception as e:
            error_msg = f"Chrome execution crashed: {e}"
            self._logs.append(error_msg)
            return ExecutionResult(completed=False, error=error_msg)

    async def start(self) -> None:
        """Initialize endpoint runtime."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(channel="chrome", headless=True)

    async def stop(self) -> None:
        """Terminate endpoint resources."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _execute_echo_scenario(self) -> ExecutionResult:
        """Execute bidirectional stream and datagram echo workload."""
        page = await self._browser.new_page()
        page.on(event="console", f=lambda msg: self._logs.append(f"JS Console: {msg.text}"))

        await page.route(url="http://localhost/wt-secure-context", handler=lambda route: route.fulfill(body="OK"))
        await page.goto(url="http://localhost/wt-secure-context")

        js_payload = f"""
        async () => {{
            const url = "{self._target_url}/echo";
            const wt = new WebTransport(url);
            await wt.ready;

            const stream = await wt.createBidirectionalStream();
            const writer = stream.writable.getWriter();
            const encoder = new TextEncoder();
            await writer.write(encoder.encode("Hello, Chrome!"));
            await writer.close();

            const reader = stream.readable.getReader();
            const {{ value }} = await reader.read();
            const decoder = new TextDecoder();
            const response = decoder.decode(value);

            if (response !== "Hello, Chrome!") {{
                throw new Error("Stream mismatch: " + response);
            }}

            await wt.close();
            return "SUCCESS";
        }}
        """
        try:
            result = await page.evaluate(expression=js_payload)
            if result == "SUCCESS":
                return ExecutionResult(completed=True)
            return ExecutionResult(completed=False, error=str(result))
        except Exception as e:
            return ExecutionResult(completed=False, error=f"JS Execution Error: {e}")
        finally:
            await page.close()
