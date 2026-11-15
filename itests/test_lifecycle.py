import json
import time
from contextlib import suppress
from typing import Callable
from uuid import uuid4

import pytest

from docker_python.core import NotFoundError
from docker_python.versions.v_1_44 import DockerClient
from docker_python.versions.v_1_44.models import (
    ContainerInspectResponse200,
    ContainerStateStatus,
    ContainerWaitResponse,
    ErrorResponse,
    VolumeCreateOptions,
)


def test_container_run_wait_logs_and_remove(
        client: DockerClient,
        create_container: Callable[[list[str]], str],
        windows_daemon: bool,
) -> None:
    message = 'docker-python-integration-test'
    cmd = (
        ['cmd', '/S', '/C', f'echo {message} & exit /B 17']
        if windows_daemon else
        ['sh', '-c', f'echo {message}; exit 17']
    )
    container_id = create_container(cmd)
    container = client.container_inspect(id=container_id).execute()
    assert isinstance(container, ContainerInspectResponse200)
    assert container.state
    assert container.state.status == ContainerStateStatus.CREATED
    containers = client.container_list().with_all(True).with_filters(
        json.dumps({'id': [container_id]}),
    ).execute()
    assert [container.id for container in containers] == [container_id]

    client.container_start(id=container_id).execute()
    result = client.container_wait(id=container_id).execute()
    assert isinstance(result, ContainerWaitResponse)
    assert result.status_code == 17
    assert client.container_inspect(id=container_id).execute().state.status == ContainerStateStatus.EXITED
    # Docker's log framing is retained by the transport; the payload is still present.
    with client.container_logs(id=container_id, stdout=True, stderr=True).execute_stream() as stream:
        assert message.encode() in b''.join(stream)

    client.container_delete(id=container_id).execute()
    with pytest.raises(NotFoundError) as error:
        client.container_inspect(id=container_id).execute()
    assert error.value.response.status == 404
    assert isinstance(error.value.response.body, ErrorResponse)


def wait_until(predicate, timeout: int = 15, interval: float | int = 0.1) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(interval)
    pytest.fail(f"Condition not met within {timeout}s")


def test_container_start_stop_and_restart(
        client: DockerClient,
        create_container: Callable[[list[str]], str],
        windows_daemon: bool,
) -> None:
    cmd = ['cmd', '/S', '/C', 'ping -t 127.0.0.1 >NUL'] if windows_daemon else ['sleep', '300']
    container_id = create_container(cmd)

    def is_running():
        return client.container_inspect(id=container_id).execute().state.running

    client.container_start(id=container_id).execute()
    wait_until(lambda: is_running())

    client.container_stop(id=container_id, t=1).execute()
    wait_until(lambda: not is_running())

    client.container_start(id=container_id).execute()
    wait_until(lambda: is_running())

    client.container_restart(id=container_id, t=1).execute()
    wait_until(lambda: is_running())

    client.container_delete(id=container_id, force=True).execute()

    def is_deleted():
        try:
            client.container_inspect(id=container_id).execute()
            return False
        except NotFoundError:
            return True

    wait_until(is_deleted)


def test_volume_create_inspect_list_and_remove(client: DockerClient):
    name = f'docker-python-itest-{uuid4().hex}'
    labels = {'docker-python-itest': name}
    volume = client.volume_create().with_volume_config(VolumeCreateOptions(name=name, labels=labels)).execute()
    try:
        assert volume.name == name
        assert volume.labels == labels
        assert client.volume_inspect(name=name).execute().labels == labels
        volumes = client.volume_list(filters=json.dumps({'name': [name]})).execute()
        assert volumes.volumes
        assert [volume.name for volume in volumes.volumes] == [name]
        client.volume_delete(name=name).execute()

        def exists() -> bool:
            r = client.volume_list(filters=json.dumps({'name': [name]})).execute()
            assert r.volumes is not None
            return len(r.volumes) != 0

        wait_until(lambda: not exists(), 10, 0.5)
        with pytest.raises(NotFoundError):
            client.volume_inspect(name=name).execute()
    finally:
        with suppress(NotFoundError):
            client.volume_delete(name=name, force=True).execute()
