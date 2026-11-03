"""Emit dataclasses for objects, enums for enumerations, and collection aliases."""
import ast
from dataclasses import dataclass, field
import keyword
from pathlib import Path
import re

from .swagger import Schema

GENERATED = '# Generated from Docker Engine Swagger; regenerate via docker_python_generator.\n'


def snake(name: str) -> str:
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    name = re.sub(r'\W', '_', name).lower()
    if not name or name[0].isdigit():
        name = '_' + name
    return name + '_' if keyword.iskeyword(name) else name


def class_name(name: str) -> str:
    result = re.sub(r'\W', '_', name)
    return '_' + result if result[0].isdigit() else result


def runtime_alias(annotation: str, references: set[str]) -> str:
    """Aliases execute immediately, so their external names need ForwardRefs."""
    symbols = {class_name(name) for name in references}

    class DeferReferences(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name):
            if node.id in symbols:
                return ast.Call(
                    func=ast.Name(id='ForwardRef', ctx=ast.Load()),
                    args=[ast.Constant(node.id)],
                    keywords=[ast.keyword(arg='module', value=ast.Name(id='__name__', ctx=ast.Load()))],
                )
            return node

    tree = DeferReferences().visit(ast.parse(annotation, mode='eval'))
    return ast.unparse(ast.fix_missing_locations(tree))


@dataclass
class ModelGenerator:
    definitions: dict[str, Schema]
    blocks: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    references: set[str] = field(default_factory=set)
    current_model: str = ""

    def flatten(self, schema: Schema, seen: frozenset[str] = frozenset()) -> Schema:
        if '$ref' in schema:
            name = schema['$ref'].removeprefix('#/definitions/')
            if name in seen:
                raise ValueError(f'Cyclic allOf reference: {name}')
            return self.flatten(self.definitions[name], seen | {name})
        result: Schema = {key: value for key, value in schema.items() if key != 'allOf'}
        properties = dict(schema.get('properties', {}))
        required = list(schema.get('required', []))
        for part in schema.get('allOf', []):
            parent = self.flatten(part, seen)
            result = {**parent, **result}
            properties = {**parent.get('properties', {}), **properties}
            required.extend(parent.get('required', []))
        if properties or 'properties' in schema:
            result['properties'] = properties
            result['required'] = list(dict.fromkeys(required))
        return result

    def annotation(self, schema: Schema, name: str) -> str:
        if 'allOf' in schema:
            if len(schema['allOf']) == 1 and 'properties' not in schema:
                merged = {**schema['allOf'][0], **{key: value for key, value in schema.items() if key != 'allOf'}}
                return self.annotation(merged, name)
            schema = self.flatten(schema)
        if name in self.definitions and name != self.current_model:
            name += "Value"
        if '$ref' in schema:
            ref = schema['$ref'].removeprefix('#/definitions/')
            if ref not in self.definitions:
                raise ValueError(f'Unknown definition: {ref}')
            self.references.add(ref)
            annotation = class_name(ref)
        elif schema.get('enum'):
            self.emit_enum(name, schema)
            annotation = name
        elif 'properties' in schema or 'allOf' in schema:
            self.emit_object(name, self.flatten(schema))
            annotation = name
        elif schema.get('type') == 'array':
            annotation = f'list[{self.annotation(schema.get("items", {}), name + "Item")}]'
        elif schema.get('type') == 'object' or 'additionalProperties' in schema:
            value = schema.get('additionalProperties', {})
            annotation = 'dict[str, ' + (self.annotation(value, name + 'Value') if isinstance(value, dict) else 'Any') + ']'
        else:
            annotation = {'string': 'bytes' if schema.get('format') == 'binary' else 'str', 'file': 'bytes', 'integer': 'int', 'number': 'float', 'boolean': 'bool'}.get(schema.get('type', ''), 'Any')
        if schema.get('x-nullable') and annotation != 'Any':
            annotation += ' | None'
        return annotation

    def emit_enum(self, name: str, schema: Schema) -> None:
        values = schema['enum']
        base = 'str, Enum' if all(isinstance(v, str) for v in values) else 'IntEnum' if all(type(v) is int for v in values) else 'Enum'
        lines = [f'class {name}({base}):']
        used: set[str] = set()
        for index, value in enumerate(values):
            member = snake(str(value)).upper().strip('_') or 'EMPTY'
            if member[0].isdigit():
                member = 'VALUE_' + member
            if member in used:
                member += '_' + str(index)
            used.add(member)
            lines.append(f'    {member} = {value!r}')
        self.blocks.append('\n'.join(lines))
        self.exports.append(name)

    def emit_object(self, name: str, schema: Schema) -> None:
        lines = ['@dataclass(kw_only=True)', f'class {name}(Model):']
        required = set(schema.get('required', []))
        used: set[str] = set()
        for wire, prop in schema.get('properties', {}).items():
            attr = snake(wire)
            if attr in used:
                raise ValueError(f'Field name collision in {name}: {wire}')
            used.add(attr)
            annotation = self.annotation(prop, name + class_name(wire))
            optional = wire not in required
            if optional and annotation != 'Any' and not annotation.endswith(' | None'):
                annotation += ' | None'
            default = 'default=None, ' if optional else ''
            lines.append(f'    {attr}: {annotation} = field({default}metadata={{"wire_name": {wire!r}}})')
        if len(lines) == 2:
            lines.append('    pass')
        self.blocks.append('\n'.join(lines))
        self.exports.append(name)

    def generate(self, output: Path) -> None:
        output.mkdir(parents=True, exist_ok=True)
        all_exports: list[tuple[str, list[str]]] = []
        for name, schema in self.definitions.items():
            self.blocks, self.exports, self.references = [], [], set()
            symbol = class_name(name)
            self.current_model = name
            annotation = self.annotation(schema, symbol)
            is_alias = symbol not in self.exports
            if is_alias:
                if self.references:
                    runtime = runtime_alias(annotation, self.references)
                    self.blocks.append(
                        f'if TYPE_CHECKING:\n    {symbol}: TypeAlias = {annotation}\n'
                        f'else:\n    {symbol} = {runtime}'
                    )
                else:
                    self.blocks.append(f'{symbol}: TypeAlias = {annotation}')
                self.exports.append(symbol)
            imports = [GENERATED.rstrip(), 'from __future__ import annotations', '',
                       'from dataclasses import dataclass, field', 'from enum import Enum, IntEnum',
                       'from typing import Any, TYPE_CHECKING, TypeAlias, ForwardRef', 'from docker_python.core.models import Model']
            if self.references:
                imports.extend(['', 'if TYPE_CHECKING:'])
                imports.extend(f'    from .{snake(ref)} import {class_name(ref)}' for ref in sorted(self.references))
            text = '\n'.join(imports) + '\n\n\n' + '\n\n\n'.join(self.blocks) + '\n'
            (output / (snake(name) + '.py')).write_text(text)
            all_exports.append((snake(name), list(self.exports)))
        exports = [symbol for _, symbols in all_exports for symbol in symbols]
        if len(exports) != len(set(exports)):
            raise ValueError('Generated model names collide')
        init = GENERATED + ''.join(f'from .{module} import {", ".join(symbols)}\n' for module, symbols in all_exports)
        init += '\n__all__ = ' + repr(exports) + '\n'
        init += '\nfrom docker_python.core.models import bind_model_namespace as _bind_model_namespace\n'
        init += f'_bind_model_namespace(__name__, {[module for module, _ in all_exports]!r}, __all__)\n'

        (output / '__init__.py').write_text(init)
