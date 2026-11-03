from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
import unittest
from urllib.parse import parse_qs, urlsplit

from docker_python.core import Request
from docker_python.transports.requests import RequestsTransport


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.received = []

        class Handler(BaseHTTPRequestHandler):
            def handle_request(self):
                body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
                cls.received.append((self.command, self.path, dict(self.headers), body))
                path = urlsplit(self.path).path
                payload, content_type = b'{"ok":true}', 'application/json'
                status = 200
                if path == '/bytes':
                    payload, content_type = b'\x00\xfftar data', 'application/x-tar'
                elif path == '/jsonl':
                    payload = b'{"id":1}\n{"id":2}\n'
                elif path == '/upgrade':
                    status, payload = 101, b''
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('X-Example', 'header-value')
                self.end_headers()
                if self.command != 'HEAD':
                    self.wfile.write(payload)

            do_GET = handle_request
            do_POST = handle_request
            do_HEAD = handle_request

            def log_message(self, *args):
                pass

        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.host = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.transport = RequestsTransport(self.host)
        self.addCleanup(self.transport.close)

    def test_binary_upload_and_collection_formats(self):
        response = self.transport.send(Request(
            'POST', '/echo', query={'changes': ['ENV A=1', 'ENV B=2'], 'platform': ['linux/amd64', 'linux/arm64'],
                                   'all': True, 'filters': {'status': ['running']}},
            headers={'Content-Type': 'application/x-tar', 'X-Registry-Auth': 'test-auth'},
            body=b'\x00\xffarchive', query_formats={'changes': 'multi', 'platform': 'csv'},
        ))
        self.assertEqual(response.body, {'ok': True})
        method, path, headers, body = self.received[-1]
        query = parse_qs(urlsplit(path).query)
        self.assertEqual(method, 'POST')
        self.assertEqual(query['changes'], ['ENV A=1', 'ENV B=2'])
        self.assertEqual(query['platform'], ['linux/amd64,linux/arm64'])
        self.assertEqual(query['all'], ['true'])
        self.assertEqual(json.loads(query['filters'][0]), {'status': ['running']})
        self.assertEqual(headers['X-Registry-Auth'], 'test-auth')
        self.assertEqual(body, b'\x00\xffarchive')

    def test_json_null_and_absent_bodies(self):
        self.transport.send(Request('POST', '/echo', body={'Image': 'alpine'}))
        self.assertEqual(json.loads(self.received[-1][3]), {'Image': 'alpine'})
        self.transport.send(Request('POST', '/echo', body=None))
        self.assertEqual(self.received[-1][3], b'null')
        self.transport.send(Request('POST', '/echo'))
        self.assertEqual(self.received[-1][3], b'')

    def test_form_and_file_parameters(self):
        self.transport.send(Request('POST', '/echo', form={'name': 'example'}, files={'archive': b'tar bytes'}))
        _, _, headers, body = self.received[-1]
        self.assertTrue(headers['Content-Type'].startswith('multipart/form-data; boundary='))
        self.assertIn(b'name="name"', body)
        self.assertIn(b'example', body)
        self.assertIn(b'name="archive"', body)
        self.assertIn(b'tar bytes', body)

    def test_binary_ndjson_headers_streams_and_upgrade_rejection(self):
        self.assertEqual(self.transport.send(Request('GET', '/bytes')).body, b'\x00\xfftar data')
        self.assertEqual(self.transport.send(Request('GET', '/jsonl')).body, b'{"id":1}\n{"id":2}\n')
        response = self.transport.send(Request('HEAD', '/metadata'))
        self.assertIsNone(response.body)
        self.assertEqual(response.headers['X-Example'], 'header-value')
        with self.transport.stream(Request('GET', '/bytes')) as stream:
            self.assertEqual(b''.join(stream), b'\x00\xfftar data')
        with self.assertRaisesRegex(NotImplementedError, 'interactive HTTP upgrades'):
            self.transport.stream(Request('GET', '/upgrade'))


if __name__ == '__main__':
    unittest.main()
