import displayio


class Menu:
    def __init__(self, name: str, buttons: list, background_color=0x000000):
        self.name = name
        self.group = displayio.Group()
        self.buttons = buttons

        # Optional: add a background
        if background_color is not None:
            bg = displayio.Bitmap(320, 240, 1)
            palette = displayio.Palette(1)
            palette[0] = background_color
            tile = displayio.TileGrid(bg, pixel_shader=palette, x=0, y=0)
            self.group.append(tile)

        # Attach buttons to group
        for button in self.buttons:
            button.attach_to(self.group)

    def show(self, hal, manager):
        hal.clear_display()
        hal.display.root_group = self.group
        for button in self.buttons:
            button.register(manager)
