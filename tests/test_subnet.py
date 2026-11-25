import ipaddress
import re
import unittest

from generators.subnet import SubnetGenerator


class TestSubnetGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = SubnetGenerator()

    def test_ip_int_roundtrip(self) -> None:
        cases = [
            (0, 0, 0, 0, "0.0.0.0"),
            (192, 168, 10, 42, "192.168.10.42"),
            (255, 255, 255, 255, "255.255.255.255"),
        ]
        for o1, o2, o3, o4, expected in cases:
            val = self.gen._ip_to_int(o1, o2, o3, o4)
            self.assertEqual(self.gen._int_to_ip(val), expected)

    def test_magic_number(self) -> None:
        self.assertEqual(self.gen._get_magic_number("255.255.224.0"), (3, 32))   # /19
        self.assertEqual(self.gen._get_magic_number("255.255.255.0"), (4, 256))  # /24
        self.assertEqual(self.gen._get_magic_number("255.255.255.128"), (4, 128))  # /25
        self.assertEqual(self.gen._get_magic_number("255.255.255.252"), (4, 4))  # /30

    def test_generated_tasks_match_stdlib(self) -> None:
        for _ in range(200):
            task = self.gen.generate()
            match = re.search(r"\d+\.\d+\.\d+\.\d+/\d+", task.description)
            self.assertIsNotNone(match, f"No CIDR found in: {task.description}")

            iface = ipaddress.IPv4Interface(match.group(0))
            net = iface.network
            fields = {f.key: f.expected_value for f in task.fields}

            self.assertEqual(fields["subnet_mask"], str(iface.netmask))
            self.assertEqual(fields["network_id"], str(net.network_address))
            self.assertEqual(fields["broadcast"], str(net.broadcast_address))
            self.assertEqual(fields["first_host"], str(net.network_address + 1))
            self.assertEqual(fields["last_host"], str(net.broadcast_address - 1))
            self.assertEqual(fields["host_count"], net.num_addresses - 2)
            self.assertTrue(len(task.solution_steps) >= 5)


if __name__ == "__main__":
    unittest.main()