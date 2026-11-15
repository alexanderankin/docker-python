import json
import unittest
from copy import deepcopy
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import get_type_hints

from docker_python_generator.custom.model_parsers import ExposedPortsCustomization
from docker_python_generator.customizations import (
    RuntimeModule,
    SchemaContext,
    apply_customizations,
)
from docker_python_generator.swagger import PYTHON_TYPE, load_spec

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "docker_python_generator.custom.model_parsers.ExposedPortsCustomization"


@dataclass(frozen=True)
class FuturePortsCustomization(ExposedPortsCustomization):
    def is_compatible_with_schema(self, schema, context):
        return context.resolve(schema).get("additionalProperties") == {"type": "boolean"}

    def runtime_modules(self):
        original = super().runtime_modules()[0]
        return (RuntimeModule("exposed_ports_v2", original.source, original.exports),)


class CustomizationTests(unittest.TestCase):
    def test_windows_cgroup_enum_extensions_preserve_original_specs(self):
        for path in sorted((ROOT / "docker-engine-api-specs").glob("*.yaml")):
            with self.subTest(spec=path.name):
                spec = load_spec(path)
                original = deepcopy(spec)
                customized = apply_customizations(spec).spec
                properties = customized["definitions"]["SystemInfo"]["properties"]
                for name in ("CgroupDriver", "CgroupVersion"):
                    if name in properties:
                        values = original["definitions"]["SystemInfo"]["properties"][name]["enum"]
                        self.assertEqual(properties[name]["enum"], [*values, ""])
                self.assertEqual(spec, original)

    def spec(self):
        return load_spec(ROOT / "docker-engine-api-specs/v1.55.yaml")

    def config(self, directory, sources):
        path = Path(directory) / "customizations.toml"
        path.write_text(
            '[fields."ContainerConfig.ExposedPorts"]\ntype = "ExposedPorts"\nsource = ' + json.dumps(sources) + "\n"
        )
        return path

    def test_all_existing_versions_use_their_own_custom_types_in_composed_models(self):
        classes = []
        for version in ["1_40", "1_44", "1_55"]:
            with self.subTest(version=version):
                models = import_module(f"docker_python.versions.v_{version}.models")
                classes.append(models.ExposedPorts)
                for name in [
                    "ContainerConfig",
                    "ImageConfig",
                    "ContainerCreateRequest",
                ]:
                    cls = getattr(models, name)
                    self.assertEqual(get_type_hints(cls)["exposed_ports"], models.ExposedPorts | None)
                    self.assertFalse(
                        any("ExposedPortsValue" in symbol for symbol in vars(import_module(cls.__module__)))
                    )
                request = models.ContainerCreateRequest(
                    image="alpine",
                    exposed_ports=models.ExposedPorts((models.ExposedPort(80), models.ExposedPort(53, "udp"))),
                )
                wire = json.loads(json.dumps(request.to_wire()))
                self.assertEqual(wire["ExposedPorts"], {"80/tcp": {}, "53/udp": {}})
                self.assertEqual(models.ContainerCreateRequest.from_wire(wire), request)
                self.assertIsInstance(
                    models.ContainerConfig.from_wire(wire).exposed_ports,
                    models.ExposedPorts,
                )
                self.assertIsInstance(
                    models.ImageConfig.from_wire(wire).exposed_ports,
                    models.ExposedPorts,
                )
        self.assertEqual(len(set(classes)), 3)

    def test_unknown_shape_and_missing_target_fail_with_location_and_version(self):
        spec = self.spec()
        spec["definitions"]["ContainerConfig"]["properties"]["ExposedPorts"]["additionalProperties"] = {
            "type": "boolean"
        }
        with self.assertRaisesRegex(
            ValueError,
            "API 1.55: #/definitions/ContainerConfig/properties/ExposedPorts: expected exactly one",
        ):
            apply_customizations(spec)
        del spec["definitions"]["ContainerConfig"]["properties"]["ExposedPorts"]
        with self.assertRaisesRegex(ValueError, "customization target missing"):
            apply_customizations(spec)

    def test_ambiguity_is_rejected_and_candidates_select_by_shape(self):
        with TemporaryDirectory() as directory:
            original = self.spec()
            with self.assertRaisesRegex(ValueError, "found 2"):
                apply_customizations(original, self.config(directory, [SOURCE, SOURCE]))
            config = self.config(directory, [SOURCE, __name__ + ".FuturePortsCustomization"])
            old = apply_customizations(original, config)
            changed = deepcopy(original)
            changed["definitions"]["ContainerConfig"]["properties"]["ExposedPorts"]["additionalProperties"] = {
                "type": "boolean"
            }
            new = apply_customizations(changed, config)
            self.assertEqual(old.runtime_modules[0].name, "exposed_ports")
            self.assertEqual(new.runtime_modules[0].name, "exposed_ports_v2")
            self.assertNotIn(
                PYTHON_TYPE,
                original["definitions"]["ContainerConfig"]["properties"]["ExposedPorts"],
            )
            self.assertEqual(apply_customizations(original, config), old)

    def test_compatibility_resolves_references(self):
        spec = self.spec()
        value = spec["definitions"]["ContainerConfig"]["properties"]["ExposedPorts"]
        spec["definitions"]["PortsShape"] = value
        context = SchemaContext("1.55", "#/definitions/PortsShape", spec)
        self.assertTrue(
            ExposedPortsCustomization().is_compatible_with_schema({"$ref": "#/definitions/PortsShape"}, context)
        )
        changed = deepcopy(value)
        changed["minProperties"] = 1
        self.assertFalse(ExposedPortsCustomization().is_compatible_with_schema(changed, context))


if __name__ == "__main__":
    unittest.main()
