from importlib import import_module
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import get_type_hints
import unittest

from docker_python.core import Response
from docker_python.core.models import to_wire
from docker_python.core.parameters import Unset
from docker_python_generator.clean import clean
from docker_python_generator.commands import CommandGenerator
from docker_python_generator.discovery import SchemaDiscovery
from docker_python_generator.models import ModelGenerator


class GenerationCleanupTests(unittest.TestCase):
    def test_clean_only_removes_generated_model_and_command_directories(self):
        with TemporaryDirectory() as temp:
            version = Path(temp) / 'v1.55'
            package = version / 'src/docker_python/versions/v_1_55'
            for relative in ['models/item.py', 'commands/operation.py', 'client.py', '__init__.py']:
                path = package / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('')
            (version / 'pyproject.toml').write_text('[project]\nname = "example"\n')
            clean(version)
            self.assertFalse((package / 'models').exists())
            self.assertFalse((package / 'commands').exists())
            self.assertTrue((package / 'client.py').exists())
            self.assertTrue((package / '__init__.py').exists())
            self.assertTrue((version / 'pyproject.toml').exists())
            clean(version)  # Repeated cleaning is harmless.

    def test_generation_prunes_obsolete_generated_alias_files(self):
        with TemporaryDirectory() as temp:
            output = Path(temp)
            ModelGenerator({'OldAlias': {'type': 'boolean'}}).generate(output)
            custom = output / 'custom.py'
            custom.write_text('# Handwritten helper\n')
            ModelGenerator({}).generate(output)
            self.assertFalse((output / 'old_alias.py').exists())
            self.assertTrue(custom.exists())

    def test_collections_inline_but_nested_dataclasses_and_enums_remain_typed(self):
        spec = {
            'swagger': '2.0', 'info': {'version': '1.0', 'title': 'Test'},
            'definitions': {'NamedTags': {'type': 'array', 'items': {'type': 'string'}}},
            'paths': {'/echo': {'post': {
                'operationId': 'Echo', 'parameters': [
                    {'name': 'tags', 'in': 'query', 'type': 'array', 'items': {'type': 'string'}},
                    {'name': 'mode', 'in': 'query', 'type': 'string', 'enum': ['fast', 'slow']},
                    {'name': 'body', 'in': 'body', 'required': True, 'schema': {
                        'type': 'array', 'items': {'type': 'object', 'properties': {'Name': {'type': 'string'}}},
                    }},
                ], 'responses': {'200': {'description': 'Result', 'schema': {
                    'type': 'array', 'items': {'type': 'object', 'properties': {'Value': {'type': 'string'}}},
                }}},
            }}},
        }
        with TemporaryDirectory() as temp:
            output = Path(temp) / 'inline_types_test'
            discovery = SchemaDiscovery(spec)
            ModelGenerator(discovery.collect()).generate(output / 'models')
            CommandGenerator(spec).generate(output)
            self.assertFalse((output / 'models/echo_query_tags.py').exists())
            self.assertFalse((output / 'models/echo_response200.py').exists())
            sys.path.insert(0, temp)
            try:
                api = import_module('inline_types_test')
                models = import_module('inline_types_test.models')
                commands = import_module('inline_types_test.commands')
                self.assertEqual(models.NamedTags, list[str])
                self.assertEqual(get_type_hints(commands.EchoCommand)['tags'], list[str] | Unset)
                self.assertEqual(get_type_hints(commands.EchoCommand)['mode'], models.EchoQueryMode | Unset)
                class Transport:
                    def send(self, request):
                        self.body = to_wire(request.body)
                        return Response(200, {}, [{'Value': 'returned'}])
                transport = Transport()
                result = api.DockerClient(transport).echo(
                    body=[models.EchoRequestItem(name='sent')], tags=['one', 'two'],
                ).execute()
                self.assertEqual(transport.body, [{'Name': 'sent'}])
                self.assertIsInstance(result[0], models.EchoResponse200Item)
                self.assertEqual(result[0].value, 'returned')
            finally:
                sys.path.remove(temp)
                for name in list(sys.modules):
                    if name == 'inline_types_test' or name.startswith('inline_types_test.'):
                        del sys.modules[name]


if __name__ == '__main__':
    unittest.main()
