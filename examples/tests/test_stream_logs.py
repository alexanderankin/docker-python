import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

from docker_python.core import DockerError, NotFoundError, Response, ResponseStream
from docker_python.versions.v_1_55.models import ContainerCreateResponse

spec = importlib.util.spec_from_file_location('stream_logs_example', Path(__file__).resolve().parents[1] / 'stream-logs.py')
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class StreamLogsTests(unittest.TestCase):
    def test_line_buffer_handles_split_utf8_multiple_lines_and_crlf(self):
        self.assertEqual(list(example.lines([b'caf\xc3', b'\xa9\r\nsecond\npar', b'tial'])), ['café', 'second'])

    def run_main(self, client):
        with patch.object(sys, 'argv', ['stream-logs.py']), patch.object(example, 'DockerClient', return_value=client), patch.object(
            example, 'RequestsTransport', return_value=Mock(),
        ), self.assertLogs('docker_python.examples', level='INFO') as logs:
            result = example.main()
        return result, logs.output

    def client(self):
        client = Mock()
        client.container_create.return_value.execute.return_value = ContainerCreateResponse(id='example-id', warnings=[])
        return client

    def test_stops_at_thirty_lines_closes_stream_and_cleans_up(self):
        client = self.client()
        close = Mock()
        stream = ResponseStream(200, {}, iter([b''.join(f'line {i}\n'.encode() for i in range(1, 36))]), close)
        client.container_logs.return_value.execute_stream.return_value = stream
        result, logs = self.run_main(client)
        self.assertEqual(result, 0)
        messages = [message for message in logs if 'new log line:' in message]
        self.assertEqual(len(messages), 30)
        self.assertTrue(messages[-1].endswith('new log line: line 30'))
        self.assertTrue(any('Created container: example-id' in message for message in logs))
        close.assert_called_once()
        client.container_start.assert_called_once_with(id='example-id')
        client.container_logs.assert_called_once_with(id='example-id', follow=True, stdout=True, stderr=True)
        client.container_stop.assert_called_once_with(id='example-id', t=2)
        client.container_delete.assert_called_once_with(id='example-id', force=True)
        config = client.container_create.call_args.kwargs['body']
        self.assertEqual(config.image, 'alpine:latest')
        self.assertTrue(config.tty)
        methods = [call[0] for call in client.method_calls]
        self.assertLess(methods.index('container_create'), methods.index('container_start'))
        self.assertLess(methods.index('container_start'), methods.index('container_logs'))
        self.assertLess(methods.index('container_stop'), methods.index('container_delete'))

    def test_start_failure_still_removes_a_container_that_is_not_running(self):
        client = self.client()
        client.container_start.return_value.execute.side_effect = DockerError(Response(500, {}, 'start failed'))
        client.container_stop.return_value.execute.side_effect = DockerError(Response(304, {}))
        result, _ = self.run_main(client)
        self.assertEqual(result, 1)
        client.container_delete.assert_called_once_with(id='example-id', force=True)

    def test_pulls_missing_alpine_and_cleans_up_on_interruption(self):
        client = self.client()
        client.container_create.return_value.execute.side_effect = [
            NotFoundError(Response(404, {}, 'missing image')),
            ContainerCreateResponse(id='example-id', warnings=[]),
        ]
        close_pull = Mock()
        client.image_create.return_value.execute_stream.return_value = ResponseStream(200, {}, iter([b'pulling']), close_pull)
        client.container_logs.return_value.execute_stream.side_effect = KeyboardInterrupt
        result, _ = self.run_main(client)
        self.assertEqual(result, 130)
        client.image_create.assert_called_once_with(from_image='alpine', tag='latest')
        close_pull.assert_called_once()
        client.container_stop.assert_called_once_with(id='example-id', t=2)
        client.container_delete.assert_called_once_with(id='example-id', force=True)


if __name__ == '__main__':
    unittest.main()
