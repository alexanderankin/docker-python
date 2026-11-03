import logging
from contextlib import closing
from importlib import import_module

from docker_python.core import DockerError
from docker_python.transports.requests import RequestsTransport
from requests.exceptions import RequestException

from .common import LOGGER, log_error, parser

API_VERSIONS = ('v_1_40', 'v_1_44', 'v_1_55')


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    argument_parser = parser('Run basic Docker commands with a selected generated API package.')
    argument_parser.add_argument('--api-version', choices=API_VERSIONS, default='v_1_55')
    commands = argument_parser.add_subparsers(dest='command', required=True)
    images = commands.add_parser('images', help='List images')
    images.add_argument('--all', action='store_true', help='Include intermediate images')
    ps = commands.add_parser('ps', help='List running containers')
    ps.add_argument('--all', action='store_true', help='Include stopped containers')
    network = commands.add_parser('network', help='Manage networks')
    network.add_subparsers(dest='network_command', required=True).add_parser('ls', help='List networks')
    args = argument_parser.parse_args()

    api = import_module(f'docker_python.versions.{args.api_version}')
    try:
        with closing(RequestsTransport(args.host)) as transport:
            client = api.DockerClient(transport)
            client.check_version()
            if args.command == 'images':
                operation = client.list_images().with_all(args.all)
            elif args.command == 'ps':
                operation = client.list_containers().with_all(args.all)
            else:
                operation = client.list_networks()
            for model in operation.execute():
                LOGGER.info('%s', model)
    except (DockerError, RequestException, ValueError) as error:
        return log_error(error)
    return 0
