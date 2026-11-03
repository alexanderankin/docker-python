#!/usr/bin/env python3
import logging
from contextlib import closing
from time import perf_counter

from docker_python.core import DockerError, NotFoundError
from docker_python.transports.requests import RequestsTransport
from docker_python.versions.v_1_55 import DockerClient
from docker_python.versions.v_1_55.models import ContainerCreateRequest
from docker_python_examples.common import LOGGER, log_error, parser
from requests.exceptions import RequestException


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = parser('Wait for Alpine to sleep 5 seconds using Docker API 1.55.').parse_args()
    try:
        with closing(RequestsTransport(args.host)) as transport:
            client = DockerClient(transport)
            client.check_version()
            config = ContainerCreateRequest(image='alpine:latest', cmd=['sleep', '5'])
            try:
                container = client.container_create(body=config).execute()
            except NotFoundError:
                LOGGER.info('Pulling alpine:latest')
                with client.image_create(from_image='alpine', tag='latest').execute_stream() as pull:
                    for _ in pull:
                        pass
                container = client.container_create(body=config).execute()
            try:
                LOGGER.info('Created container: %s', container.id)
                started = perf_counter()
                client.container_start(id=container.id).execute()
                result = client.container_wait(id=container.id).execute()
                duration = perf_counter() - started
                LOGGER.info('Container finished after %.3f seconds', duration)
                LOGGER.info('Wait returned: %s', result)
            finally:
                client.container_delete(id=container.id, force=True).execute()
                LOGGER.info('Removed container: %s', container.id)
    except (DockerError, RequestException, ValueError) as error:
        return log_error(error)
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
