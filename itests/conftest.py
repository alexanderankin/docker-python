import sys
from contextlib import closing, suppress
from typing import Any, Callable, Generator
from uuid import uuid4

import pytest
from docker_python.core import NotFoundError
from docker_python.transports.requests import RequestsTransport
from docker_python.versions.v_1_44 import DockerClient
from docker_python.versions.v_1_44.models import (
    ContainerCreateRequest,
    HostConfig,
    HostConfigLogConfig,
    HostConfigLogConfigType,
)


@pytest.fixture(scope='session')
def client() -> Generator[DockerClient, Any, None]:
    host = 'npipe:////./pipe/docker_engine' if sys.platform == 'win32' else 'unix:///var/run/docker.sock'
    with closing(RequestsTransport(host, timeout=300)) as transport:
        client = DockerClient(transport)
        assert client.check_version() == '1.44'
        yield client


@pytest.fixture(scope='session')
def windows_daemon(client: DockerClient) -> bool:
    return client.system_info().execute().os_type == 'windows'


@pytest.fixture(scope='session')
def image(client: DockerClient, windows_daemon: bool) -> str:
    image = 'mcr.microsoft.com/windows/nanoserver:ltsc2022' if windows_daemon else 'alpine:3.21'
    try:
        client.image_inspect(name=image).execute()
    except NotFoundError:
        with client.image_create(from_image=image).execute_stream() as stream:
            for _ in stream:
                pass
        # Pull failures can arrive in a successful HTTP stream; confirm the image exists.
        client.image_inspect(name=image).execute()
    return image


@pytest.fixture
def create_container(client: DockerClient, image: str, request: pytest.FixtureRequest) -> Callable[[list[str]], str]:
    def create(cmd):
        container = client.container_create().with_name(f'docker-python-itest-{uuid4().hex}').with_body(
            ContainerCreateRequest(
                image=image,
                cmd=cmd,
                # Keep log retrieval independent of the daemon's default logging driver.
                host_config=HostConfig(log_config=HostConfigLogConfig(type=HostConfigLogConfigType.JSON_FILE)),
            ),
        ).execute()

        def cleanup():
            with suppress(NotFoundError):
                client.container_delete(id=container.id, force=True).execute()

        request.addfinalizer(cleanup)
        return container.id

    return create
