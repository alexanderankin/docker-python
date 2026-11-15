"""HTTP over local Windows named pipes using overlapped pywin32 I/O."""

import io
import math
import sys
from pathlib import Path

from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool


class _PipeReader(io.RawIOBase):
    def __init__(self, pipe):
        super().__init__()
        self.pipe = pipe

    def readable(self):
        return True

    def readinto(self, buffer):
        data = self.pipe.recv(len(buffer))
        buffer[: len(data)] = data
        return len(data)


class PipeSocket:
    def __init__(self, path: Path, timeout):
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

    def settimeout(self, timeout):
        self.timeout = timeout

    def _io(self, data, *, read):
        operation = self._types.OVERLAPPED()
        operation.hEvent = self._event.CreateEvent(None, True, False, None)
        try:
            try:
                if read:
                    status, buffer = self._file.ReadFile(self.handle, data, operation)
                else:
                    status, _ = self._file.WriteFile(self.handle, data, operation)
                if status == 997:  # ERROR_IO_PENDING
                    milliseconds = (
                        0xFFFFFFFF if self.timeout is None else min(math.ceil(self.timeout * 1000), 0xFFFFFFFE)
                    )
                    if self._event.WaitForSingleObject(operation.hEvent, milliseconds) == 258:
                        self._file.CancelIoEx(self.handle, operation)
                        # Keep the buffer and OVERLAPPED alive until cancellation completes.
                        try:
                            self._file.GetOverlappedResult(self.handle, operation, True)
                        except self._types.error:
                            pass
                        raise TimeoutError("Docker named pipe operation timed out")
                count = self._file.GetOverlappedResult(self.handle, operation, True)
                return bytes(buffer[:count]) if read else count
            except self._types.error as error:
                if read and error.winerror in (109, 232, 233):
                    return b""
                raise OSError(error.winerror, error.strerror) from error
        finally:
            operation.hEvent.Close()

    def recv(self, size):
        return self._io(size, read=True)

    def sendall(self, data):
        remaining = memoryview(data)
        while remaining:
            count = self._io(remaining, read=False)
            if not count:
                raise OSError("Docker named pipe closed while writing")
            remaining = remaining[count:]

    def makefile(self, mode, buffering=None):
        return io.BufferedReader(_PipeReader(self))

    def close(self):
        if self.handle is not None:
            self.handle.Close()
            self.handle = None


class PipeConnection(HTTPConnection):
    def __init__(self, *args, pipe_path, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipe_path = pipe_path
        self.sock: PipeSocket | None = None

    def connect(self):
        self.sock = PipeSocket(self.pipe_path, self.timeout)

    @property
    def is_connected(self):
        # Named pipe handles cannot be polled by urllib3's socket select().
        return self.sock is not None and self.sock.handle is not None


class PipeConnectionPool(HTTPConnectionPool):
    ConnectionCls = PipeConnection


class NamedPipeAdapter(HTTPAdapter):
    def __init__(self, pipe_path, **kwargs):
        super().__init__(**kwargs)
        self.pipe_pool = PipeConnectionPool("localhost", pipe_path=pipe_path)

    def get_connection(self, url, proxies=None):
        return self.pipe_pool

    def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
        return self.pipe_pool

    def request_url(self, request, proxies):
        return request.path_url

    def close(self):
        self.pipe_pool.close()
        super().close()
