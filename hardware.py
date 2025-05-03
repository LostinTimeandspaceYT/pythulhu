import board
import displayio
import adafruit_tsc2007
import adafruit_ili9341
import terminalio
from adafruit_imageload import load as load_image
from adafruit_display_text import label
import neopixel as np
from file_manager import FileManager
from time import sleep

# For the rotary Encoder
from rainbowio import colorwheel
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel

# Support both 8.x.x and 9.x.x. Change when 8.x.x is discontinued as a stable release.
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

DEBUG = False

# Release any resources currently in use for the displays
displayio.release_displays()
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
COLORS = {
    "fail": 0xFF0000,
    "success": 0x00FF00,
    "neutral": 0xFFFFFF,
    "skill": 0x0000FF
}

class HAL:
    """
    The HAL acts as the primary interface between a game's logic and the hardware.
    This isn't a HAL in the traditional sense, but serves a similar purpose here.

    TODO: Decide how games should display stuff.
    TODO: Add touch screen interface.
    """
    seesaw = None
    display = None
    root_group = None
    encoder = None
    button = None
    pixel = None
    board_pixel = None
    tsc = None
    irq_dio = None

    @classmethod
    def init(cls):
        cls.seesaw = seesaw.Seesaw(board.STEMMA_I2C(), addr=0x36)
        seesaw_product = (cls.seesaw.get_version() >> 16) & 0xFFFF
        if DEBUG:
            print("Found product {}".format(seesaw_product))
            if seesaw_product != 4991:
                print("Wrong firmware loaded?  Expected 4991")

        # Configure seesaw pin used to read knob button presses
        # The internal pull up is enabled to prevent floating input
        cls.seesaw.pin_mode(24, cls.seesaw.INPUT_PULLUP)

        # Initialize Rotary Encoder
        cls.button = digitalio.DigitalIO(cls.seesaw, 24)
        cls.encoder = rotaryio.IncrementalEncoder(cls.seesaw)
        cls.pixel = neopixel.NeoPixel(cls.seesaw, 6, 1)
        cls.pixel.brightness = 0.5

        # Metro's on-board Neopixel
        cls.board_pixel = np.NeoPixel(board.NEOPIXEL, 1)
        cls.board_pixel.brightness = 0.5

        # Initialize Display
        spi = board.SPI()
        tft_cs = board.D10
        tft_rst = board.D6
        tft_dc = board.D9
        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
        cls.display = adafruit_ili9341.ILI9341(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
        cls.root_group = displayio.Group()
        cls.display.root_group = cls.root_group 
        cls.irq_dio = None
        cls.tsc = adafruit_tsc2007.TSC2007(board.I2C(), irq=cls.irq_dio)

    @classmethod
    def rotate_display(cls, degrees: int)-> None:
        cls.display.rotation = degrees

    @classmethod
    def clear_display(cls):
        while len(cls.root_group) > 0:
            cls.root_group.pop()

    @classmethod
    def reset_display(cls):
        cls.root_group = displayio.Group()
        cls.display.root_group = cls.root_group  # reattach if necessary

    @classmethod
    def clear_text(cls):
        for group in cls.display.root_group:
            if isinstance(group[0], label.Label):
                group[0].text = ""

    @classmethod
    def display_text(cls, group_index: int, text: str) -> None:
        cls.ensure_text_group(group_index)
        cls.display.root_group[group_index][0].text = text

    @classmethod
    def display_multiline(cls, lines: list[str], start_y=0, line_height=20):
        cls.clear_display()
        for i, line in enumerate(lines):
            txt = label.Label(terminalio.FONT, text=line, color=0xFFFFFF, x=0, y=start_y + i * line_height)
            cls.display.root_group.append(txt)

    @classmethod
    def display_image(cls, img_name: str) -> None:
        img_path = FileManager.get_image_path(img_name)
        if img_path is not None:
            cls.clear_display()
            bitmap = displayio.OnDiskBitmap(img_path)
            tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
            cls.root_group.append(tile_grid)

    @classmethod
    def create_sprite(cls,
        name: str,
        width: int,
        height: int
    ) -> displayio.TileGrid:

        path = FileManager.get_image_path(name)
        if path is not None:
            sprite_sheet, palette = load_image(path, bitmap=displayio.Bitmap, palette=displayio.Palette)

            sprite = displayio.TileGrid(
                sprite_sheet, 
                pixel_shader=palette,
                width= 1,
                height= 1,
                tile_width= width,
                tile_height=height
            )
            return sprite

    @classmethod
    def ensure_text_group(cls, index: int, color=0xFFFFFF, font=terminalio.FONT, x=0, y=0):
        if len(cls.root_group) <= index:
            for _ in range(index - len(cls.root_group) + 1):
                cls.root_group.append(displayio.Group())
            cls.root_group[index].append(
                label.Label(font=font, text="", color=color, x=x, y=y)
            )

    @classmethod
    def main_splash(cls):
        return cls.root_group

    @classmethod
    def is_button_pressed(cls) -> bool:
        return not cls.button.value

    @classmethod
    def get_encoder_position(cls) -> int:
        return cls.encoder.position

    @classmethod
    def fill_pixel(cls, color: int) -> None:
        cls.pixel.fill(colorwheel(color))

    @classmethod
    def fill_metro_pixel(cls, color: int) -> None:
        cls.board_pixel.fill(colorwheel(color))

    @classmethod
    def fill_all_pixels(cls, color: int) -> None:
        cls.pixel.fill(colorwheel(color))
        cls.board_pixel.fill(colorwheel(color))

    @classmethod
    def increase_all_pixel_brightness(cls) -> None:
        cls.pixel.brightness = min(1.0, cls.pixel.brightness + 0.1)
        cls.board_pixel.brightness = min(1.0, cls.pixel.brightness + 0.1)

    @classmethod
    def decrease_all_pixel_brightness(cls) -> None:
        cls.pixel.brightness = max(0, cls.pixel.brightness - 0.1)
        cls.board_pixel.brightness = max(0, cls.pixel.brightness - 0.1)

    @classmethod
    def get_touch(cls):
        if cls.tsc.touched:
            point = cls.tsc.touch
            return (point["x"], point["y"])
        return None

    @classmethod
    def draw_main_background(cls):
        """
        Draws the default background to the display.
        NOTE: The display defaults to potrait mode layout.

        TODO: allow for customization
        """
        # Draw a green background
        color_bitmap = displayio.Bitmap(DISPLAY_HEIGHT, DISPLAY_WIDTH, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0x00FF00  # Bright Green

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

        cls.root_group.append(bg_sprite)

        # Draw a smaller inner rectangle
        inner_bitmap = displayio.Bitmap(220, 150, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0xAA0088  # Purple
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=10, y=10)
        cls.root_group.append(inner_sprite)
        cls.display.rotation = 270

    @classmethod
    def show_credits_screen(cls):
        # TODO: refactor to use Adafuit Slideshow.
        logo = FileManager.get_image_path("LogoLTS")
        pythulhu = FileManager.get_image_path("pythulhu")
        groups = []
        images = [logo, pythulhu]

        for i in range(len(images)):
            splash = displayio.Group()
            bitmap = displayio.OnDiskBitmap(images[i])
            tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
            splash.append(tile_grid)
            groups.append(splash)

        index = 0
        touch_state = False
        cls.display.root_group = groups[index]
        while True:
            if cls.tsc.touched and not touch_state:
                point = cls.tsc.touch
                touch_state = True
                if point["pressure"] < 200:  # ignore touches with no 'pressure' as false
                    continue

                # left side of the screen
                if point["y"] < 2000:
                    index = (index - 1) % len(images)
                # right side of the screen
                else:
                    index = (index + 1) % len(images)
                    if (index == 0):
                        break

                cls.display.root_group = groups[index]
            if not cls.tsc.touched and touch_state:
                touch_state = False
