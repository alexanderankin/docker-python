from pathlib import Path
from tempfile import TemporaryDirectory
import tomllib
import re
import unittest

from sync_dependencies import packages, synchronize


ROOT = Path(__file__).resolve().parents[2]


class ReleaseDependencyTests(unittest.TestCase):
    def test_each_release_and_combined_releases_have_consistent_pins(self):
        components = {
            'core': ['core/pyproject.toml'],
            'requests': ['docker-python-requests/pyproject.toml'],
            'generation': ['generator/pyproject.toml', *[
                str(path.relative_to(ROOT)) for path in sorted(ROOT.glob('versions/*/pyproject.toml'))
            ]],
        }
        for component in [*components, 'all']:
            with self.subTest(component=component), TemporaryDirectory() as temp:
                root = Path(temp)
                for package in packages(ROOT):
                    target = root / package.path.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(package.path.read_text())
                paths = components[component] if component != 'all' else [
                    path for paths in components.values() for path in paths
                ]
                for relative in paths:
                    path = root / relative
                    path.write_text(re.sub(r'(?m)^version = .*$', 'version = "9.8.7"', path.read_text()))
                before = {p.path: p.path.read_text() for p in packages(root)}
                self.assertTrue(synchronize(root, check=True))
                self.assertEqual(before, {p.path: p.path.read_text() for p in packages(root)})
                self.assertTrue(synchronize(root))
                projects = packages(root)
                versions = {p.name: p.version for p in projects}
                for package in projects:
                    original = tomllib.loads(before[package.path])['project']
                    self.assertEqual(package.version, original['version'])
                    for dependency in package.dependencies:
                        name, separator, version = dependency.partition('==')
                        if separator and name in versions:
                            self.assertEqual(version, versions[name])
                        else:
                            self.assertIn(dependency, original.get('dependencies', []))
                self.assertEqual([], synchronize(root))
                self.assertEqual([], synchronize(root, check=True))

    def test_only_exact_internal_requirements_are_updated(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            core = root / 'core/pyproject.toml'
            core.parent.mkdir()
            core.write_text('[project]\nname = "docker-python-core"\nversion = "0.2.0"\n')
            client = root / 'client/pyproject.toml'
            client.parent.mkdir()
            client.write_text('''[project]
name = "client"
version = "1.0.0"
dependencies = ["docker-python-core==0.1.0", 'external==0.1.0']
[tool.example]
version = "0.1.0"
''')
            synchronize(root)
            self.assertIn('"docker-python-core==0.2.0"', client.read_text())
            self.assertIn("'external==0.1.0'", client.read_text())
            self.assertIn('version = "0.1.0"', client.read_text())


if __name__ == '__main__':
    unittest.main()
