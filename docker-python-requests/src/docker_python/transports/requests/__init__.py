from dataclasses import dataclass, field
from typing import Any
import json
import requests
from requests_unixsocket import UnixAdapter
from urllib.parse import quote
from docker_python.core import Request, Response
from docker_python.core.models import to_wire


@dataclass
class RequestsTransport:
    base_url: str = "http://localhost:2375"
    timeout: float = 60.0
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

    def send(self, request: Request) -> Response:
        query = {
            key: json.dumps(value) if isinstance(value, (dict, list, bool)) else value
            for key, value in request.query.items() if value is not None
        }
        body: Any = to_wire(request.body)
        result = self.session.request(
            request.method, self.base_url.rstrip("/") + request.path,
            params=query, headers=request.headers, json=body, timeout=self.timeout,
        )
        payload = result.json() if result.content and "json" in result.headers.get("Content-Type", "") else result.text
        return Response(result.status_code, dict(result.headers), payload)

    def close(self) -> None:
        self.session.close()
