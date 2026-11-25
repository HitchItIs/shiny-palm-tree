from core.models import InputField, Task
from generators.base import BaseGenerator


class SubnetGenerator(BaseGenerator):
    @property
    def category_id(self) -> str:
        return "subnet"
    
    @property
    def name(self) -> str:
        return "ipv4-subnetting"
    
    
    
    def _ip_to_int(self, o1: int, o2: int, o3: int, o4: int) -> int:
        return (o1 << 24) | (o2 << 16) | (o3 << 8) | o4
    
    def _int_to_ip(self, val: int) ->str:
        return f"{(val >> 24) & 255}.{(val >> 16) & 255}.{val & 255}"
    
    def _get_magic_number(self, mask_str: str) -> tuple [int, int]:
        octets = [int(x) for x in mask_str.split(".")]
        for index, octet in enumerate( octets, start=1):
            if octet < 255:
                return index, 256 - octet
            return 4, 1
        
        
    def generate (self) -> Task:
        
        o1, o2 = 192, 168
        o3 = self._gauss_int(0, 255)
        o4 = self._gauss_int(1, 254)
        cidr = self._gauss_int(19, 30, mu=25, sigma=2.5)
        ip_str = f"{o1}.{o2}.{o3}{o4}/{cidr}"
        
        
    
