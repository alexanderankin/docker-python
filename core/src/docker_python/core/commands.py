"""Execution shared by generated commands; no dependency on generated versions."""
from dataclasses import dataclass, replace
import json
from typing import Any, ClassVar, Generic

from . import Client, RequestBuilder, Response, ResponseBuilder, ResponseStream, Result, T
from .models import to_wire
from .parameters import ParameterSpec, UNSET


@dataclass(frozen=True)
class Command(Generic[T]):
    client: Client
    METHOD: ClassVar[str]
    PATH: ClassVar[str]
    PARAMETERS: ClassVar[tuple[ParameterSpec, ...]] = ()
    CONTENT_TYPE: ClassVar[str | None] = None
    RESPONSE: ClassVar[ResponseBuilder[Any]]

    def build_request(self) -> RequestBuilder:
        request = RequestBuilder(self.METHOD, self.PATH)
        formats = {}
        for parameter in self.PARAMETERS:
            value = getattr(self, parameter.attribute)
            if value is UNSET:
                if parameter.required:
                    raise ValueError(f"Missing required parameter: {parameter.name}")
                continue
            location, name = parameter.location, parameter.name
            if location == 'path':
                if value is None:
                    raise ValueError(f"Path parameter cannot be null: {name}")
                request = request.with_path(name, str(to_wire(value)))
            elif location == 'query':
                request = request.with_query(**{name: to_wire(value)})
                if parameter.collection_format:
                    formats[name] = parameter.collection_format
            elif location == 'header':
                request = request.with_headers(**{name: str(to_wire(value))})
            elif location == 'body':
                request = request.with_body(value)
            elif location == 'formData':
                request = (request.with_files if parameter.is_file else request.with_form)(**{name: to_wire(value)})
            else:
                raise ValueError(f"Unsupported parameter location: {location}")
        if self.CONTENT_TYPE and request.body is not UNSET:
            if not any(name.lower() == 'content-type' for name in request.headers):
                request = request.with_headers(**{'Content-Type': self.CONTENT_TYPE})
        return replace(request, query_formats=formats)

    def execute(self) -> T:
        return self.client.execute(self.build_request(), self.RESPONSE)

    def execute_response(self) -> Result[T]:
        request = self.build_request().build(self.client.version)
        return self.RESPONSE.build_result(self.client.transport.send(request))

    def execute_stream(self) -> ResponseStream:
        send_stream = getattr(self.client.transport, 'stream', None)
        if send_stream is None:
            raise TypeError('This transport does not support streaming responses')
        stream = send_stream(self.build_request().build(self.client.version))
        if stream.status not in self.RESPONSE.statuses:
            try:
                body = b''.join(stream)
                try:
                    body = json.loads(body)
                except (ValueError, UnicodeDecodeError):
                    pass
                self.RESPONSE.build(Response(stream.status, stream.headers, body))
            finally:
                stream.close()
        return stream
