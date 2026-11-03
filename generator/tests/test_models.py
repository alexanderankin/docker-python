from dataclasses import is_dataclass
from importlib import import_module, invalidate_caches
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import get_type_hints
import unittest

from docker_python.core import Response
from docker_python.core.models import from_wire
from docker_python_generator.discovery import SchemaDiscovery
from docker_python_generator.models import ModelGenerator, snake
from docker_python_generator.swagger import load_spec

ROOT = Path(__file__).resolve().parents[2]


class ModelGenerationTests(unittest.TestCase):
    def test_every_bundled_spec_generates_importable_resolvable_models(self):
        for spec_path in sorted((ROOT / 'docker-engine-api-specs').glob('*.yaml')):
            with self.subTest(spec=spec_path.name), TemporaryDirectory() as temp:
                spec = load_spec(spec_path)
                package = 'generated_test_' + spec['info']['version'].replace('.', '_')
                output = Path(temp) / package
                schemas = SchemaDiscovery(spec).collect()
                ModelGenerator(schemas).generate(output)
                self.assertEqual(len(list(output.glob('*.py'))), len(schemas) + 1)
                sys.path.insert(0, temp)
                try:
                    invalidate_caches()
                    models = import_module(package)
                    for name in schemas:
                        module = import_module(package + '.' + snake(name))
                        self.assertIs(getattr(models, name), getattr(module, name))
                    for name in models.__all__:
                        cls = getattr(models, name)
                        if isinstance(cls, type) and is_dataclass(cls):
                            get_type_hints(cls)
                finally:
                    sys.path.remove(temp)
                    for name in list(sys.modules):
                        if name == package or name.startswith(package + '.'):
                            del sys.modules[name]

    def test_recursive_objects_and_collection_aliases(self):
        definitions = {
            'A': {'type': 'object', 'properties': {'B': {'$ref': '#/definitions/B'}}},
            'B': {'type': 'object', 'properties': {'A': {'$ref': '#/definitions/A'}}},
            'SelfList': {'type': 'array', 'items': {'$ref': '#/definitions/SelfList'}},
            'Left': {'type': 'array', 'items': {'$ref': '#/definitions/Right'}},
            'Right': {'type': 'array', 'items': {'$ref': '#/definitions/Left'}},
            'Tree': {'type': 'object', 'properties': {
                'Name': {'type': 'string'},
                'Children': {'$ref': '#/definitions/Children'},
            }},
            'Children': {'type': 'array', 'items': {'$ref': '#/definitions/Tree'}},
        }
        with TemporaryDirectory() as temp:
            package = 'recursive_test_models'
            ModelGenerator(definitions).generate(Path(temp) / package)
            sys.path.insert(0, temp)
            try:
                models = import_module(package)
                # Import individual modules as users do, and resolve hints without custom globals.
                self.assertIs(import_module(package + '.a').A, models.A)
                self.assertIs(get_type_hints(models.A)['b'].__args__[0], models.B)
                self.assertIsInstance(models.A.from_wire({'B': {'A': {}}}).b.a, models.A)
                tree = models.Tree.from_wire({'Name': 'root', 'Children': [{'Name': 'leaf'}]})
                self.assertIsInstance(tree.children[0], models.Tree)
                self.assertEqual(tree.children[0].name, 'leaf')
                self.assertEqual(from_wire(models.Left, [[[]]]), [[[]]])
                self.assertEqual(from_wire(models.SelfList, [[[]]]), [[[]]])
                self.assertIsInstance(from_wire(models.Children, [{'Name': 'root'}])[0], models.Tree)
            finally:
                sys.path.remove(temp)
                for name in list(sys.modules):
                    if name == package or name.startswith(package + '.'):
                        del sys.modules[name]

    def test_schema_discovery_includes_shared_parameters_and_response_headers(self):
        spec = {
            'swagger': '2.0', 'info': {'version': '1.0', 'title': 'Test'},
            'definitions': {},
            'parameters': {'Limit': {'name': 'limit', 'in': 'query', 'type': 'integer'}},
            'responses': {'Result': {
                'description': 'Result', 'schema': {'type': 'object', 'properties': {'Value': {'type': 'string'}}},
                'headers': {'X-Next': {'type': 'string'}},
            }},
            'paths': {'/test': {
                'parameters': [{'$ref': '#/parameters/Limit'}],
                'get': {'operationId': 'ListTest', 'responses': {'200': {'$ref': '#/responses/Result'}}},
                'post': {'operationId': 'CreateTest', 'parameters': [
                    {'name': 'limit', 'in': 'query', 'type': 'string'},
                    {'name': 'body', 'in': 'body', 'schema': {'type': 'object', 'properties': {}}},
                ], 'responses': {}},
            }},
        }
        schemas = SchemaDiscovery(spec).collect()
        self.assertNotIn('ListTestQueryLimit', schemas)
        self.assertNotIn('CreateTestQueryLimit', schemas)
        self.assertIn('CreateTestRequest', schemas)
        self.assertIn('ListTestResponse200', schemas)
        self.assertNotIn('ListTestResponse200HeaderXNext', schemas)

    def test_inline_request_response_and_parameter_types(self):
        from docker_python.versions.v_1_44.models import (
            ContainerCreateRequest, ContainerTopResponse200,
            HostConfig, MountType,
        )
        from docker_python.versions.v_1_44 import models
        from docker_python.versions.v_1_44.commands import ContainerListCommand
        from docker_python.core.parameters import Unset
        self.assertFalse(hasattr(models, 'ContainerListQueryAll'))
        self.assertEqual(get_type_hints(ContainerListCommand)['all'], bool | Unset)
        self.assertEqual(ContainerCreateRequest.__name__, 'ContainerCreateRequest')
        self.assertIn('memory', get_type_hints(HostConfig))
        request = ContainerCreateRequest.from_wire({
            'Image': 'alpine', 'HostConfig': {'Mounts': [{'Type': 'bind'}]},
        })
        self.assertEqual(request.image, 'alpine')
        self.assertIsInstance(request.host_config, HostConfig)
        self.assertIs(request.host_config.mounts[0].type, MountType.BIND)
        response = ContainerTopResponse200.from_wire({'Titles': ['PID'], 'Processes': [['42']]})
        self.assertEqual(response.titles, ['PID'])
        self.assertEqual(response.processes, [['42']])

    def test_nested_models_enums_aliases_and_wire_names(self):
        from docker_python.versions.v_1_44.models import (
            ContainerConfig, HostConfig, Mount, MountType, PortBinding, SystemVersion,
        )
        payload = {
            'Image': 'alpine',
            'HostConfig': {
                'Mounts': [{'Type': 'bind', 'Source': '/tmp', 'Target': '/data'}],
                'PortBindings': {'80/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '8080'}]},
            },
        }
        # HostConfig is supplied by the command as a sibling of ContainerConfig;
        # decode these schemas independently, as defined in Swagger.
        config = ContainerConfig.from_wire({'Image': payload['Image']})
        host = HostConfig.from_wire(payload['HostConfig'])
        self.assertEqual(config.image, 'alpine')
        self.assertIsInstance(host.mounts[0], Mount)
        self.assertIs(host.mounts[0].type, MountType.BIND)
        self.assertIsInstance(host.port_bindings['80/tcp'][0], PortBinding)
        self.assertEqual(host.to_wire(), payload['HostConfig'])
        version = SystemVersion.from_wire({'Platform': {'Name': 'Docker Engine'}, 'ApiVersion': '1.44'})
        self.assertEqual(version.platform.name, 'Docker Engine')
        self.assertEqual(version.api_version, '1.44')
        self.assertIsNone(version.min_api_version)

    def test_allof_required_and_enum_decoding(self):
        from docker_python.versions.v_1_44.models import ChangeType, MountPoint, Port
        from docker_python.versions.v_1_44.models import MountType
        mount = MountPoint.from_wire({'Type': 'volume', 'Name': 'data'})
        self.assertIs(mount.type, MountType.VOLUME)
        self.assertEqual(ChangeType(1).value, 1)
        with self.assertRaises(TypeError):
            Port()

    def test_generated_command_uses_complete_model(self):
        for version in ['1_40', '1_44', '1_55']:
            with self.subTest(version=version):
                api = import_module('docker_python.versions.v_' + version)
                models = import_module(api.__name__ + '.models')
                class FakeTransport:
                    def send(self, request):
                        return Response(200, {}, {'Version': '27.0', 'ApiVersion': '1.55', 'Platform': {'Name': 'Docker Engine'}})
                result = api.DockerClient(FakeTransport()).system_version().execute()
                self.assertIsInstance(result, models.SystemVersion)
                self.assertEqual(result.platform.name, 'Docker Engine')


if __name__ == '__main__':
    unittest.main()
