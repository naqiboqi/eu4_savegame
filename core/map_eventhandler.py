import tkinter as tk

from PIL import Image, ImageTk
from .models import EUArea, EUProvince, MapMode, ProvinceType, ProvinceTypeColor, EURegion
from .utils import MapUtils



class MapEventHandler:
    def __init__(
        self,
        canvas: tk.Canvas,
        map_mode: MapMode,
        world_image: Image.Image,
        hover_label: tk.Label, 
        provinces: dict[int, EUProvince]):
        self.canvas = canvas
        self.map_mode = map_mode
        self.world_image = world_image
        self.hover_label = hover_label
        self.provinces = provinces

        self.scale_x = 1
        self.scale_y = 1
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.start_drag_x = 0
        self.start_drag_y = 0

        self.scaled_image = self.world_image
        self.tk_image = ImageTk.PhotoImage(self.scaled_image)

        self.canvas_id = self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.tk_image)

        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_pan_end)
        self.canvas.bind("<MouseWheel>", self.on_zoom)

    def set_image_in_bounds(self):
        image_width = self.scaled_image.width
        image_height = self.scaled_image.height

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.offset_x = MapUtils.get_bounded_offset(
            offset=self.offset_x, 
            image_dim=image_width, 
            canvas_dim=canvas_width)
        self.offset_y = MapUtils.get_bounded_offset(
            offset=self.offset_y,
            image_dim=image_height,
            canvas_dim=canvas_height)

    def on_pan_start(self, event: tk.Event):
        self.dragging = True
        self.start_drag_x = event.x
        self.start_drag_y = event.y

    def on_pan_drag(self, event: tk.Event):
        if self.dragging:
            dx = event.x - self.start_drag_x
            dy = event.y - self.start_drag_y

            self.offset_x += dx
            self.offset_y += dy

            self.set_image_in_bounds()
            self.canvas.coords(self.canvas_id, self.offset_x, self.offset_y)

            self.start_drag_x = event.x
            self.start_drag_y = event.y

    def on_pan_end(self, event: tk.Event):
        self.dragging = False

    def on_zoom(self, event: tk.Event):
        ZOOM_IN_FACTOR = 1.1
        ZOOM_OUT_FACTOR = 0.9

        MIN_SCALE = 0.5  
        MAX_SCALE = 5.0  

        new_scale = self.scale_x * (ZOOM_IN_FACTOR if event.delta > 0 else ZOOM_OUT_FACTOR)
        new_width = new_scale * self.world_image.width
        new_height = new_scale * self.world_image.height

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if new_width <= canvas_width and new_height <= canvas_height:
            if new_scale < self.scale_x:
                new_scale = self.scale_x

        if not MIN_SCALE <= new_scale <= MAX_SCALE:
            return

        self.scale_x = self.scale_y = new_scale
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        image_x, image_y = MapUtils.canvas_to_image_coords(
            canvas_x=canvas_x,
            canvas_y=canvas_y,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            scale_x=self.scale_x,
            scale_y=self.scale_y)

        self.offset_x = canvas_x - image_x * self.scale_x
        self.offset_y = canvas_y - image_y * self.scale_y

        self.canvas.after(50, self.update_on_zoom)

    def update_on_zoom(self):
        self.scaled_image = self.world_image.resize(
            (int(self.world_image.width * self.scale_x), int(self.world_image.height * self.scale_y)),
            Image.Resampling.NEAREST)

        self.set_image_in_bounds()

        self.tk_image = ImageTk.PhotoImage(self.scaled_image)
        self.canvas.itemconfig(self.canvas_id, image=self.tk_image)

        self.canvas.coords(self.canvas_id, self.offset_x, self.offset_y)
        self.canvas.config(scrollregion=(0, 0, self.scaled_image.width, self.scaled_image.height))

    def get_hovered_province(self, x: int, y: int):
        for province in self.provinces.values():
            if (x, y) in province.pixel_locations:
                return province

        return None

    def on_map_hover(self, event: tk.Event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        adjusted_x = (canvas_x - self.offset_x) / self.scale_x
        adjusted_y = (canvas_y - self.offset_y) / self.scale_y

        province = self.get_hovered_province(int(adjusted_x), int(adjusted_y))
        self.hover_label.config(text=f"Hovering over: ({adjusted_x:.2f}, {adjusted_y:.2f}) Province name {province.name} with ID {province.province_id}. Owned by {province.owner}")
