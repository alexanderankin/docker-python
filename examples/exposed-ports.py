#!/usr/bin/env python3
"""Inspect the generated ExposedPorts map and its JSON without running Docker."""
import json
import logging

from docker_python.versions.v_1_55.models.container_create_request import (
    ContainerCreateRequest,
    ContainerCreateRequestExposedPortsValue,
)
from docker_python_examples.common import LOGGER


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Docker's JSON shape is {"80/tcp": {}, "443/tcp": {}, "53/udp": {}}.
    # The Swagger enum containing only {} becomes this generated EMPTY member.
    exposed_ports: dict[str, ContainerCreateRequestExposedPortsValue] = {
        '80/tcp': ContainerCreateRequestExposedPortsValue.EMPTY,
        '443/tcp': ContainerCreateRequestExposedPortsValue.EMPTY,
        '53/udp': ContainerCreateRequestExposedPortsValue.EMPTY,
    }
    container = ContainerCreateRequest(
        image='alpine:latest',
        exposed_ports=exposed_ports,
    )
    LOGGER.info('Python ExposedPorts map: %s', container.exposed_ports)

    # Equivalent to the JSON object docker-java's ExposedPorts.toPrimitive() produces.
    payload = json.dumps(container.to_wire(), indent=2)
    LOGGER.info('Docker JSON:\n%s', payload)

    # from_wire() maps each empty object back to the generated enum member.
    restored = ContainerCreateRequest.from_wire(json.loads(payload))
    LOGGER.info('Decoded ExposedPorts map: %s', restored.exposed_ports)
    LOGGER.info('Round-trip preserves the model: %s', restored == container)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
