from dataclasses import fields, is_dataclass
from importlib import import_module, invalidate_caches
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import get_type_hints
import unittest

from docker_python.core import NotFoundError, Response, ResponseStream
from docker_python_generator.commands import CommandGenerator
from docker_python_generator.discovery import SchemaDiscovery
from docker_python_generator.models import ModelGenerator, snake
from docker_python_generator.swagger import load_spec

ROOT = Path(__file__).resolve().parents[2]


class RecordingTransport:
    def __init__(self, response=None):
        self.response = response or Response(204, {})
        self.requests = []
        self.closed = False

    def send(self, request):
        self.requests.append(request)
        return self.response

    def stream(self, request):
        self.requests.append(request)
        return ResponseStream(self.response.status, self.response.headers,
                              iter([b'first\n', b'second\n']), self.close)

    def close(self):
        self.closed = True


class CommandGenerationTests(unittest.TestCase):
    def test_all_operations_across_all_specs_generate_import_and_build(self):
        for spec_path in sorted((ROOT / 'docker-engine-api-specs').glob('*.yaml')):
            with self.subTest(spec=spec_path.name), TemporaryDirectory() as temp:
                spec = load_spec(spec_path)
                discovery = SchemaDiscovery(spec)
                package = 'generated_commands_' + spec['info']['version'].replace('.', '_')
                output = Path(temp) / package
                ModelGenerator(discovery.collect()).generate(output / 'models')
                CommandGenerator(spec).generate(output)
                sys.path.insert(0, temp)
                try:
                    invalidate_caches()
                    api = import_module(package)
                    commands = import_module(package + '.commands')
                    operations = list(discovery.operations())
                    self.assertEqual(set(commands.__all__), {op.name + 'Command' for op in operations})
                    self.assertEqual(len(list((output / 'commands').glob('*.py'))), len(operations) + 1)
                    client = api.DockerClient(RecordingTransport())
                    for operation in operations:
                        cls = getattr(commands, operation.name + 'Command')
                        self.assertTrue(is_dataclass(cls))
                        get_type_hints(cls)
                        factory = getattr(client, snake(operation.name))
                        get_type_hints(factory)
                        parameters = { (p['name'], p['in']): p for p in operation.parameters }
                        kwargs = {}
                        for parameter in cls.PARAMETERS:
                            original = parameters[(parameter.name, parameter.location)]
                            value = {'integer': 7, 'boolean': True, 'array': ['first', 'second']}.get(original.get('type'), 'a/b')
                            if parameter.location == 'body':
                                value = {}
                            kwargs[parameter.attribute] = value
                        command = factory(**kwargs)
                        request = command.build_request().build(client.version)
                        self.assertEqual(request.method, operation.method)
                        self.assertNotIn('{', request.path)
                        self.assertEqual(len(cls.PARAMETERS), len(operation.parameters))
                        statuses = {int(status) for status in operation.responses if status.isdigit()
                                    and (200 <= int(status) < 300 or status == '101')}
                        self.assertEqual(set(cls.RESPONSE.statuses), statuses)
                finally:
                    sys.path.remove(temp)
                    for module in list(sys.modules):
                        if module == package or module.startswith(package + '.'):
                            del sys.modules[module]

    def test_create_builders_and_typed_response(self):
        from docker_python.versions.v_1_44 import DockerClient
        from docker_python.versions.v_1_44.models import ContainerCreateRequest, ContainerCreateResponse
        transport = RecordingTransport(Response(201, {'Location': '/containers/abc'}, {'Id': 'abc', 'Warnings': []}))
        client = DockerClient(transport)
        command = client.container_create().with_body(ContainerCreateRequest(image='alpine')).with_name('sample')
        result = command.execute_response()
        self.assertIsInstance(result.body, ContainerCreateResponse)
        self.assertEqual(result.body.id, 'abc')
        self.assertEqual(result.status, 201)
        self.assertEqual(result.headers['Location'], '/containers/abc')
        request = transport.requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.query['name'], 'sample')
        self.assertEqual(request.headers['Content-Type'], 'application/json')
        self.assertEqual(request.body.to_wire(), {'Image': 'alpine'})

    def test_required_validation_path_encoding_empty_responses_and_errors(self):
        from docker_python.versions.v_1_44 import DockerClient
        from docker_python.versions.v_1_44.models import ErrorResponse
        transport = RecordingTransport()
        client = DockerClient(transport)
        with self.assertRaisesRegex(ValueError, 'id'):
            client.container_inspect().execute()
        self.assertEqual(transport.requests, [])
        self.assertIsNone(client.container_delete(id='name/with space').with_force(True).execute())
        self.assertEqual(transport.requests[-1].path, '/v1.44/containers/name%2Fwith%20space')
        transport.response = Response(404, {}, {'message': 'No such container'})
        with self.assertRaises(NotFoundError) as raised:
            client.container_inspect(id='missing').execute()
        self.assertIsInstance(raised.exception.response.body, ErrorResponse)
        self.assertEqual(raised.exception.response.body.message, 'No such container')

    def test_head_headers_binary_upload_and_stream_lifecycle(self):
        from docker_python.versions.v_1_44 import DockerClient
        transport = RecordingTransport(Response(200, {'X-Docker-Container-Path-Stat': 'metadata'}))
        client = DockerClient(transport)
        result = client.container_archive_info(id='abc', path='/tmp').execute_response()
        self.assertIsNone(result.body)
        self.assertEqual(result.headers['X-Docker-Container-Path-Stat'], 'metadata')
        request = client.image_build().with_input_stream(b'tar bytes').with_x_registry_config('auth').build_request()
        self.assertEqual(request.body, b'tar bytes')
        self.assertEqual(request.headers['X-Registry-Config'], 'auth')
        self.assertEqual(request.headers['Content-Type'], 'application/x-tar')
        with client.system_events().execute_stream() as stream:
            self.assertEqual(list(stream), [b'first\n', b'second\n'])
        self.assertTrue(transport.closed)


if __name__ == '__main__':
    unittest.main()
