#!/usr/bin/env python3
from contextlib import closing

from docker_python.core import DockerError
from docker_python.transports.requests import RequestsTransport
from docker_python.versions.v_1_55 import DockerClient
from docker_python_examples.common import LOGGER, configure_logging, log_error, parser
from requests.exceptions import RequestException


def main() -> int:
    configure_logging()
    args = parser('List networks using Docker API 1.55.').parse_args()
    try:
        with closing(RequestsTransport(args.host)) as transport:
            client = DockerClient(transport)
            client.check_version()
            for network in client.list_networks().execute():
                LOGGER.info('%s', network)
    except (DockerError, RequestException, ValueError) as error:
        return log_error(error)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
