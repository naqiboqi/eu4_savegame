"""
This module defines EUProvince, which represents the smallest building block of the world in
Europa Universalis IV.
"""



from dataclasses import dataclass, fields
from enum import Enum
from math import floor
from typing import Optional, get_type_hints
from . import EUMapEntity, EUCountry, TerrainType
from ..utils import resolve_type



class ProvinceType(Enum):
    """Enum of province types.
    
    - Owned
    - Native
    - Sea
    - Wasteland
    """
    OWNED = "owned"
    NATIVE = "native"
    SEA = "sea"
    WASTELAND = "wasteland"


class ProvinceTypeColor(Enum):
    """Enum of display colors for each province type.
    
    **Owned** provinces have their own definition from their owner tag.
    - Native -> Sandy brown (203, 164, 103)
    - Sea -> Blue (203, 164, 103)
    - Wasteland -> Grey (128, 128, 128)
    """
    OWNED: tuple[int] = ()
    NATIVE = (203, 164, 103)
    SEA = (55, 90, 220)
    WASTELAND = (128, 128, 128)


@dataclass
class EUProvince(EUMapEntity):
    """Represents a province on the map.
    
    Inherits attributes from `EUMapEntity`.

    Attributes:
        province_id (int): The unique ID of the province.
        name (str): The province's name.
        province_type (ProvinceType): The type of province (Owned, Native, Wasteland, or Sea).
        terrain_type (TerrainType): The type of terrain the province has (e.g. grasslands, steppe, glacial, etc.).
        owner (Optional[EUCountry]): The province's owner.
        capital (Optional[str]): The province's capital city.
        hre (Optional[bool]): If the province is within the Holy Roman Empire.
        culture (Optional[str]): The province's culture.
        religion (Optional[str]): The province's religion.
        base_tax (Optional[int]): The province's tax development.
        base_production (Optional[int]): The province's production development.
        base_manpower (Optional[int]): The province's manpower development.
        trade_goods (Optional[str]): The dominant trade good produced by the province.
        trade_power (Optional[float]): The province's trade power.
            Higher levels indicate stronger influence on that province's trade node.
        center_of_trade (Optional[int]): The province's center of trade level.
            Higher levels indicate stronger trade power and development.
        trade (Optional[str]): The trade node that the province belongs to.
        local_autonomy (Optional[float]): The province's autonomy and degree of separation.
            Higher levels indicate less production and power contribution to the owning country.
        devastation (Optional[int]): The amount of devastation in the province.
            Higher levels indicate less production and power contribution to the owning country.
        unrest (Optional[int]): The amount of unrest in the province.
            Higher levels indicate a higher likelyhood of rebellion.
        garrison (Optional[int]): The province's fort garrison population.
        fort_level (Optional[int]): The province's fort level. 
            Higher levels indicate a stronger fort and make the province harder to siege and occupy.
        native_size (Optional[int]): The number of natives in the province.
        native_ferocity (Optional[int]): The ferocity of natives in the province.
            Represents their strength during an uprising.
        native_hostileness (Optional[int]): The hostility of natives in the province.
            Represents the likelyhood of an uprising.
        patrol (Optional[int]): The number of game ticks it takes to patrol the province (only if it a sea province).
    """
    province_id: int
    province_type: ProvinceType
    terrain_type: Optional[TerrainType] = None
    owner: Optional[EUCountry] = None
    capital: Optional[str] = None
    hre: Optional[bool] = False
    culture: Optional[str] = None
    religion: Optional[str] = None
    base_tax: Optional[int] = 0
    base_production: Optional[int] = 0
    base_manpower: Optional[int] = 0
    trade_goods: Optional[str] = None
    trade_power: Optional[float] = 0.00
    center_of_trade: Optional[int] = None
    trade: Optional[str] = None
    local_autonomy: Optional[float] = 0.00
    devastation: Optional[float] = 0.00
    unrest: Optional[float] = 0.00
    garrison: Optional[int] = 0
    fort_level: Optional[int] = None
    native_size: Optional[int] = 0
    native_ferocity: Optional[int] = 0
    native_hostileness: Optional[int] = 0
    patrol: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        """Builds the province from a dictionary."""
        converted_data = {}
        type_hints = get_type_hints(cls)

        for key, value in data.items():
            if key not in type_hints:
                continue

            field_type = resolve_type(type_hints[key])
            try:
                if field_type == str:
                    converted_data[key] = value
                elif field_type == int:
                    converted_data[key] = int(float(value))
                elif field_type == float:
                    converted_data[key] = round(float(value), 2)
                elif field_type == ProvinceType:
                    converted_data[key] = ProvinceType(value)
                else:
                    converted_data[key] = value
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return cls(**converted_data)

    def update_from_dict(self, data: dict):
        """Updates the province based on data from a dictionary."""
        type_hints = {}
        for obj in self.__class__.mro():
            type_hints.update(get_type_hints(obj))

        for key, value in data.items():
            if key not in type_hints:
                continue

            field_type = resolve_type(type_hints[key])
            try:
                if field_type == str:
                    setattr(self, key, value)
                elif field_type == int:
                    setattr(self, key, int(float(value)))
                elif field_type == float:
                    setattr(self, key, round(float(value), 2))
                elif field_type == ProvinceType:
                    setattr(self, key, ProvinceType(value))
                else:
                    setattr(self, key, value)
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return self

    @property
    def owner_name(self):
        match(self.province_type):
            case ProvinceType.OWNED:
                owner = self.owner
                return owner.name or owner.tag
            case ProvinceType.NATIVE:
                return "Native Lands"

        return "-"

    @property
    def is_capital(self):
        """If the province is the capital of its owning country."""
        if self.owner:
            return self.owner.capital == self.province_id
        return False

    @property
    def development(self):
        """Returns the total development of the province.
        
        As wasteland and sea provinces have no development, returns 0 in those cases.
        """
        if not (self.province_type == ProvinceType.SEA or self.province_type == ProvinceType.WASTELAND):
            return self.base_manpower + self.base_production + self.base_tax

        return 0

    @property
    def autonomy_modifier(self):
        """Computes the autonomy modifier based on local autonomy.

        The autonomy modifier is calculated as:
            `1 - (local_autonomy / 100)`
        """
        if self.local_autonomy:
            return 1 - (self.local_autonomy / 100)
        return 1.00

    @property
    def tax_income(self):
        """The monthly tax income of the province in ducats."""
        annual_income = self.base_tax * 0.5 * self.autonomy_modifier
        return round(annual_income / 12, 2)

    @property
    def base_production_income(self):
        """The monthly production income of the province before applying the trade good price."""
        annual_income = self.goods_produced * self.autonomy_modifier
        return round(annual_income, 2)

    @property
    def goods_produced(self):
        """The amount of goods produced by the province. Is based on the province's `base_production`."""
        return round(self.base_production * 0.10 * self.autonomy_modifier, 2)

    @property
    def manpower(self):
        """The amount of manpower contributed by the province. Is based on the province's `base_manpower`."""
        return floor(self.base_manpower * 125 * self.autonomy_modifier) + 250

    @property
    def sailors(self):
        """The amount of sailors contributed by the province. Is based on the province's `base_production`."""
        return floor(self.base_production * 30 * self.autonomy_modifier)

    def __eq__(self, other: "EUProvince"):
        return self.province_id == other.province_id

    def __str__(self):
        return f"Province: {self.name} with ID {self.province_id}"
