from dataclasses import dataclass, field, replace
from typing import Any, Callable, Generic, Iterator, Mapping, Protocol, TypeVar

from .parameters import UNSET
from urllib.parse import quote

T = TypeVar("T")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: Mapping[str, Any] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    body: Any = UNSET
    form: Mapping[str, Any] = field(default_factory=dict)
    files: Mapping[str, Any] = field(default_factory=dict)
    query_formats: Mapping[str, str] = field(default_factory=dict)


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


class BadRequestError(DockerError):
    pass


class UnauthorizedError(DockerError):
    pass


class ForbiddenError(DockerError):
    pass


class NotFoundError(DockerError):
    pass


class ConflictError(DockerError):
    pass


class ServerError(DockerError):
    pass


class UnavailableError(ServerError):
    pass


ERROR_TYPES = {
    400: BadRequestError, 401: UnauthorizedError, 403: ForbiddenError,
    404: NotFoundError, 409: ConflictError, 500: ServerError, 503: UnavailableError,
}


@dataclass(frozen=True)
class Result(Generic[T]):
    status: int
    headers: Mapping[str, str]
    body: T


@dataclass
class ResponseStream:
    status: int
    headers: Mapping[str, str]
    chunks: Iterator[bytes]
    close: Callable[[], None]

    def __iter__(self) -> Iterator[bytes]:
        return self.chunks

    def __enter__(self) -> "ResponseStream":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


@dataclass(frozen=True)
class ResponseBuilder(Generic[T]):
    decode: Callable[[Any], T]
    statuses: tuple[int, ...] = (200,)
    errors: Mapping[int, type[DockerError]] = field(default_factory=dict)
    decoders: Mapping[int, Callable[[Any], T]] = field(default_factory=dict)
    error_decoders: Mapping[int, Callable[[Any], Any]] = field(default_factory=dict)
    default_error_decoder: Callable[[Any], Any] = lambda body: body

    def build(self, response: Response) -> T:
        if response.status not in self.statuses:
            decoder = self.error_decoders.get(response.status, self.default_error_decoder)
            try:
                body = decoder(response.body)
            except (TypeError, ValueError, KeyError):
                body = response.body  # Preserve malformed error responses, too.
            error = replace(response, body=body)
            raise self.errors.get(response.status, ERROR_TYPES.get(response.status, DockerError))(error)
        return self.decoders.get(response.status, self.decode)(response.body)

    def build_result(self, response: Response) -> Result[T]:
        return Result(response.status, response.headers, self.build(response))


@dataclass(frozen=True)
class RequestBuilder:
    method: str
    path: str
    query: Mapping[str, Any] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    body: Any = UNSET
    form: Mapping[str, Any] = field(default_factory=dict)
    files: Mapping[str, Any] = field(default_factory=dict)
    query_formats: Mapping[str, str] = field(default_factory=dict)

    def with_path(self, name: str, value: str) -> "RequestBuilder":
        return replace(self, path=self.path.replace("{" + name + "}", quote(value, safe="")))

    def with_query(self, **values: Any) -> "RequestBuilder":
        return replace(self, query={**self.query, **values})

    def with_headers(self, **values: str) -> "RequestBuilder":
        return replace(self, headers={**self.headers, **values})

    def with_body(self, body: Any) -> "RequestBuilder":
        return replace(self, body=body)

    def with_form(self, **values: Any) -> "RequestBuilder":
        return replace(self, form={**self.form, **values})

    def with_files(self, **values: Any) -> "RequestBuilder":
        return replace(self, files={**self.files, **values})

    def build(self, version: str) -> Request:
        if "{" in self.path or "}" in self.path:
            raise ValueError(f"Unresolved path parameters: {self.path}")
        return Request(self.method, f"/v{version}{self.path}", self.query, self.headers,
                       self.body, self.form, self.files, self.query_formats)


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
