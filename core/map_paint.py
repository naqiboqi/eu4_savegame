import math
import numpy as np
import tkinter as tk

from PIL import Image, ImageTk
from .colors import EUColors
from .map_eventhandler import MapEventHandler
from .models import EUArea, EUProvince, MapMode, ProvinceType, ProvinceTypeColor, EURegion
from .utils import MapUtils
from .world import EUWorldData



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



class MapPainter:
    def __init__(self, colors: EUColors, world_data: EUWorldData):
        self.colors = colors
        self.world_data = world_data
        self.selector = MapModeSelector()
        self.map_modes = {
            MapMode.POLITICAL: self.draw_map_political,
            MapMode.AREA: self.draw_map_area,
            MapMode.REGION: self.draw_map_region,
            MapMode.DEVELOPMENT: self.draw_map_development,
            MapMode.RELIGION: self.draw_map_religion
        }

        self.handler: MapEventHandler = None
        self.canvas: tk.Canvas = None
        self.hover_label: tk.Label = None
        self.quit_button: tk.Button = None
        self.root: tk.Tk = None
        self.tk_image: ImageTk.PhotoImage = None
        self.world_image: Image.Image = None

    def draw_map(self):
        print("Drawing map....")
        #draw_map_mode = self.map_modes.get(self.selector.map_mode, self.draw_map_political)
        self.world_image = self.world_data.world_image
        map_pixels = self.draw_map_area()

        world_image = Image.fromarray(map_pixels)
        self.world_image = world_image

        if not self.root:
            self.root = tk.Tk()     
            self.root.title("Map Viewer")

            self.canvas = tk.Canvas(self.root, width=1200, height=900)
            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.tk_image = ImageTk.PhotoImage(self.world_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

            self.quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy)
            self.quit_button.pack()

            self.hover_label = tk.Label(self.root, text="Choose a Province", bg="white")
            self.hover_label.pack()

            self.handler = MapEventHandler(
                canvas=self.canvas,
                map_mode=self.selector.map_mode,
                world_image=self.world_image,
                hover_label=self.hover_label, 
                provinces=self.world_data.provinces)
            self.canvas.bind("<Motion>", self.handler.on_map_hover)

        self.root.mainloop()

    def draw_map_political(self):
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

        province_type_colors = {
            ProvinceType.NATIVE: ProvinceTypeColor.NATIVE.value,
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        for province in world_provinces.values():
            province_type = province.province_type

            if province_type == ProvinceType.OWNED:
                owner_country = province.owner
                province_color = owner_country.tag_color
            else:
                province_color = province_type_colors.get(province_type, None)

            x_coords, y_coords = zip(*province.pixel_locations)
            map_pixels[y_coords, x_coords] = province_color

        return map_pixels

    def draw_map_area(self):
        world_areas = self.world_data.areas
        map_pixels = np.array(self.world_image)

        for area in world_areas.values():
            area_pixels = area.pixel_locations
            if area_pixels:
                if area.is_land_area:
                    area_color = MapUtils.seed_color(area.area_id)
                elif area.is_sea_area:
                    area_color = ProvinceTypeColor.SEA.value
                elif area.is_wasteland_area:
                    area_color = ProvinceTypeColor.WASTELAND.value

                x_coords, y_coords = zip(*area_pixels)
                map_pixels[y_coords, x_coords] = area_color

        return map_pixels

    def draw_map_region(self):
        world_regions = self.world_data.regions
        map_pixels = np.array(self.world_image)

        return None

    def development_to_color(self, development: float, max_development: float=200.000):
        normalized = math.log(max(1, development)) / math.log(max(1, max_development))
        intensity = int(255 * normalized)
        return (0, intensity, 0)

    def draw_map_development(self):
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

        max_development = max(p.development for p in world_provinces.values())

        province_type_colors = {
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        for province in world_provinces.values():
            province_color = province_type_colors.get(province.province_type)

            if province_color is None:
                province_color = self.development_to_color(province.development, max_development)

            x_coords, y_coords = zip(*province.pixel_locations)
            map_pixels[y_coords, x_coords] = province_color

        return map_pixels

    def draw_map_religion(self):
        pass
