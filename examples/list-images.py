#!/usr/bin/env python3
from contextlib import closing

from docker_python.core import DockerError
from docker_python.transports.requests import RequestsTransport
from docker_python.versions.v_1_44 import DockerClient
from docker_python_examples.common import LOGGER, configure_logging, log_error, parser
from requests.exceptions import RequestException


def main() -> int:
    configure_logging()
    argument_parser = parser('List images using Docker API 1.44.')
    argument_parser.add_argument('--all', action='store_true', help='Include intermediate images')
    args = argument_parser.parse_args()
    try:
        with closing(RequestsTransport(args.host)) as transport:
            client = DockerClient(transport)
            client.check_version()
            for image in client.list_images().with_all(args.all).execute():
                LOGGER.info('%s', image)
    except (DockerError, RequestException, ValueError) as error:
        return log_error(error)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
