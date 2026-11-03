from dataclasses import dataclass, field, replace
from typing import Any, Callable, Generic, Mapping, Protocol, TypeVar
from urllib.parse import quote

T = TypeVar("T")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: Mapping[str, Any] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    body: Any = None


@dataclass(frozen=True)
class Response:
    status: int
    headers: Mapping[str, str]
    body: Any = None


class Transport(Protocol):
    def send(self, request: Request) -> Response: ...


class DockerError(RuntimeError):
    def __init__(self, response: Response):
        self.response = response
        super().__init__(f"Docker returned {response.status}: {response.body}")


@dataclass(frozen=True)
class ResponseBuilder(Generic[T]):
    decode: Callable[[Any], T]
    statuses: tuple[int, ...] = (200,)
    errors: Mapping[int, type[DockerError]] = field(default_factory=dict)

    def build(self, response: Response) -> T:
        if response.status not in self.statuses:
            raise self.errors.get(response.status, DockerError)(response)
        return self.decode(response.body)


@dataclass(frozen=True)
class RequestBuilder:
    method: str
    path: str
    query: Mapping[str, Any] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    body: Any = None

    def with_path(self, name: str, value: str) -> "RequestBuilder":
        return replace(self, path=self.path.replace("{" + name + "}", quote(value, safe="")))

    def with_query(self, **values: Any) -> "RequestBuilder":
        return replace(self, query={**self.query, **values})

    def with_headers(self, **values: str) -> "RequestBuilder":
        return replace(self, headers={**self.headers, **values})

    def with_body(self, body: Any) -> "RequestBuilder":
        return replace(self, body=body)

    def build(self, version: str) -> Request:
        return Request(self.method, f"/v{version}{self.path}", self.query, self.headers, self.body)


def agree_version(requested: str, server_max: str, server_min: str) -> str:
    def parts(value: str) -> tuple[int, ...]:
        return tuple(map(int, value.split(".")))
    if not parts(server_min) <= parts(requested) <= parts(server_max):
        raise ValueError(f"API {requested} is outside daemon range {server_min}..{server_max}")
    return requested


@dataclass
class Client:
    transport: Transport
    version: str

    def execute(self, request: RequestBuilder, response: ResponseBuilder[T]) -> T:
        return response.build(self.transport.send(request.build(self.version)))

    def check_version(self) -> str:
        response = self.transport.send(Request("GET", "/version"))
        data = ResponseBuilder(lambda body: body).build(response)
        return agree_version(self.version, data["ApiVersion"], data["MinAPIVersion"])
