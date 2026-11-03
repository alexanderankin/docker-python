import argparse
import logging
import os

from docker_python.core import DockerError
from requests.exceptions import RequestException

LOGGER = logging.getLogger('docker_python.examples')


def parser(description: str) -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=description)
    result.add_argument('--host', default=os.environ.get('DOCKER_HOST', 'unix:///var/run/docker.sock'),
                        help='Docker endpoint (default: DOCKER_HOST or unix:///var/run/docker.sock)')
    return result


def log_error(error: DockerError | RequestException | ValueError) -> int:
    LOGGER.error('%s', error)
    return 1
