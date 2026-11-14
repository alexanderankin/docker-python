"""Parser fixtures based on the docker-java model tests and their documented forms."""

import unittest
from copy import deepcopy
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import get_type_hints

from docker_python.core.models import from_wire, to_wire

from docker_python_generator.customizations import apply_customizations
from docker_python_generator.swagger import load_spec

ROOT = Path(__file__).resolve().parents[2]


class ModelParserTests(unittest.TestCase):
    def models(self, version="1_55"):
        return import_module("docker_python.versions.v_" + version + ".models")

    def test_protocols_exposed_ports_and_scalar_json(self):
        m = self.models()
        for text in ["tcp", "TCP", "TcP"]:
            self.assertIs(m.InternetProtocol.parse(text), m.InternetProtocol.TCP)
        self.assertEqual(m.ExposedPort.parse("80"), m.ExposedPort(80))
        self.assertEqual(m.ExposedPort.parse("80/UDP"), m.ExposedPort(80, m.InternetProtocol.UDP))
        self.assertEqual(to_wire(m.ExposedPort.parse("80")), "80/tcp")
        self.assertEqual(from_wire(m.ExposedPort, "80"), m.ExposedPort(80))
        self.assertIs(from_wire(m.InternetProtocol, "SCTP"), m.InternetProtocol.SCTP)
        for text in [None, "nonsense", "80/quic", "80/tcp/extra"]:
            with self.subTest(value=text), self.assertRaisesRegex(ValueError, "ExposedPort"):
                m.ExposedPort.parse(text)

    def test_host_and_full_port_bindings(self):
        m = self.models()
        for text, ip, host, port in [
            ("127.0.0.1:80:8080/tcp", "127.0.0.1", "80", 8080),
            ("127.0.0.1:80:8080", "127.0.0.1", "80", 8080),
            ("80:8080", None, "80", 8080),
            ("8080", None, None, 8080),
            ("127.0.0.1::8080", "127.0.0.1", None, 8080),
            ("[::1]:80:8080", "::1", "80", 8080),
            ("[::1]::8080", "::1", None, 8080),
            ("8000-8005:8080", None, "8000-8005", 8080),
        ]:
            with self.subTest(value=text):
                result = m.PortBinding.parse(text)
                self.assertEqual(result.binding.host_ip, ip)
                self.assertEqual(result.binding.host_port, host)
                self.assertEqual(result.exposed_port, m.ExposedPort(port))
                self.assertEqual(m.PortBinding.parse(str(result)), result)
        for value, ip, port in [
            ("", None, None),
            ("80", None, "80"),
            ("127.0.0.1", "127.0.0.1", None),
            ("127.0.0.1:80", "127.0.0.1", "80"),
            ("[::1]:80", "::1", "80"),
        ]:
            self.assertEqual(m.Binding.parse(value), m.Binding(host_ip=ip, host_port=port))
        for text in [None, "nonsense", "80:bad", "a:b:c:d", "[::1]"]:
            with self.subTest(value=text), self.assertRaisesRegex(ValueError, "PortBinding"):
                m.PortBinding.parse(text)

    def test_ports_preserve_null_empty_and_multiple_bindings(self):
        m = self.models()
        wire = {
            "80/tcp": [{"HostIp": "", "HostPort": "80"}, {"HostIp": "127.0.0.1", "HostPort": "8080"}],
            "2377/tcp": None,
            "53/udp": [],
        }
        ports = from_wire(m.Ports, wire)
        self.assertEqual(to_wire(ports), wire)
        self.assertEqual(len(ports.bindings[m.ExposedPort(80)]), 2)
        self.assertIsNone(ports.bindings[m.ExposedPort(2377)])
        self.assertEqual(ports.bindings[m.ExposedPort(53, "udp")], ())
        self.assertEqual(
            len(
                m.Ports.from_bindings(m.PortBinding.parse("80:8080"), m.PortBinding.parse("81:8080")).bindings[
                    m.ExposedPort(8080)
                ]
            ),
            2,
        )

    def test_binds_options_and_windows_paths(self):
        m = self.models()
        cases = [
            "/host:/container",
            "/host:/container:ro",
            "named-volume:/data:rw,nocopy",
            "a:/container:ro",
            "C:/host:D:/container:ro",
            r"C:\host:/container:rw,nocopy",
            r"C:\host:D:\container:ro,z",
            "C:/host:/container:ro,Z,rshared",
        ]
        for text in cases:
            with self.subTest(value=text):
                bind = m.Bind.parse(text)
                self.assertEqual(m.Bind.parse(str(bind)), bind)
                self.assertEqual(from_wire(m.Bind, to_wire(bind)), bind)
        self.assertEqual(m.Bind.parse("a:/container:ro").source, "a")
        bind = m.Bind.parse("/src:/dst:ro,Z,nocopy,rshared")
        self.assertIs(bind.access_mode, m.AccessMode.RO)
        self.assertIs(bind.selinux, m.SELContext.PRIVATE)
        self.assertIs(bind.propagation, m.PropagationMode.RSHARED)
        self.assertTrue(bind.nocopy)
        for text in [None, "bad", "/src:", "/src:/dst:bad", "/src:/dst:ro:extra"]:
            with self.subTest(value=text), self.assertRaisesRegex(ValueError, "Bind"):
                m.Bind.parse(text)

    def test_volumes_links_and_volumes_from(self):
        m = self.models()
        self.assertEqual(m.Volume.parse("/data"), m.Volume("/data"))
        self.assertEqual(m.Volume.parse({"path": "/data"}), m.Volume("/data"))
        self.assertEqual(to_wire(m.Volume("/data")), "/data")
        self.assertEqual(to_wire(from_wire(m.Volumes, {"/data": {}})), {"/data": {}})
        self.assertEqual(to_wire(m.Volumes(())), {})
        self.assertEqual(to_wire(m.Binds(())), [])
        self.assertEqual(to_wire(m.Links(())), [])
        self.assertEqual(m.Link.parse("/name1:/name2/alias"), m.Link("name1", "alias"))
        self.assertEqual(to_wire(from_wire(m.Links, ["name:alias"])), ["name:alias"])
        self.assertEqual(m.VolumesFrom.parse("db"), m.VolumesFrom("db", m.AccessMode.RW))
        self.assertEqual(to_wire(m.VolumesFrom.parse("db:ro")), "db:ro")
        for cls, values in [
            (m.Volume, [None, "", {}]),
            (m.Link, [None, "bad", "a:", "a:b:c"]),
            (m.VolumesFrom, [None, "", "db:bad", "db:ro:extra"]),
        ]:
            for value in values:
                with self.subTest(cls=cls, value=value), self.assertRaises(ValueError):
                    cls.parse(value)

    def test_structured_parsers_keep_json_objects(self):
        m = self.models()
        for text, source, destination, permissions in [
            ("/dev/sda", "/dev/sda", "/dev/sda", "rwm"),
            ("/dev/sda:/dev/xvdc:r", "/dev/sda", "/dev/xvdc", "r"),
            ("/dev/sda:/dev/xvdc", "/dev/sda", "/dev/xvdc", "rwm"),
            ("/dev/sda:rw", "/dev/sda", "/dev/sda", "rw"),
        ]:
            result = m.Device.parse(text)
            self.assertEqual(
                to_wire(result),
                {"PathOnHost": source, "PathInContainer": destination, "CgroupPermissions": permissions},
            )
            self.assertEqual(from_wire(m.Device, to_wire(result)), result)
        for text, name, retries in [
            ("no", "no", 0),
            ("always", "always", 0),
            ("unless-stopped", "unless-stopped", 0),
            ("on-failure", "on-failure", 0),
            ("on-failure:5", "on-failure", 5),
        ]:
            result = m.RestartPolicy.parse(text)
            self.assertEqual(to_wire(result), {"Name": name, "MaximumRetryCount": retries})
            self.assertEqual(from_wire(m.RestartPolicy, to_wire(result)), result)
        for cls, values in [
            (m.Device, [None, "", "/dev/sda:/target:q", "/dev/sda:/target:rr", "/dev/sda::rw"]),
            (m.RestartPolicy, [None, "bad", "always:3", "on-failure:-1", "on-failure:1:2"]),
        ]:
            for value in values:
                with self.subTest(cls=cls, value=value), self.assertRaises(ValueError):
                    cls.parse(value)

    def test_every_existing_version_wires_custom_types_and_names(self):
        for version in ["1_40", "1_44", "1_55"]:
            with self.subTest(version=version):
                m = self.models(version)
                host = m.HostConfig(
                    binds=m.Binds((m.Bind.parse("/host:/data:ro"),)),
                    links=m.Links((m.Link.parse("db:database"),)),
                    volumes_from=[m.VolumesFrom.parse("other:ro")],
                    devices=[m.Device.parse("/dev/null")],
                    restart_policy=m.RestartPolicy.parse("on-failure:2"),
                    port_bindings=m.Ports.from_bindings(m.PortBinding.parse("127.0.0.1:8080:80")),
                )
                request = m.ContainerCreateRequest(
                    image="alpine", host_config=host, volumes=m.Volumes((m.Volume("/data"),))
                )
                wire = to_wire(request)
                self.assertEqual(from_wire(m.ContainerCreateRequest, wire), request)
                self.assertEqual(get_type_hints(m.HostConfig)["devices"], list[m.Device] | None)
                self.assertEqual(get_type_hints(m.HostConfig)["volumes_from"], list[m.VolumesFrom] | None)
                volume_json = {
                    "Name": "named",
                    "Driver": "local",
                    "Mountpoint": "/host",
                    "Labels": {},
                    "Scope": "local",
                    "Options": {},
                }
                inspected = m.InspectVolumeResponse.from_wire(volume_json)
                self.assertEqual(to_wire(inspected), volume_json)
                self.assertEqual(m.VolumeListResponse.from_wire({"Volumes": [volume_json]}).volumes[0], inspected)

    def test_changed_definition_and_inherited_field_contracts_fail(self):
        spec = load_spec(ROOT / "docker-engine-api-specs/v1.55.yaml")
        for name in ["PortBinding", "PortMap", "DeviceMapping", "RestartPolicy"]:
            changed = deepcopy(spec)
            changed["definitions"][name]["minProperties"] = 1
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "compatible customization"):
                apply_customizations(changed)
        with TemporaryDirectory() as temp:
            config = Path(temp) / "custom.toml"
            config.write_text(
                '[fields."Derived.Value"]\ntype="Links"\nsource="docker_python_generator.custom.model_parsers.StringListCustomization"\n'
            )
            schema = {"type": "array", "items": {"type": "string"}}
            sample = {
                "swagger": "2.0",
                "info": {"version": "test"},
                "paths": {},
                "definitions": {
                    "Base": {"properties": {"Value": schema}},
                    "Derived": {"allOf": [{"$ref": "#/definitions/Base"}]},
                },
            }
            result = apply_customizations(sample, config)
            self.assertNotEqual(result.spec, sample)
            sample["definitions"]["Derived"]["properties"] = {"Value": schema}
            with self.assertRaisesRegex(ValueError, "Ambiguous inherited field"):
                apply_customizations(sample, config)


if __name__ == "__main__":
    unittest.main()
