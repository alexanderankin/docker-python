import json
import unittest

from docker_python.versions.v_1_55.models import (
    ContainerCreateRequest,
    ExposedPort,
    ExposedPorts,
)


class ExposedPortsTests(unittest.TestCase):
    def test_custom_ports_round_trip_in_generated_request(self):
        request = ContainerCreateRequest(
            image='alpine:latest', exposed_ports=ExposedPorts((ExposedPort(80), ExposedPort(53, 'udp'))),
        )
        wire = json.loads(json.dumps(request.to_wire()))
        self.assertEqual(wire, {'Image': 'alpine:latest', 'ExposedPorts': {'80/tcp': {}, '53/udp': {}}})
        restored = ContainerCreateRequest.from_wire(wire)
        self.assertEqual(restored, request)
        self.assertIsInstance(restored.exposed_ports, ExposedPorts)
        self.assertIsInstance(restored.exposed_ports.ports[0], ExposedPort)

    def test_empty_map_and_omitted_ports(self):
        self.assertEqual(ContainerCreateRequest.from_wire({'ExposedPorts': {}}).exposed_ports, ExposedPorts(()))
        self.assertIsNone(ContainerCreateRequest.from_wire({}).exposed_ports)


if __name__ == '__main__':
    unittest.main()
