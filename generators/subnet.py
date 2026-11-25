from core.models import InputField, Task
from generators.base import BaseGenerator


class SubnetGenerator(BaseGenerator):
    @property
    def category_id(self) -> str:
        return "subnet"

    @property
    def name(self) -> str:
        return "IPv4-Subnetting"

    def _ip_to_int(self, o1: int, o2: int, o3: int, o4: int) -> int:
        return (o1 << 24) | (o2 << 16) | (o3 << 8) | o4

    def _int_to_ip(self, val: int) -> str:
        return (
            f"{(val >> 24) & 255}."
            f"{(val >> 16) & 255}."
            f"{(val >> 8) & 255}."
            f"{val & 255}"
        )

    def _get_magic_number(self, mask_str: str) -> tuple[int, int]:
        octets = [int(x) for x in mask_str.split(".")]
        for index, octet in enumerate(octets, start=1):
            if octet < 255:
                return index, 256 - octet
        return 4, 1

    def generate(self) -> Task:
        o1, o2 = 192, 168
        o3 = self._gauss_int(0, 255)
        o4 = self._gauss_int(1, 254)
        cidr = self._gauss_int(19, 30, mu=25, sigma=2.5)
        ip_str = f"{o1}.{o2}.{o3}.{o4}/{cidr}"

        ip_int = self._ip_to_int(o1, o2, o3, o4)
        mask_int = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
        net_int = ip_int & mask_int
        broadcast_int = net_int | (~mask_int & 0xFFFFFFFF)

        mask_str = self._int_to_ip(mask_int)
        net_str = self._int_to_ip(net_int)
        broadcast_str = self._int_to_ip(broadcast_int)
        first_host = self._int_to_ip(net_int + 1)
        last_host = self._int_to_ip(broadcast_int - 1)
        host_count = (1 << (32 - cidr)) - 2

        octet_pos, magic = self._get_magic_number(mask_str)

        fields = [
            InputField("subnet_mask", "Subnetzmaske", mask_str),
            InputField("network_id", "Netzadresse", net_str),
            InputField("broadcast", "Broadcast-Adresse", broadcast_str),
            InputField("first_host", "Erste nutzbare Host-IP", first_host),
            InputField("last_host", "Letzte nutzbare Host-IP", last_host),
            InputField("host_count", "Anzahl nutzbarer Hosts", host_count),
        ]

        solution_steps = [
            f"CIDR /{cidr} entspricht der Subnetzmaske {mask_str}.",
            f"Interessantes Oktett: {octet_pos}. Oktett -> Schrittweite (Magic Number) = {magic}.",
            f"Netzadresse (Vielfaches von {magic} <= IP-Oktett): {net_str}.",
            f"Broadcast-Adresse (nächstes Netz - 1): {broadcast_str}.",
            f"Nutzbarer Hostbereich: {first_host} bis {last_host}.",
            f"Anzahl nutzbarer Hosts: 2^(32 - {cidr}) - 2 = 2^{32 - cidr} - 2 = {host_count}.",
        ]

        return Task(
            category=self.category_id,
            title=f"{self.name}: {ip_str}",
            description=f"Bestimme die Netzdaten für die IP-Adresse {ip_str}.",
            fields=fields,
            solution_steps=solution_steps,
        )
        
    
