"""Keep exact internal dependency pins aligned with local package metadata."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import tomllib


@dataclass(frozen=True)
class Package:
    path: Path
    name: str
    version: str
    dependencies: tuple[str, ...]


def packages(root: Path) -> list[Package]:
    paths = sorted(root.glob('*/pyproject.toml')) + sorted(root.glob('versions/*/pyproject.toml'))
    result = []
    for path in paths:
        project = tomllib.loads(path.read_text())['project']
        result.append(Package(path, project['name'], project['version'], tuple(project.get('dependencies', ()))))
    return result


def synchronize(root: Path, *, check: bool = False) -> list[Path]:
    projects = packages(root)
    versions = {package.name: package.version for package in projects}
    changed = []
    for package in projects:
        content = package.path.read_text()
        updated = content
        for dependency in package.dependencies:
            name, separator, version = dependency.partition('==')
            if separator and name in versions and version != versions[name]:
                # Match the full quoted requirement, preserving formatting and other fields.
                updated = re.sub(
                    r"(['\"])" + re.escape(dependency) + r'\1',
                    lambda match: f'{match[1]}{name}=={versions[name]}{match[1]}',
                    updated,
                )
        if updated != content:
            changed.append(package.path)
            if not check:
                package.path.write_text(updated)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    changed = synchronize(args.root, check=args.check)
    for path in changed:
        print(f'{"Stale" if args.check else "Updated"}: {path.relative_to(args.root)}')
    if args.check and changed:
        parser.exit(1, 'Run python .github/scripts/sync_dependencies.py to update internal dependency pins.\n')


if __name__ == '__main__':
    main()
