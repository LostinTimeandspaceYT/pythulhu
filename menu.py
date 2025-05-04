import displayio
from touch_ui import TouchButton
import gc

class Menu:
    def __init__(self, name: str, buttons: list, hal, manager, background_color=0x000000):
        self.name = name
        self.buttons = buttons
        self.hal = hal
        self.manager = manager
        self.group = displayio.Group()

        if background_color is not None:
            bg = displayio.Bitmap(320, 240, 1)
            palette = displayio.Palette(1)
            palette[0] = background_color
            tile = displayio.TileGrid(bg, pixel_shader=palette, x=0, y=0)
            self.group.append(tile)

        for button in self.buttons:
            button.attach_to(self.group)

    def show(self):
        self.hal.clear_display()
        gc.collect()
        self.hal.display.root_group = self.group
        for button in self.buttons:
            button.register(self.manager)


class PagedMenu:
    def __init__(
        self,
        name: str,
        lines: list[str],
        hal,
        manager,
        on_back=None,
        page_size=10,
        line_height=16
    ):
        self.name = name
        self.lines = lines
        self.hal = hal
        self.manager = manager
        self.on_back_callback = on_back
        self.page_size = page_size
        self.line_height = line_height
        self.page = 0
        self.total_pages = (len(lines) + page_size - 1) // page_size

    def show(self):
        self.hal.clear_display()
        gc.collect()
        self.hal.reset_display()
        self.manager.buttons.clear()

        start = self.page * self.page_size
        end = min(start + self.page_size, len(self.lines))
        visible = self.lines[start:end]
        self.hal.display_multiline(visible, start_y=10, line_height=self.line_height)

        nav_y = 200

        if self.page > 0:
            prev = TouchButton("prev", 10, nav_y, 100, 30, "Prev", callback=self.prev_page)
            prev.attach_to(self.hal.root_group)
            prev.register(self.manager)

        if self.page < self.total_pages - 1:
            nxt = TouchButton("next", 210, nav_y, 100, 30, "Next", callback=self.next_page)
            nxt.attach_to(self.hal.root_group)
            nxt.register(self.manager)

        back = TouchButton("back", 110, nav_y, 100, 30, "Back", callback=self.on_back)
        back.attach_to(self.hal.root_group)
        back.register(self.manager)

    def prev_page(self, button):
        self.page -= 1
        self.show()

    def next_page(self, button):
        self.page += 1
        self.show()

    def on_back(self, button):
        if self.on_back_callback:
            self.on_back_callback(button)