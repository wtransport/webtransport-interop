"""Firefox client endpoint."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, cast

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities


class FirefoxClient(BaseEndpoint):
    """Client adapter for Mozilla Firefox."""

    def __init__(self, *, target_url: str) -> None:
        """Initialize browser endpoint."""
        self._target_url = target_url
        self._browser: webdriver.Firefox | None = None
        self._logs: list[str] = []

    @property
    def harness_capabilities(self) -> HarnessCapabilities:
        """Endpoint harness execution capabilities."""
        return HarnessCapabilities(controllable=False)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "firefox"

    @property
    def protocol_capabilities(self) -> ProtocolCapabilities:
        """Endpoint protocol feature capabilities."""
        return ProtocolCapabilities(bidi_stream=True, datagram=True, uni_stream=True)

    @property
    def version(self) -> str:
        """Implementation version identifier."""
        return str(self._browser.capabilities.get("browserVersion", "unknown")) if self._browser else "unknown"

    def get_logs(self) -> str:
        """Retrieve execution diagnostic logs."""
        return "\n".join(self._logs)

    async def run_scenario(self, *, name: str) -> ExecutionResult:
        """Execute scenario workload."""
        self._logs.clear()
        if not self._browser:
            return ExecutionResult(completed=False, error="browser not started")

        method_name = f"_execute_{name}_scenario"
        handler = getattr(self, method_name, None)

        if not handler:
            error_msg = f"unsupported scenario: {name}"
            self._logs.append(error_msg)
            return ExecutionResult(completed=False, error=error_msg)

        try:
            typed_handler = cast(Callable[[], Coroutine[Any, Any, ExecutionResult]], handler)
            return await typed_handler()
        except Exception as e:
            error_msg = f"firefox execution crashed: {e}"
            self._logs.append(error_msg)
            return ExecutionResult(completed=False, error=error_msg)

    async def start(self) -> None:
        """Initialize endpoint runtime."""

        def _launch() -> webdriver.Firefox:
            options = FirefoxOptions()
            options.add_argument("--headless")
            return webdriver.Firefox(options=options)

        self._browser = await asyncio.to_thread(_launch)

    async def stop(self) -> None:
        """Terminate endpoint resources."""
        if self._browser:
            await asyncio.to_thread(self._browser.quit)

    async def _execute_echo_scenario(self) -> ExecutionResult:
        """Execute bidirectional stream and datagram echo workload."""
        if not self._browser:
            return ExecutionResult(completed=False, error="browser not started")

        async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            data = await reader.read(1024)
            if b"GET /wt-secure-context" in data:
                writer.write(
                    (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html\r\n"
                        "Content-Length: 2\r\n"
                        "Access-Control-Allow-Origin: *\r\n\r\nOK"
                    ).encode()
                )
            await writer.drain()
            writer.close()

        server = await asyncio.start_server(handle_request, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]

        await asyncio.to_thread(self._browser.get, f"http://127.0.0.1:{port}/wt-secure-context")

        js_payload = f"""
        const callback = arguments[arguments.length - 1];
        (async () => {{
            try {{
                const url = "{self._target_url}/echo";
                const wt = new WebTransport(url);
                await wt.ready;

                const stream = await wt.createBidirectionalStream();
                const writer = stream.writable.getWriter();
                const encoder = new TextEncoder();
                await writer.write(encoder.encode("Hello, Firefox!"));
                await writer.close();

                const reader = stream.readable.getReader();
                const {{ value }} = await reader.read();
                const decoder = new TextDecoder();
                const response = decoder.decode(value);

                if (response !== "Hello, Firefox!") {{
                    throw new Error("stream mismatch: " + response);
                }}

                await wt.close();
                callback("SUCCESS");
            }} catch (e) {{
                callback(e.message);
            }}
        }})();
        """

        try:
            result = await asyncio.to_thread(self._browser.execute_async_script, js_payload)
            if result == "SUCCESS":
                return ExecutionResult(completed=True)
            return ExecutionResult(completed=False, error=str(result))
        except Exception as e:
            return ExecutionResult(completed=False, error=f"selenium evaluation failed: {e}")
        finally:
            server.close()
            await server.wait_closed()
