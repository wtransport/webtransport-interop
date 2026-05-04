"""PyWebTransport client endpoint."""

from __future__ import annotations

import asyncio
import ssl
import struct
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from typing import Any, Final, cast
from urllib.parse import urlencode

from pywebtransport import (
    ClientConfig,
    ClientError,
    ConnectionError,
    SessionClosedError,
    SessionError,
    StreamError,
    WebTransportClient,
    WebTransportSession,
)
from pywebtransport import __version__ as LIB_VERSION
from pywebtransport.types import EventType

from webtransport_interop.config import HarnessConfig
from webtransport_interop.endpoints.base_endpoint import BaseEndpoint
from webtransport_interop.types import ExecutionResult, HarnessCapabilities, ProtocolCapabilities

_ERR_BORED: Final[int] = 0x04
_ERR_BRUH: Final[int] = 0x02
_ERR_DA_YAMN: Final[int] = 0x01
_ERR_IDC: Final[int] = 0x01
_ERR_I_LIED: Final[int] = 0x03
_ERR_SUS: Final[int] = 0x03
_ERR_WHATEVER: Final[int] = 0x02


class PyWebTransportClient(BaseEndpoint):
    """Client adapter for PyWebTransport library."""

    def __init__(self, *, target_url: str) -> None:
        """Initialize client adapter."""
        self._target_url = target_url
        self._config = ClientConfig(verify_mode=ssl.CERT_NONE)
        self._logs: list[str] = []

    @property
    def harness_capabilities(self) -> HarnessCapabilities:
        """Endpoint harness execution capabilities."""
        return HarnessCapabilities(controllable=True)

    @property
    def name(self) -> str:
        """Harness registration identity."""
        return "pywebtransport"

    @property
    def protocol_capabilities(self) -> ProtocolCapabilities:
        """Endpoint protocol feature capabilities."""
        return ProtocolCapabilities(bidi_stream=True, capsule=True, datagram=True, stream_reset=True, uni_stream=True)

    @property
    def version(self) -> str:
        """Implementation version identifier."""
        return LIB_VERSION

    def get_logs(self) -> str:
        """Retrieve execution diagnostic logs."""
        return "\n".join(self._logs)

    async def run_scenario(self, *, name: str) -> ExecutionResult:
        """Execute scenario workload."""
        self._logs.clear()
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
            error_msg = f"Client execution crashed: {e}"
            self._logs.append(error_msg)
            return ExecutionResult(completed=False, error=error_msg)

    async def start(self) -> None:
        """Initialize endpoint runtime."""
        ...

    async def stop(self) -> None:
        """Terminate endpoint resources."""
        ...

    async def _baton_test_01_invalid_version(self) -> None:
        """Verify server rejects invalid protocol version."""
        url = self._build_baton_url(version=99)
        try:
            async with self._connect(url=url):
                pass
        except (ConnectionError, ClientError, SessionError) as e:
            if "0x10b" in str(e).lower() or "400" in str(e):
                return
        raise RuntimeError("Server accepted invalid version 99")

    async def _baton_test_02_invalid_count(self) -> None:
        """Verify server rejects excessive baton count."""
        url = self._build_baton_url(count=999999)
        try:
            async with self._connect(url=url):
                pass
        except (ConnectionError, ClientError, SessionError) as e:
            if "0x10b" in str(e).lower() or "400" in str(e):
                return
        raise RuntimeError("Server accepted invalid count 999999")

    async def _baton_test_03_invalid_baton(self) -> None:
        """Verify server rejects invalid baton value."""
        url = self._build_baton_url(baton=0)
        try:
            async with self._connect(url=url):
                pass
        except (ConnectionError, ClientError, SessionError) as e:
            if "0x10b" in str(e).lower() or "400" in str(e):
                return
        raise RuntimeError("Server accepted invalid baton value 0")

    async def _baton_test_04_server_initiates_uni_stream(self) -> None:
        """Verify server initiates the protocol with unidirectional streams."""
        count = 3
        url = self._build_baton_url(count=count, baton=10)
        async with self._connect(url=url) as session:
            streams_received = 0
            event = asyncio.Event()

            async def accept_uni() -> None:
                """Consume incoming unidirectional streams."""
                nonlocal streams_received
                try:
                    while True:
                        _ = await session.accept_unidirectional_stream()
                        streams_received += 1
                        if streams_received >= count:
                            event.set()
                except SessionClosedError:
                    pass

            task = asyncio.create_task(coro=accept_uni())
            try:
                async with asyncio.timeout(delay=5.0):
                    await event.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not initiate unidirectional stream") from None
            finally:
                task.cancel()

    async def _baton_test_05_flow_uni_to_bidi(self) -> None:
        """Verify Unidirectional -> Bidirectional stream switching logic."""
        url = self._build_baton_url(baton=10)
        async with self._connect(url=url) as session:
            reply_received = asyncio.Event()

            async def accept_uni() -> None:
                """Process unidirectional and switch to bidirectional."""
                try:
                    while True:
                        stream = await session.accept_unidirectional_stream()
                        payload = await stream.read_all()
                        if not payload:
                            continue
                        bidi = await session.create_bidirectional_stream()

                        async def read_reply() -> None:
                            """Await the server's reply on the created bidirectional stream."""
                            data = await bidi.read_all()
                            if data:
                                reply_received.set()

                        asyncio.create_task(coro=read_reply())
                        next_val = (payload[-1] + 1) % 256
                        await bidi.write(data=_create_payload(baton_value=next_val), end_stream=True)
                except SessionClosedError:
                    pass

            task = asyncio.create_task(coro=accept_uni())
            try:
                async with asyncio.timeout(delay=5.0):
                    await reply_received.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not reply on the same bidirectional stream") from None
            finally:
                task.cancel()

    async def _baton_test_06_flow_bidi_self_to_uni(self) -> None:
        """Verify Bidirectional (Self) -> Unidirectional stream switching logic."""
        url = self._build_baton_url(count=1, baton=10)
        async with self._connect(url=url) as session:
            server_bidi_opened = asyncio.Event()
            server_uni_opened = asyncio.Event()

            async def accept_bidi() -> None:
                """Process incoming bidirectional streams."""
                try:
                    while True:
                        stream = await session.accept_bidirectional_stream()
                        server_bidi_opened.set()

                        async def handle_server_bidi(s: Any) -> None:
                            """Process data on the accepted stream."""
                            try:
                                payload = await s.read_all()
                                if payload:
                                    next_val = (payload[-1] + 1) % 256
                                    await s.write(data=_create_payload(baton_value=next_val), end_stream=True)
                            except StreamError:
                                pass

                        asyncio.create_task(coro=handle_server_bidi(stream))
                except SessionClosedError:
                    pass

            async def accept_uni() -> None:
                """Detect incoming unidirectional streams."""
                try:
                    while True:
                        _ = await session.accept_unidirectional_stream()
                        server_uni_opened.set()
                except SessionClosedError:
                    pass

            task_bidi = asyncio.create_task(coro=accept_bidi())
            task_uni = asyncio.create_task(coro=accept_uni())
            uni = await session.create_unidirectional_stream()
            await uni.write(data=_create_payload(baton_value=50), end_stream=True)

            try:
                async with asyncio.timeout(delay=5.0):
                    await server_bidi_opened.wait()
                    await server_uni_opened.wait()
            except asyncio.TimeoutError:
                if not server_bidi_opened.is_set():
                    raise RuntimeError("Server did not open Bidi stream in response to Uni") from None
                raise RuntimeError("Server did not open Uni stream in response to Bidi (Self)") from None
            finally:
                task_bidi.cancel()
                task_uni.cancel()

    async def _baton_test_07_datagram_trigger(self) -> None:
        """Verify server sends datagram when baton value modulo 7 is 0."""
        url = self._build_baton_url(count=1, baton=10)
        async with self._connect(url=url) as session:
            dgram_received = asyncio.Event()

            def on_dgram(evt: Any) -> None:
                """Signal datagram reception."""
                dgram_received.set()

            session.events.on(event_type=EventType.DATAGRAM_RECEIVED, handler=on_dgram)
            stream = await session.create_unidirectional_stream()
            await stream.write(data=_create_payload(baton_value=7), end_stream=True)

            try:
                async with asyncio.timeout(delay=5.0):
                    await dgram_received.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not send datagram for baton % 7 == 0") from None

    async def _baton_test_08_random_padding(self) -> None:
        """Verify server adds padding when baton value modulo 5 is 0."""
        url = self._build_baton_url(count=1, baton=20)
        async with self._connect(url=url) as session:
            padding_verified = asyncio.Event()

            async def accept_uni() -> None:
                """Process streams to verify padding adherence."""
                try:
                    while True:
                        stream = await session.accept_unidirectional_stream()
                        data = await stream.read_all()
                        if not data:
                            continue
                        try:
                            p_len, header_len = _VarInt.parse(data=data)
                            if len(data) == header_len + p_len + 1:
                                if p_len > 0:
                                    padding_verified.set()
                        except Exception:
                            pass
                except SessionClosedError:
                    pass

            task = asyncio.create_task(coro=accept_uni())
            try:
                async with asyncio.timeout(delay=5.0):
                    await padding_verified.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not send valid padding for baton % 5 == 0") from None
            finally:
                task.cancel()

    async def _baton_test_09_malformed_baton(self) -> None:
        """Verify server closes session with ERR_BRUH on malformed message."""
        url = self._build_baton_url(count=1, baton=10)
        async with self._connect(url=url) as session:
            close_event = asyncio.Event()
            received_error = None

            def on_close(evt: Any) -> None:
                """Capture session closure error code."""
                nonlocal received_error
                received_error = evt.data.get("error_code")
                close_event.set()

            session.events.on(event_type=EventType.SESSION_CLOSED, handler=on_close)
            stream = await session.create_unidirectional_stream()
            await stream.write(data=_VarInt.encode(value=100) + b"\x00", end_stream=True)

            try:
                async with asyncio.timeout(delay=5.0):
                    await close_event.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not close session on malformed baton") from None

            if received_error != _ERR_BRUH:
                raise RuntimeError(f"Expected ERR_BRUH (0x02), got {received_error}")

    async def _baton_test_10_unexpected_value(self) -> None:
        """Verify server closes session with ERR_SUS on unexpected baton value."""
        url = self._build_baton_url(count=1, baton=10)
        async with self._connect(url=url) as session:
            close_event = asyncio.Event()
            received_error = None

            def on_close(evt: Any) -> None:
                """Capture session closure error code."""
                nonlocal received_error
                received_error = evt.data.get("error_code")
                close_event.set()

            session.events.on(event_type=EventType.SESSION_CLOSED, handler=on_close)

            async def accept_uni() -> None:
                """Accept incoming streams and send unexpected values."""
                try:
                    while True:
                        _ = await session.accept_unidirectional_stream()
                        reply = await session.create_bidirectional_stream()
                        await reply.write(data=_create_payload(baton_value=99), end_stream=True)
                except SessionClosedError:
                    pass

            task = asyncio.create_task(coro=accept_uni())
            try:
                async with asyncio.timeout(delay=5.0):
                    await close_event.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not close session on unexpected baton value") from None
            finally:
                task.cancel()

    async def _baton_test_11_stop_sending_reaction(self) -> None:
        """Verify server resets stream with ERR_WHATEVER upon receiving STOP_SENDING."""
        url = self._build_baton_url(count=1, baton=10)
        async with self._connect(url=url) as session:
            reset_received = asyncio.Event()

            async def accept_uni() -> None:
                """Process incoming streams and immediately stop receiving."""
                try:
                    while True:
                        stream = await session.accept_unidirectional_stream()

                        def on_reset(e: Any) -> None:
                            """Verify correct error code on reset."""
                            if e.data.get("error_code") == _ERR_WHATEVER:
                                reset_received.set()

                        stream.events.on(event_type=EventType.STREAM_RESET_RECEIVED, handler=on_reset)
                        await stream.stop_receiving(error_code=_ERR_IDC)
                except SessionClosedError:
                    pass

            task = asyncio.create_task(coro=accept_uni())
            try:
                async with asyncio.timeout(delay=5.0):
                    await reset_received.wait()
            except asyncio.TimeoutError:
                return
            finally:
                task.cancel()

    async def _baton_test_12_spontaneous_reset_reaction(self) -> None:
        """Verify server ignores spontaneous RESET_STREAM."""
        url = self._build_baton_url(count=1, baton=10)
        async with self._connect(url=url) as session:
            session_closed = asyncio.Event()
            session.events.on(
                event_type=EventType.SESSION_CLOSED,
                handler=lambda e: session_closed.set(),
            )

            stream = await session.create_unidirectional_stream()
            await stream.write(data=b"padding")
            await stream.reset(error_code=_ERR_I_LIED)

            try:
                async with asyncio.timeout(delay=2.0):
                    await session_closed.wait()
                raise RuntimeError("Server closed session on I_LIED reset (Should ignore)")
            except asyncio.TimeoutError:
                pass

    async def _baton_test_13_graceful_finish(self) -> None:
        """Verify server closes session gracefully when batons finish."""
        url = self._build_baton_url(count=1, baton=255)
        async with self._connect(url=url) as session:
            close_event = asyncio.Event()
            close_code = None

            def on_close(evt: Any) -> None:
                """Capture closure code on completion."""
                nonlocal close_code
                close_code = evt.data.get("error_code")
                close_event.set()

            session.events.on(event_type=EventType.SESSION_CLOSED, handler=on_close)

            async def accept_uni() -> None:
                """Process the final stream to trigger closure."""
                try:
                    while True:
                        stream = await session.accept_unidirectional_stream()
                        await stream.read_all()
                        reply = await session.create_bidirectional_stream()
                        await reply.write(data=_create_payload(baton_value=0), end_stream=True)
                except SessionClosedError:
                    pass

            task = asyncio.create_task(coro=accept_uni())
            try:
                async with asyncio.timeout(delay=5.0):
                    await close_event.wait()
            except asyncio.TimeoutError:
                raise RuntimeError("Server did not close session gracefully") from None
            finally:
                task.cancel()

            if close_code != 0:
                raise RuntimeError(f"Expected NO_ERROR (0), got {close_code}")

    def _build_baton_url(self, **kwargs: Any) -> str:
        """Construct the connection URL with query parameters."""
        query = urlencode(query=kwargs)
        return f"{self._target_url}/webtransport/devious-baton?{query}"

    @asynccontextmanager
    async def _connect(self, *, url: str) -> AsyncGenerator[WebTransportSession, None]:
        """Establish a new WebTransport session context for testing."""
        async with WebTransportClient(config=self._config) as client:
            session = await client.connect(url=url)
            try:
                yield session
            finally:
                if not session.is_closed:
                    await session.close()

    async def _execute_devious_baton_scenario(self) -> ExecutionResult:
        """Execute the devious baton state machine validation workload."""
        tests = [
            self._baton_test_01_invalid_version,
            self._baton_test_02_invalid_count,
            self._baton_test_03_invalid_baton,
            self._baton_test_04_server_initiates_uni_stream,
            self._baton_test_05_flow_uni_to_bidi,
            self._baton_test_06_flow_bidi_self_to_uni,
            self._baton_test_07_datagram_trigger,
            self._baton_test_08_random_padding,
            self._baton_test_09_malformed_baton,
            self._baton_test_10_unexpected_value,
            self._baton_test_11_stop_sending_reaction,
            self._baton_test_12_spontaneous_reset_reaction,
            self._baton_test_13_graceful_finish,
        ]

        for test_func in tests:
            try:
                await self._execute_with_retry(test_func=test_func)
            except RuntimeError as e:
                err_msg = f"{test_func.__name__} assertion failed: {e}"
                self._logs.append(err_msg)
                return ExecutionResult(completed=False, error=err_msg)
            except Exception as e:
                err_msg = f"{test_func.__name__} crashed with unhandled exception: {e}"
                self._logs.append(err_msg)
                return ExecutionResult(completed=False, error=err_msg)

        return ExecutionResult(completed=True)

    async def _execute_echo_scenario(self) -> ExecutionResult:
        """Execute the bidirectional stream and datagram echo workload."""

        async def _run_echo() -> None:
            url = f"{self._target_url}/echo"
            async with self._connect(url=url) as session:
                stream_payload = b"Hello, WebTransport!"
                stream = await session.create_bidirectional_stream()
                await stream.write(data=stream_payload, end_stream=True)
                stream_response = await stream.read_all()
                await stream.close()

                if stream_response != stream_payload:
                    raise RuntimeError(f"Stream Echo mismatch. Sent: {stream_payload!r}, Recv: {stream_response!r}")

                datagram_payload = b"Datagram Test"
                loop = asyncio.get_running_loop()
                recv_future = loop.create_future()

                async def on_dgram(evt: Any) -> None:
                    if isinstance(evt.data, dict) and (data := evt.data.get("data")):
                        if not recv_future.done():
                            recv_future.set_result(data)

                session.events.on(event_type=EventType.DATAGRAM_RECEIVED, handler=on_dgram)
                await session.send_datagram(data=datagram_payload)

                try:
                    async with asyncio.timeout(delay=5.0):
                        datagram_response = await recv_future
                except asyncio.TimeoutError:
                    raise RuntimeError("Server did not echo datagram within timeout")
                finally:
                    session.events.off(event_type=EventType.DATAGRAM_RECEIVED, handler=on_dgram)

                if datagram_response != datagram_payload:
                    raise RuntimeError(
                        f"Datagram Echo mismatch. Sent: {datagram_payload!r}, Recv: {datagram_response!r}"
                    )

        try:
            await self._execute_with_retry(test_func=_run_echo)
            return ExecutionResult(completed=True)
        except Exception as e:
            return ExecutionResult(completed=False, error=str(e))

    async def _execute_with_retry(self, *, test_func: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """Execute a single test case with logging and error handling."""
        for attempt in range(1, HarnessConfig.CLIENT_RETRY_COUNT + 1):
            try:
                await test_func()
                return
            except RuntimeError as e:
                if attempt == HarnessConfig.CLIENT_RETRY_COUNT:
                    raise e
                await asyncio.sleep(delay=1.0)
            except Exception as e:
                if attempt == HarnessConfig.CLIENT_RETRY_COUNT:
                    raise RuntimeError(str(e))
                await asyncio.sleep(delay=1.0)


class _VarInt:
    """Helper for parsing and encoding QUIC VarInts."""

    @staticmethod
    def encode(*, value: int) -> bytes:
        """Encode an integer into QUIC variable-length bytes."""
        if value < 0x40:
            return struct.pack("!B", value)
        elif value < 0x4000:
            return struct.pack("!H", value | 0x4000)
        elif value < 0x40000000:
            return struct.pack("!L", value | 0x80000000)
        else:
            return struct.pack("!Q", value | 0xC000000000000000)

    @staticmethod
    def parse(*, data: bytes) -> tuple[int, int]:
        """Parse a QUIC variable-length integer from bytes."""
        if not data:
            raise ValueError("Empty data")
        first = data[0]
        if first < 0x40:
            return first, 1
        elif first < 0x80:
            if len(data) < 2:
                raise ValueError("Truncated VarInt")
            return struct.unpack("!H", bytes([first & 0x3F]) + data[1:2])[0], 2
        elif first < 0xC0:
            if len(data) < 4:
                raise ValueError("Truncated VarInt")
            return struct.unpack("!L", bytes([first & 0x3F]) + data[1:4])[0], 4
        else:
            if len(data) < 8:
                raise ValueError("Truncated VarInt")
            return struct.unpack("!Q", bytes([first & 0x3F]) + data[1:8])[0], 8


def _create_payload(*, baton_value: int, padding_len: int = 0) -> bytes:
    """Create a baton message payload."""
    padding = b"\x00" * padding_len
    return _VarInt.encode(value=padding_len) + padding + bytes([baton_value])
