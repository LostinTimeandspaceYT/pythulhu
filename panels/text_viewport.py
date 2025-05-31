import displayio
from adafruit_display_text.label import Label
import terminalio

class TextViewport:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        max_lines: int = 5,
        line_height: int = 14,
        show_background: bool = True,
        background_color: int = 0x000000,
        text_color: int = 0xFFFFFF,
    ):
        self.group = displayio.Group(x=x, y=y)
        self.labels = []
        self.line_height = line_height
        self.max_lines = max_lines

        if show_background:
            bg_bitmap = displayio.Bitmap(width, height, 1)
            palette = displayio.Palette(1)
            palette[0] = background_color
            tile = displayio.TileGrid(bg_bitmap, pixel_shader=palette, x=0, y=0)
            self.group.append(tile)

        for i in range(max_lines):
            label = Label(
                terminalio.FONT,
                text="",
                color=text_color,
                x=6,
                y=i * line_height + 4
            )
            self.group.append(label)
            self.labels.append(label)

    def set_lines(self, lines: list[str]):
        for i in range(self.max_lines):
            self.labels[i].text = lines[i] if i < len(lines) else ""
