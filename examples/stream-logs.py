#!/usr/bin/env python3
import logging
from collections.abc import Iterable, Iterator
from contextlib import closing

from docker_python.core import DockerError, NotFoundError
from docker_python.transports.requests import RequestsTransport
from docker_python.versions.v_1_55 import DockerClient
from docker_python.versions.v_1_55.models import ContainerCreateRequest
from docker_python_examples.common import LOGGER, log_error, parser
from requests.exceptions import RequestException


def lines(chunks: Iterable[bytes]) -> Iterator[str]:
    pending = b''
    for chunk in chunks:
        pending += chunk
        while b'\n' in pending:
            line, pending = pending.split(b'\n', 1)
            yield line.rstrip(b'\r').decode('utf-8')


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = parser('Stream 30 Alpine log lines using Docker API 1.55, then clean up.').parse_args()
    try:
        with closing(RequestsTransport(args.host)) as transport:
            client = DockerClient(transport)
            client.check_version()
            config = ContainerCreateRequest(
                image='alpine:latest',
                cmd=['sh', '-c', 'for i in $(seq 1 1000); do sleep 1; echo "it is now $(date)"; done'],
                tty=True,  # Plain log bytes, without Docker's stdout/stderr frame headers.
            )
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
                client.container_start(id=container.id).execute()
                with client.container_logs(
                    id=container.id, follow=True, stdout=True, stderr=True,
                ).execute_stream() as stream:
                    for count, line in enumerate(lines(stream), start=1):
                        LOGGER.info(f"new log line: {line}")
                        if count == 30:
                            break
            finally:
                try:
                    client.container_stop(id=container.id, t=2).execute()
                except DockerError as error:
                    if error.response.status != 304:  # Already stopped, or never started.
                        raise
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
