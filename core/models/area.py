from dataclasses import dataclass

from . import EUProvince



@dataclass
class EUArea:
    area_id: str
    name: str
    provinces: dict[int, EUProvince]|list[int]

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"