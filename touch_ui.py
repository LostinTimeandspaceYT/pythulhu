import time
import terminalio
import displayio
from adafruit_button import Button
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line


class LightTouchButton:
    def __init__(self, name, x, y, width, height, text, callback=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback

        self.label = Label(
            terminalio.FONT,
            text=text,
            color=0xFFFFFF,
            x=x + 4,
            y=y + 4,
        )

        self.group = displayio.Group()
        self.group.append(self.label)

    def attach_to(self, root_group):
        if self.group not in root_group:
            root_group.append(self.group)

    def remove_from(self, root_group):
        if self.group in root_group:
            root_group.remove(self.group)

    def register(self, manager):
        manager.register(self)

    def unregister(self, manager):
        manager.unregister(self)

    def update(self):
        # TODO: implement later
        pass

    def contains(self, point):
        if not point:
            return False
        px, py = point
        return (
            self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
        )

    def press(self):
        if self.callback:
            self.callback(self)


class TouchButton:
    def __init__(
        self,
        name,
        x,
        y,
        width,
        height,
        label_text,
        callback=None,
        toggle=False,
        group=None,
    ):
        self.name = name
        self.callback = callback
        self.toggleable = toggle
        self.group = group

        # Store dimensions explicitly for robust contains() logic
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.button = Button(
            x=x,
            y=y,
            width=width,
            height=height,
            label=label_text,
            label_font=terminalio.FONT,
            label_color=0xFFFFFF,
            fill_color=0x222222,
            outline_color=0xAAAAAA,
            selected_fill=0x3333FF,
            selected_outline=0xFFFFFF,
            style=Button.RECT,
        )

        self._original_fill = self.button.fill_color
        self._flash_active = False
        self._flash_until = 0

    def flash(self, duration=0.15):
        self._flash_active = True
        self._flash_until = time.monotonic() + duration
        self.button.fill_color = self._dim_color(self._original_fill, 0.5)

    def update(self):
        if self._flash_active and time.monotonic() >= self._flash_until:
            self._flash_active = False
            if not self.toggleable:
                self.button.fill_color = self._original_fill

    def set_toggled(self, state: bool):
        self.button.selected = state

    def is_toggled(self) -> bool:
        return self.button.selected

    def attach_to(self, group):
        if self.group not in group:
            group.append(self.button)

    def register(self, manager):
        manager.add_button(self)

    def unregister(self, manager):
        manager.unregister(self)

    def remove_from(self, group):
        if self.button in group:
            group.remove(self.button)

    def contains(self, point):
        if not point:
            return False
        x, y = point
        return (
            self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
        )

    def debug_touch(self, touch_point):
        x, y = touch_point
        print(f"[{self.name}] Touch at: ({x}, {y})")
        print(
            f"[{self.name}] Button bounds: x={self.x}, y={self.y}, w={self.width}, h={self.height}"
        )
        print(f"[{self.name}] Hit test result: {self.contains((x, y))}")
        print(f"[{self.name}] Selected state: {self.is_toggled()}")

    def show_debug_bounds(self, group, color=0x00FF00):
        dbg = Rect(self.x, self.y, self.width, self.height, outline=color)
        group.append(dbg)

    @staticmethod
    def draw_touch_marker(group, x, y, size=5, color=0xFF0000):
        hline = Line(x - size, y, x + size, y, color=color)
        vline = Line(x, y - size, x, y + size, color=color)
        group.append(hline)
        group.append(vline)

    def _dim_color(self, color: int, factor: float) -> int:
        r = int(((color >> 16) & 0xFF) * factor)
        g = int(((color >> 8) & 0xFF) * factor)
        b = int((color & 0xFF) * factor)
        return (r << 16) | (g << 8) | b


class TouchManager:
    def __init__(self, tsc_device, width=320, height=240):
        self.tsc = tsc_device
        self.buttons = []
        self._touch_active = False
        self.screen_width = width
        self.screen_height = height
        self.flip_x = False
        self.flip_y = True
        self.swap_xy = True

        # Default calibration (can be overridden)
        self.raw_min_x = 350
        self.raw_max_x = 3700
        self.raw_min_y = 250
        self.raw_max_y = 3600

    def register(self, btn):
        if btn not in self.buttons:
            self.buttons.append(btn)

    def unregister(self, btn):
        if btn in self.buttons:
            self.buttons.remove(btn)

    def scale_touch(self, raw_x, raw_y):
        if self.swap_xy:
            raw_x, raw_y = raw_y, raw_x

        norm_x = (raw_x - self.raw_min_x) / (self.raw_max_x - self.raw_min_x)
        norm_y = (raw_y - self.raw_min_y) / (self.raw_max_y - self.raw_min_y)

        if self.flip_x:
            norm_x = 1.0 - norm_x
        if self.flip_y:
            norm_y = 1.0 - norm_y

        screen_x = int(norm_x * self.screen_width)
        screen_y = int(norm_y * self.screen_height)
        return (screen_x, screen_y)

    def draw_coordinate_overlay(self, group):
        self.coord_label = Label(terminalio.FONT, text="", color=0xFF00FF, x=5, y=5)
        group.append(self.coord_label)

    def update_coordinates(self, raw, scaled):
        if hasattr(self, "coord_label"):
            rx, ry = raw
            sx, sy = scaled
            self.coord_label.text = f"raw: {rx},{ry}\nscaled: {sx},{sy}"

    def update(self):
        for button in self.buttons:
            button.update()

    def register_persistent(self, button):
        if button not in self.buttons:
            self.buttons.append(button)
        self.persistent_buttons.append(button)

    def clear_non_persistent(self):
        self.buttons = list(self.persistent_buttons)

    def clear_group_selection(self, group_name: str):
        for button in self.buttons:
            if button.group == group_name:
                button.set_toggled(False)

    def add_button(self, button: TouchButton):
        self.buttons.append(button)

    def unregister(self, btn):
        if btn in self.buttons:
            self.buttons.remove(btn)

    def poll(self):
        if self.tsc.touched:
            if self._touch_active:
                return  # debounce
            self._touch_active = True

            point = self.tsc.touch
            if point is None:
                return

            raw_pos = (point["x"], point["y"])
            screen_pos = self.scale_touch(*raw_pos)
            self.update_coordinates(raw_pos, screen_pos)

            for button in self.buttons:
                if button.contains(screen_pos):
                    if hasattr(button, "toggleable") and button.toggleable:
                        if getattr(button, "group", None):
                            self.clear_group_selection(button.group)
                        button.set_toggled(not button.is_toggled())
                    if hasattr(button, "flash"):
                        button.flash()
                    if button.callback:
                        button.callback(button)
                    return

        else:
            self._touch_active = False


"""DEBUG EXAMPLES:

    time.sleep(0.025)
    if HAL.tsc.touched:
        point = HAL.tsc.touch
        if point:
            scaled = touch_ui.scale_touch(point["x"], point["y"])
            TouchButton.draw_touch_marker(HAL.root_group, *scaled)
"""
