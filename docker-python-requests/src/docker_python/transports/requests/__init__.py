from dataclasses import dataclass, field
import json
from typing import Any
from urllib.parse import quote

import requests
from requests_unixsocket import UnixAdapter

from docker_python.core import Request, Response, ResponseStream
from docker_python.core.models import to_wire
from docker_python.core.parameters import UNSET


@dataclass
class RequestsTransport:
    base_url: str = 'http://localhost:2375'
    timeout: float | None = 60.0
    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self) -> None:
        if self.base_url.startswith('unix://'):
            socket_path = self.base_url.removeprefix('unix://')
            if not socket_path.startswith('/'):
                raise ValueError('Docker Unix socket path must be absolute')
            self.session.mount('http+unix://', UnixAdapter())
            self.session.trust_env = False
            self.base_url = 'http+unix://' + quote(socket_path, safe='')
        elif self.base_url.startswith('tcp://'):
            self.base_url = 'http://' + self.base_url.removeprefix('tcp://')

    def _send(self, request: Request, *, stream: bool = False) -> requests.Response:
        query = []
        for name, value in request.query.items():
            if value is None:
                continue
            format_ = request.query_formats.get(name)
            if isinstance(value, list) and format_:
                values = [json.dumps(item) if isinstance(item, bool) else str(item) for item in value]
                if format_ == 'multi':
                    query.extend((name, item) for item in values)
                    continue
                separators = {'csv': ',', 'ssv': ' ', 'tsv': '\t', 'pipes': '|'}
                value = separators[format_].join(values)
            elif isinstance(value, (dict, list, bool)):
                value = json.dumps(value)
            query.append((name, value))
        options: dict[str, Any] = {}
        if request.body is not UNSET:
            body = to_wire(request.body)
            if isinstance(body, (bytes, bytearray)) or hasattr(body, 'read'):
                options['data'] = body
            elif body is None:
                options['data'] = b'null'
            else:
                options['json'] = body
        if request.form:
            options['data'] = dict(request.form)
        if request.files:
            options['files'] = dict(request.files)
        result = self.session.request(
            request.method, self.base_url.rstrip('/') + request.path,
            params=query, headers=dict(request.headers), timeout=self.timeout,
            stream=stream, **options,
        )
        if result.status_code == 101:
            result.close()
            raise NotImplementedError('The requests transport does not support interactive HTTP upgrades or WebSockets')
        return result

    def send(self, request: Request) -> Response:
        result = self._send(request)
        try:
            if not result.content:
                payload = None
            elif 'json' in result.headers.get('Content-Type', ''):
                try:
                    payload = result.json()
                except ValueError:
                    payload = result.content  # NDJSON/build output: use stream() to consume incrementally.
            elif result.headers.get('Content-Type', '').startswith('text/'):
                payload = result.text
            else:
                payload = result.content
            return Response(result.status_code, dict(result.headers), payload)
        finally:
            result.close()

    def stream(self, request: Request) -> ResponseStream:
        result = self._send(request, stream=True)
        return ResponseStream(result.status_code, dict(result.headers),
                              result.iter_content(chunk_size=8192), result.close)

    def close(self) -> None:
        self.session.close()
