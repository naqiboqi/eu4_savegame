import numpy as np

from enum import Enum
from PIL import Image

from .models import EUArea, EUProvince, EURegion



class MapMode(Enum):
    POLITICAL = "political"
    AREA = "area"
    REGION = "region"
    DEVELOPMENT = "development"
    RELIGION = "religion"



class MapDrawer:
    def __init__(self, ):
        self.selector = MapModeSelector()
        self.world_provinces: dict[int, EUProvince] = None
        self.tag_colors: dict[str, tuple[int]] = None
        self.default_province_colors: dict[tuple[int], int] = None
        self.map_bmp: Image.Image = None
        self.map_modes = {
            MapMode.POLITICAL: self.draw_political_map,
            MapMode.AREA: self.draw_area_map,
            MapMode.REGION: self.draw_region_map,
            MapMode.DEVELOPMENT: self.draw_development_map,
            MapMode.RELIGION: self.draw_religion_map
        }

    def draw_map_political(self):
        map_pixels = np.array(self.map_bmp)
        height, width = map_pixels.shape[:2]
        for x in range(width):
            for y in range(height):
                pixel_color = tuple(map_pixels[y, x][:3])
                if pixel_color in self.default_province_colors:
                    province_id = self.default_province_colors[pixel_color]
                    owner_tag = self.world_provinces[province_id].owner

                    if owner_tag and owner_tag in self.tag_colors:
                        pass
                    


class MapModeSelector:
    def __init__(self):
        self.map_mode = None
    
    def select_map_mode(self):
        modes = [mode.value for mode in MapMode]
        while not self.map_mode:
            print("\n".join([f'{i}. {mode.capitalize()}' for i, mode in enumerate(modes, 1)]) + "\n")

            try:
                map_mode = int(input("Select a map mode to view (enter the number): \n"))
            except ValueError:
                print("Please enter a valid selection.\n")
                continue
            
            if not 1 <= map_mode <= len(modes):
                print("Please enter a valid selection.\n")
                continue

            self.map_mode = MapMode(modes[map_mode - 1])
        

selector = MapModeSelector()
selector.select_map_mode()