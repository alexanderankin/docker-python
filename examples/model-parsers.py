#!/usr/bin/env python3
"""Build container-create JSON from typed model parsers, without running Docker."""

import json
import logging

from docker_python.versions.v_1_55.models import (
    Bind,
    Binds,
    ContainerCreateRequest,
    Device,
    ExposedPort,
    ExposedPorts,
    HostConfig,
    InternetProtocol,
    Link,
    Links,
    PortBinding,
    Ports,
    RestartPolicy,
    Volume,
    Volumes,
    VolumesFrom,
)
from docker_python_examples.common import LOGGER


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    request = ContainerCreateRequest(
        image="alpine:latest",
        exposed_ports=ExposedPorts(
            (ExposedPort.parse("80/TCP"), ExposedPort(53, InternetProtocol.UDP))
        ),
        volumes=Volumes((Volume.parse("/data"),)),
        host_config=HostConfig(
            binds=Binds((Bind.parse("/tmp/example:/data:ro"),)),
            links=Links((Link.parse("database:db"),)),
            volumes_from=[VolumesFrom.parse("other-container:ro")],
            port_bindings=Ports.from_bindings(
                PortBinding.parse("127.0.0.1:8080:80/tcp")
            ),
            devices=[Device.parse("/dev/null:/dev/example:rw")],
            restart_policy=RestartPolicy.parse("on-failure:3"),
        ),
    )
    payload = json.dumps(request.to_wire(), indent=2)
    LOGGER.info("Container-create JSON:\n%s", payload)
    restored = ContainerCreateRequest.from_wire(json.loads(payload))
    LOGGER.info("Round-trip preserves the model: %s", restored == request)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
