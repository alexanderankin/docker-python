import socket
import sys
import unittest
from threading import Thread
from types import SimpleNamespace
from unittest.mock import Mock, patch

from docker_python.core import Request
from docker_python.transports.requests import RequestsTransport
from docker_python.transports.requests.npipe import PipeSocket


class NamedPipeTests(unittest.TestCase):
    def test_requests_and_streaming_over_pipe_connection(self):
        client, server = socket.socketpair()
        self.addCleanup(client.close)
        self.addCleanup(server.close)
        received = []

        def serve():
            with server.makefile('rb') as reader:
                for _ in range(2):
                    received.append(reader.readline())
                    while reader.readline() != b'\r\n':
                        pass
                    server.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                                   b'Transfer-Encoding: chunked\r\n\r\nB\r\n{"ok":true}\r\n0\r\n\r\n')

        thread = Thread(target=serve, daemon=True)
        thread.start()
        pipe = Mock(wraps=client)
        pipe.handle = object()
        with patch('docker_python.transports.requests.npipe.PipeSocket', return_value=pipe) as factory:
            with_transport = RequestsTransport('npipe:////./pipe/docker_engine')
            self.addCleanup(with_transport.close)
            self.assertFalse(with_transport.session.trust_env)
            self.assertEqual(with_transport.send(Request('GET', '/info', query={'all': True})).body, {'ok': True})
            with with_transport.stream(Request('GET', '/events')) as response:
                self.assertEqual(b''.join(response), b'{"ok":true}')
            factory.assert_called_once_with('\\\\.\\pipe\\docker_engine', 60.0)
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(received, [b'GET /info?all=true HTTP/1.1\r\n', b'GET /events HTTP/1.1\r\n'])

    def test_invalid_pipe_paths(self):
        for url in ('npipe://remote/pipe/docker_engine', 'npipe:////./pipe/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                RequestsTransport(url)

    def test_overlapped_reads_writes_timeout_and_close(self):
        class WindowsError(Exception):
            winerror = 109
            strerror = 'broken pipe'

        event = Mock()
        file = Mock()
        file.ReadFile.return_value = (997, b'data')
        file.WriteFile.return_value = (997, None)
        file.GetOverlappedResult.return_value = 4
        event.WaitForSingleObject.return_value = 0
        types = SimpleNamespace(OVERLAPPED=lambda: SimpleNamespace(), error=WindowsError)
        with patch.object(sys, 'platform', 'win32'), patch.dict(sys.modules, {
            'pywintypes': types, 'win32event': event, 'win32file': file,
        }):
            pipe = PipeSocket('\\\\.\\pipe\\docker_engine', 0.25)
            self.assertEqual(pipe.recv(4), b'data')
            pipe.sendall(b'data')
            event.WaitForSingleObject.assert_called_with(event.CreateEvent.return_value, 250)
            event.WaitForSingleObject.return_value = 258
            with self.assertRaises(socket.timeout):
                pipe.recv(4)
            file.CancelIoEx.assert_called_once()
            file.ReadFile.side_effect = WindowsError()
            self.assertEqual(pipe.recv(4), b'')
            pipe.close()
            pipe.close()
            file.CreateFile.return_value.Close.assert_called_once()

    @unittest.skipIf(sys.platform == 'win32', 'Windows supports named pipes')
    def test_non_windows_error(self):
        with self.assertRaisesRegex(OSError, 'require Windows'):
            PipeSocket('\\\\.\\pipe\\docker_engine', 60)
