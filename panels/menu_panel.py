import displayio
from panels.base_panel import BasePanel


class MenuPanel(BasePanel):
    def __init__(self, context, buttons: list, background_color=0x000000):
        super().__init__(context)
        self.buttons = buttons

        if background_color is not None:
            bg = displayio.Bitmap(320, 240, 1)
            palette = displayio.Palette(1)
            palette[0] = background_color
            tile = displayio.TileGrid(bg, pixel_shader=palette, x=0, y=0)
            self.group.append(tile)

        for button in self.buttons:
            button.attach_to(self.group)

    def attach_to(self):
        super().attach_to()
        self.manager.buttons.clear()
        for button in self.buttons:
            button.register(self.manager)


class PagedMenuPanel(BasePanel):
    def __init__(self, context, lines: list[str], page_size=10, line_height=16):
        super().__init__(context)
        self.lines = lines
        self.page_size = page_size
        self.line_height = line_height
        self.page = 0
        self.total_pages = (len(lines) + page_size - 1) // page_size

    def attach_to(self):
        super().attach_to()
        self.render_page()

    def render_page(self):
        self.hal.clear_display()
        self.manager.buttons.clear()

        start = self.page * self.page_size
        end = min(start + self.page_size, len(self.lines))
        visible = self.lines[start:end]
        self.hal.display_multiline(visible, start_y=10, line_height=self.line_height)

        if self.page > 0:
            self.context.show_nav_button("prev", self.prev_page)
        else:
            self.context.hide_nav_button("prev")

        if self.page < self.total_pages - 1:
            self.context.show_nav_button("next", self.next_page)
        else:
            self.context.hide_nav_button("next")

        self.context.show_nav_button("back", self.context.go_back)

    def prev_page(self, button):
        self.page -= 1
        self.render_page()

    def next_page(self, button):
        self.page += 1
        self.render_page()

    def reset(self, lines=None):
        if lines:
            self.lines = lines
            self.page = 0
            self.total_pages = (len(lines) + self.page_size - 1) // self.page_size
