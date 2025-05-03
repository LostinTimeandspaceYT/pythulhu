import time
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import terminalio


class TouchRegion:
    def __init__(self, name: str, x: int, y: int, width: int, height: int, callback):
        self.name = name
        self.bounds = (x, y, x + width, y + height)
        self.callback = callback

    def contains(self, touch: tuple[int, int]) -> bool:
        x1, y1, x2, y2 = self.bounds
        tx, ty = touch
        return x1 <= tx <= x2 and y1 <= ty <= y2

class TouchManager:
    def __init__(self, tsc_device, width=320, height=240):
        self.tsc = tsc_device
        self.regions: list[TouchRegion] = []
        self.screen_width = width
        self.screen_height = height
        self.regions: list[TouchRegion] = []
        self.buttons: list[TouchButton] = []

        # These are estimated; can be calibrated
        self.raw_min_x = 350
        self.raw_max_x = 3700
        self.raw_min_y = 328
        self.raw_max_y = 3600

    def scale_touch(self, raw_x, raw_y):
        norm_x = (raw_x - self.raw_min_x) / (self.raw_max_x - self.raw_min_x)
        norm_y = (raw_y - self.raw_min_y) / (self.raw_max_y - self.raw_min_y)
        screen_x = int(norm_x * self.screen_width)
        screen_y = int((1.0 - norm_y) * self.screen_height)
        return (screen_x, screen_y)

    def draw_coordinate_overlay(self, group):
        self.coord_label = label.Label(terminalio.FONT, text="", color=0xFF00FF, x=5, y=5)
        group.append(self.coord_label)

    def update_coordinates(self, raw, scaled):
        if hasattr(self, "coord_label"):
            rx, ry = raw
            sx, sy = scaled
            self.coord_label.text = f"raw: {rx},{ry}\nscaled: {sx},{sy}"

    def update(self):
        for button in self.buttons:
            button.update()

    def add_region(self, region):
        self.regions.append(region)
        if hasattr(region, "_button_ref"):
            self.buttons.append(region._button_ref)

    def remove_region(self, name: str):
        self.regions = [r for r in self.regions if r.name != name]

    def clear_regions(self):
        self.regions.clear()

    def poll(self):
        if not self.tsc.touched:
            return

        point = self.tsc.touch
        if point is None:
            return

        raw_pos = (point["x"], point["y"])
        screen_pos = self.scale_touch(*raw_pos)

        self.update_coordinates(raw_pos, screen_pos)

        for region in self.regions:
            if region.contains(screen_pos):
                self.update_coordinates(raw_pos, screen_pos)
                if hasattr(region, "_button_ref"):
                    region._button_ref.flash()

                region.callback(screen_pos)
                return

    def calibrate(self, hal_display=None):
        corners = [
            ("top-left", 20, 20),
            ("top-right", self.screen_width - 20, 20),
            ("bottom-left", 20, self.screen_height - 20),
            ("bottom-right", self.screen_width - 20, self.screen_height - 20),
        ]

        raw_xs = []
        raw_ys = []

        if hal_display:
            hal_display.clear_display()

        for name, screen_x, screen_y in corners:
            if hal_display:
                hal_display.clear_display()
                hal_display.display_multiline([
                    f"Touch {name}",
                    "(Hold for 1 second)"
                ], start_y=screen_y)

            print(f"Waiting for touch at {name}...")

            while not self.tsc.touched:
                pass

            samples = []
            for _ in range(10):
                if self.tsc.touched:
                    point = self.tsc.touch
                    samples.append((point["x"], point["y"]))
                time.sleep(0.05)

            avg_x = sum(p[0] for p in samples) // len(samples)
            avg_y = sum(p[1] for p in samples) // len(samples)
            print(f"{name}: avg_x={avg_x}, avg_y={avg_y}")

            raw_xs.append(avg_x)
            raw_ys.append(avg_y)

            # Wait for user to release
            while self.tsc.touched:
                pass

        self.raw_min_x = min(raw_xs)
        self.raw_max_x = max(raw_xs)
        self.raw_min_y = min(raw_ys)
        self.raw_max_y = max(raw_ys)

        print("Calibration complete.")
        print(f"X: {self.raw_min_x} - {self.raw_max_x}")
        print(f"Y: {self.raw_min_y} - {self.raw_max_y}")

    def draw_debug_overlay(self, group):
        for region in self.regions:
            x1, y1, x2, y2 = region.bounds
            width = x2 - x1
            height = y2 - y1
            rect = Rect(x1, y1, width, height, outline=0x00FF00)
            group.append(rect)

class TouchButton:
    def __init__(self, name, x, y, width, height, label_text, callback):
        self.region = TouchRegion(name, x, y, width, height, callback)
        self.label = label.Label(terminalio.FONT, text=label_text, x=x + 5, y=y + 5, color=0xFFFFFF)
        self.rect = Rect(x, y, width, height, fill=0x222222, outline=0xAAAAAA)

        self._flash_active = False
        self._flash_until = 0
        self._original_fill = self.rect.fill

    def flash(self, duration=0.15):
        self._flash_active = True
        self._flash_until = time.monotonic() + duration
        self.rect.fill = self._dim_color(self._original_fill, factor=0.5)

    def update(self):
        if self._flash_active and time.monotonic() >= self._flash_until:
            self.rect.fill = self._original_fill
            self._flash_active = False

    def _dim_color(self, color: int, factor: float) -> int:
        r = int(((color >> 16) & 0xFF) * factor)
        g = int(((color >> 8) & 0xFF) * factor)
        b = int((color & 0xFF) * factor)
        return (r << 16) | (g << 8) | b

    def attach_to(self, group):
        group.append(self.rect)
        group.append(self.label)

    def register(self, manager: TouchManager):
        self.region.rect = self.rect
        self.region._button_ref = self  # Link back to the button
        manager.add_region(self.region)