#!/usr/bin/env python3
"""Round-trip custom dataclasses through Docker JSON, without running Docker."""
import json
import logging

from docker_python.versions.v_1_55.models import (
    ContainerCreateRequest,
    ExposedPort,
    ExposedPorts,
)
from docker_python_examples.common import LOGGER


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    container = ContainerCreateRequest(
        image='alpine:latest',
        exposed_ports=ExposedPorts((ExposedPort(80), ExposedPort(443), ExposedPort(53, 'udp'))),
    )
    LOGGER.info('Python model: %s', container.exposed_ports)
    payload = json.dumps(container.to_wire(), indent=2)
    LOGGER.info('Docker JSON:\n%s', payload)
    restored = ContainerCreateRequest.from_wire(json.loads(payload))
    LOGGER.info('Decoded model: %s', restored.exposed_ports)
    LOGGER.info('Round-trip preserves the model: %s', restored == container)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
