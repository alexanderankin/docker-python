"""Remove generated commands and models, preserving clients and package metadata."""
import argparse
from pathlib import Path
import shutil


def clean(version: Path) -> None:
    namespace = version / 'src' / 'docker_python' / 'versions'
    for package in namespace.glob('v_*'):
        for name in ('commands', 'models'):
            directory = package / name
            if directory.is_dir():
                shutil.rmtree(directory)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('versions', type=Path, nargs='+', help='Version package directories to clean')
    for version in parser.parse_args().versions:
        clean(version)


if __name__ == '__main__':
    main()
