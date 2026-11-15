"""Walk Swagger operations once, resolving shared parameters and responses."""

import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, TypeVar, cast

from .models import class_name, primitive_annotation
from .swagger import PYTHON_NAME, PYTHON_TYPE, Operation, Parameter, Response, Schema, Swagger

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch"}


def pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[^a-zA-Z0-9]+", value) if part)


@dataclass(frozen=True)
class OperationDefinition:
    path: str
    method: str
    operation: Operation
    parameters: list[Parameter]
    responses: dict[str, Response]

    @property
    def name(self) -> str:
        return self.operation["operationId"]

    def parameter_model(self, parameter: Parameter) -> str:
        prefix = pascal(self.name)
        if parameter["in"] == "body":
            return prefix + "Request"
        return prefix + pascal(parameter["in"]) + pascal(parameter["name"])

    def response_model(self, status: str) -> str:
        return pascal(self.name) + "Response" + pascal(status)


def parameter_schema(parameter: Parameter) -> Schema:
    if parameter["in"] == "body":
        return parameter["schema"]
    return cast(
        Schema,
        {key: value for key, value in parameter.items() if key not in {"name", "in", "required"}},
    )


_DRT = TypeVar("_DRT", bound=Mapping[str, Any])


def _do_resolve(value: _DRT, spec: Swagger) -> _DRT:
    seen: set[str] = set()
    while "$ref" in value:
        ref = value["$ref"]
        if not ref.startswith("#/") or ref in seen:
            raise ValueError(f"Unsupported or cyclic Swagger reference: {ref}")
        seen.add(ref)
        target: Any = spec
        for token in ref[2:].split("/"):
            target = target[token.replace("~1", "/").replace("~0", "~")]
        value = target
    return value


@dataclass
class SchemaDiscovery:
    spec: Swagger

    def resolve(self, value: _DRT) -> _DRT:
        return _do_resolve(value, self.spec)

    def operations(self) -> Iterator[OperationDefinition]:
        seen = set()
        for path, path_item in self.spec["paths"].items():
            path_item = self.resolve(path_item)
            shared = path_item.get("parameters", [])
            for method, raw in path_item.items():
                if method not in HTTP_METHODS:
                    continue
                operation = self.resolve(cast(Operation, raw))
                if operation["operationId"] in seen:
                    raise ValueError(f"Duplicate operationId: {operation['operationId']}")
                seen.add(operation["operationId"])
                parameters = {}
                for raw_parameter in [*shared, *operation.get("parameters", [])]:
                    parameter = self.resolve(raw_parameter)
                    parameters[(parameter["name"], parameter["in"])] = parameter
                responses = {
                    str(status): self.resolve(response)
                    for status, response in operation["responses"].items()
                }
                yield OperationDefinition(
                    path,
                    method.upper(),
                    operation,
                    list(parameters.values()),
                    responses,
                )

    def normalize(self, schema: Schema) -> Schema:
        # A one-part allOf is commonly just a reference with a description.
        if "allOf" in schema and len(schema["allOf"]) == 1 and "properties" not in schema:
            overrides = schema.copy()
            overrides.pop("allOf")
            merged = schema["allOf"][0].copy()
            merged.update(overrides)
            return self.normalize(merged)
        return schema

    def reference_name(self, schema: Schema) -> str:
        ref = schema["$ref"]
        name = ref.removeprefix("#/definitions/")
        if not ref.startswith("#/definitions/") or name not in self.spec["definitions"]:
            raise ValueError(f"Unknown definition: {ref}")
        return name

    def annotation(self, name: str, schema: Schema) -> str:
        schema = self.normalize(schema)
        if PYTHON_TYPE in schema:
            annotation = "models." + schema[PYTHON_TYPE]
        elif "$ref" in schema:
            reference = self.reference_name(schema)
            target = self.spec["definitions"][reference]
            annotation = "models." + class_name(target.get(PYTHON_TYPE, target.get(PYTHON_NAME, reference)))
        elif schema.get("enum") or "properties" in schema or "allOf" in schema:
            annotation = "models." + class_name(name)
        elif schema.get("type") == "array":
            annotation = f"list[{self.annotation(name + 'Item', schema.get('items', {}))}]"
        elif schema.get("type") == "object" or "additionalProperties" in schema:
            value = schema.get("additionalProperties", {})
            item = self.annotation(name + "Value", value) if isinstance(value, dict) else "Any"
            annotation = f"dict[str, {item}]"
        else:
            annotation = primitive_annotation(schema)
        if schema.get("x-nullable") and annotation != "Any":
            annotation += " | None"
        return annotation

    def collect(self) -> dict[str, Schema]:
        # Preserve names explicitly defined by the API, including recursive aliases.
        schemas = dict(self.spec["definitions"])

        def add(name: str, schema: Schema) -> None:
            schema = self.normalize(schema)
            if PYTHON_TYPE in schema:
                return
            if "$ref" in schema:
                self.reference_name(schema)
            elif schema.get("enum") or "properties" in schema or "allOf" in schema:
                if name in schemas:
                    raise ValueError(f"Operation type name collides with another model: {name}")
                schemas[name] = schema
            elif schema.get("type") == "array":
                add(name + "Item", schema.get("items", {}))
            else:
                additional = schema.get("additionalProperties")
                if isinstance(additional, dict):
                    add(name + "Value", additional)

        for definition in self.operations():
            for parameter in definition.parameters:
                add(definition.parameter_model(parameter), parameter_schema(parameter))
            for status, response in definition.responses.items():
                name = definition.response_model(status)
                if "schema" in response:
                    add(name, response["schema"])
                for header, schema in response.get("headers", {}).items():
                    add(name + "Header" + pascal(header), schema)
        return schemas
