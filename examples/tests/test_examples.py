from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
from threading import Thread
import unittest
from urllib.parse import parse_qs, urlsplit

EXAMPLES = Path(__file__).resolve().parents[1]
IMAGE = {
    'Id': 'sha256:example', 'ParentId': '', 'RepoTags': ['example:latest'],
    'RepoDigests': [], 'Created': 0, 'Size': 10, 'SharedSize': -1,
    'Labels': {}, 'Containers': 0, 'VirtualSize': 10,
}


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                cls.requests.append(self.path)
                path = urlsplit(self.path).path
                if path == '/version':
                    body = {'ApiVersion': '1.55', 'MinAPIVersion': '1.40'}
                elif path.endswith('/images/json'):
                    body = [IMAGE]
                elif path.endswith('/containers/json'):
                    body = [{'Id': 'container-id', 'Image': 'example:latest', 'Names': ['/example']}]
                elif path.endswith('/networks'):
                    body = [{'Name': 'first', 'Id': 'network-1'}, {'Name': 'second', 'Id': 'network-2'}]
                else:
                    self.send_error(404)
                    return
                payload = json.dumps(body).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

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

    def run_example(self, script, *arguments):
        result = subprocess.run(
            [sys.executable, str(EXAMPLES / script), '--host', self.host, *arguments],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')  # stdlib logging uses stderr by default.
        return result.stderr.splitlines()

    def test_fixed_version_scripts_print_each_dataclass(self):
        lines = self.run_example('list-networks.py')
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("Network(name='first'"))
        self.assertTrue(lines[1].startswith("Network(name='second'"))
        self.assertIn('/v1.55/networks', self.requests)
        lines = self.run_example('list-images.py')
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("ImageSummary(id='sha256:example'"))
        self.assertTrue(any(path.startswith('/v1.44/images/json') for path in self.requests))

    def test_cli_dispatches_every_command_for_each_version(self):
        for version in ['v_1_40', 'v_1_44', 'v_1_55']:
            prefix = '/v' + version.removeprefix('v_').replace('_', '.')
            for args, endpoint, model in [
                (['images', '--all'], '/images/json', 'ImageSummary('),
                (['ps', '--all'], '/containers/json', 'ContainerSummary('),
                (['network', 'ls'], '/networks', 'Network('),
            ]:
                with self.subTest(version=version, command=args):
                    lines = self.run_example('example-cli.py', '--api-version', version, *args)
                    self.assertTrue(all(line.startswith(model) for line in lines))
                    request = urlsplit(self.requests[-1])
                    self.assertEqual(request.path, prefix + endpoint)
                    if '--all' in args:
                        self.assertEqual(parse_qs(request.query)['all'], ['true'])

    def test_cli_reports_an_incompatible_api_before_listing(self):
        # The compatibility logic lives in core; verify the CLI surfaces its failure.
        from unittest.mock import patch
        from docker_python_examples.cli import main
        arguments = ['example-cli.py', '--host', self.host, 'images']
        with patch.object(sys, 'argv', arguments), patch(
            'docker_python.core.Client.check_version', side_effect=ValueError('incompatible API'),
        ), self.assertLogs('docker_python.examples', level='ERROR') as logs:
            self.assertEqual(main(), 1)
        self.assertIn('incompatible API', logs.output[0])


if __name__ == '__main__':
    unittest.main()
