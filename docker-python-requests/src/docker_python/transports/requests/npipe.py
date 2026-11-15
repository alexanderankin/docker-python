"""HTTP over local Windows named pipes using overlapped pywin32 I/O."""

import io
import math
import sys
from collections.abc import Mapping
from socket import socket
from typing import TYPE_CHECKING, Any, Literal, cast, overload

from typing_extensions import Buffer
from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from urllib3.util import Timeout

from requests import PreparedRequest
from requests.adapters import HTTPAdapter

SocketTimeout = float | int | None
ConnectionTimeout = Timeout | float | int | None

if TYPE_CHECKING:
    if sys.platform == "win32":
        from _win32typing import PyHANDLE, PyOVERLAPPEDReadBuffer


class _PipeReader(io.RawIOBase):
    def __init__(self, pipe: "PipeSocket") -> None:
        super().__init__()
        self.pipe = pipe

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Buffer) -> int:
        view = memoryview(buffer)
        data = self.pipe.recv(len(view))
        view[: len(data)] = data
        return len(data)


class PipeSocket:
    def __init__(self, path: str, timeout: SocketTimeout) -> None:
        if sys.platform != "win32":
            raise OSError("Docker named pipes require Windows")

        import pywintypes
        import win32event
        import win32file

        self._types = pywintypes
        self._event = win32event
        self._file = win32file
        self.timeout = timeout

        try:
            self.handle = win32file.CreateFile(
                path,
                0xC0000000,
                0,
                None,
                3,
                0x40000000,
                None,
            )
        except pywintypes.error as error:
            raise OSError(error.winerror, error.strerror) from error

    # noinspection SpellCheckingInspection
    def settimeout(self, timeout: SocketTimeout) -> None:
        self.timeout = timeout

    @overload
    def _io(self, data: int, *, read: Literal[True]) -> bytes: ...

    @overload
    def _io(self, data: memoryview[int], *, read: Literal[False]) -> int: ...

    def _io(self, data: int | memoryview[int], *, read: bool) -> bytes | int:
        operation = self._types.OVERLAPPED()

        ce_return_value = self._event.CreateEvent(None, True, False, None)
        h_event: PyHANDLE = cast("PyHANDLE", cast(object, ce_return_value))

        operation.hEvent = h_event.handle

        try:
            try:
                buffer: PyOVERLAPPEDReadBuffer | None = None
                handle = self.handle
                assert handle is not None
                if read:
                    assert isinstance(data, int)
                    status, buffer = self._file.ReadFile(handle.handle, data, operation)
                else:
                    assert isinstance(data, memoryview)
                    status, _ = self._file.WriteFile(handle.handle, data, operation)

                if status == 997:  # ERROR_IO_PENDING
                    milliseconds = (
                        0xFFFFFFFF if self.timeout is None else min(math.ceil(self.timeout * 1000), 0xFFFFFFFE)
                    )

                    if self._event.WaitForSingleObject(operation.hEvent, milliseconds) == 258:
                        self._file.CancelIo(handle.handle)

                        # Keep the buffer and OVERLAPPED alive
                        # until cancellation completes.
                        try:
                            self._file.GetOverlappedResult(handle.handle, operation, True)
                        except self._types.error:
                            pass

                        raise TimeoutError("Docker named pipe operation timed out")

                count: int = self._file.GetOverlappedResult(handle.handle, operation, True)

                if read:
                    assert buffer is not None
                    return bytes(buffer[:count])
                return count

            except self._types.error as error:
                if read and error.winerror in (109, 232, 233):
                    return b""
                raise OSError(error.winerror, error.strerror) from error
        finally:
            h_event.Close()

    def recv(self, size: int) -> bytes:
        return self._io(size, read=True)

    def sendall(self, data: Buffer) -> None:
        remaining = memoryview(data)

        while remaining:
            count = self._io(remaining, read=False)
            if not count:
                raise OSError("Docker named pipe closed while writing")
            remaining = remaining[count:]

    # noinspection unused-parameter
    def makefile(self, mode: str, buffering: int | None = None) -> io.BufferedReader:
        return io.BufferedReader(_PipeReader(self))

    def close(self) -> None:
        if self.handle is not None:
            self.handle.Close()
            self.handle = None


class PipeConnection(HTTPConnection):
    def __init__(self, *args: Any, pipe_path: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pipe_path = pipe_path

    def connect(self) -> None:
        # urllib3 types sock as a standard socket.
        self.sock = cast(socket, cast(object, PipeSocket(self.pipe_path, self.timeout)))

    @property
    def is_connected(self) -> bool:
        # Named pipe handles cannot be polled by socket select().
        sock = cast(PipeSocket | None, self.sock)
        return sock is not None and sock.handle is not None


class PipeConnectionPool(HTTPConnectionPool):
    ConnectionCls = PipeConnection  # type: ignore


class NamedPipeAdapter(HTTPAdapter):
    def __init__(self, pipe_path: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pipe_pool = PipeConnectionPool("localhost", pipe_path=pipe_path)

    def get_connection(self, url: str | bytes, proxies: Mapping[str, str] | None = None) -> HTTPConnectionPool:
        return self.pipe_pool

    def get_connection_with_tls_context(
        self,
        request: PreparedRequest,
        verify: bool | str | None,
        proxies: Mapping[str, str] | None = None,
        cert: str | tuple[str, str] | None = None,
    ) -> HTTPConnectionPool:
        return self.pipe_pool

    def request_url(self, request: PreparedRequest, proxies: Mapping[str, str] | None) -> str:
        return request.path_url or "/"

    def close(self) -> None:
        self.pipe_pool.close()
        super().close()
