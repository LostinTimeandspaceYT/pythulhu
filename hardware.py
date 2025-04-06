import board
import displayio
import adafruit_tsc2007
import adafruit_ili9341
import neopixel as np
from file_manager import FileManager

# For the rotary Encoder
from rainbowio import colorwheel
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel

# Support both 8.x.x and 9.x.x. Change when 8.x.x is discontinued as a stable release.
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

seesaw = seesaw.Seesaw(board.STEMMA_I2C(), addr=0x36)
seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF

DEBUG = False
if DEBUG:
    print("Found product {}".format(seesaw_product))
    if seesaw_product != 4991:
        print("Wrong firmware loaded?  Expected 4991")

# Configure seesaw pin used to read knob button presses
# The internal pull up is enabled to prevent floating input
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

button = digitalio.DigitalIO(seesaw, 24)
encoder = rotaryio.IncrementalEncoder(seesaw)
pixel = neopixel.NeoPixel(seesaw, 6, 1)
pixel.brightness = 0.5

# Metro's on-board Neopixel
board_pixel = np.NeoPixel(board.NEOPIXEL, 1)
board_pixel.brightness = 0.5

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D10
tft_rst = board.D6
tft_dc = board.D9

DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = adafruit_ili9341.ILI9341(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Make the display context
# TODO: Decide if main_splash should be global
main_display_group = displayio.Group()
display.root_group = main_display_group

irq_dio = None
# TODO: Game interface component
tsc = adafruit_tsc2007.TSC2007(board.I2C(), irq=irq_dio)


class HAL:
    """
    The HAL acts as the primary interface between a game's logic and the hardware.
    This isn't a HAL in the traditional sense, but serves a similar purpose here.

    TODO: Decide how games should display stuff.
    TODO: Add touch screen interface.
    """

    @classmethod
    def rotate_display(cls, degrees: int)-> None:
        display.rotation = degrees

    @classmethod
    def display_text(cls, group_index: int, text: str) -> None:
        display.root_group[group_index].text = text

    @classmethod
    def display_image(cls, img_name: str) -> None:
        img = FileManager.get_image_path(img_name)
        if img is not None:
            splash = displayio.Group()
            bitmap = displayio.OnDiskBitmap(img)
            tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
            splash.append(tile_grid)
            display.root_group = splash

    @classmethod
    def main_splash(cls):
        return display.root_group

    @classmethod
    def is_button_pressed(cls) -> bool:
        return button.value

    @classmethod
    def get_encoder_position(cls) -> int:
        return encoder.position

    @classmethod
    def fill_pixel(cls, color: int) -> None:
        pixel.fill(colorwheel(color))

    @classmethod
    def fill_metro_pixel(cls, color: int) -> None:
        board_pixel.fill(colorwheel(color))

    @classmethod
    def fill_all_pixels(cls, color: int) -> None:
        pixel.fill(colorwheel(color))
        board_pixel.fill(colorwheel(color))

    @classmethod
    def increase_all_pixel_brightness(cls) -> None:
        pixel.brightness = min(1.0, pixel.brightness + 0.1)
        board_pixel.brightness = min(1.0, pixel.brightness + 0.1)

    @classmethod
    def decrease_all_pixel_brightness(cls) -> None:
        pixel.brightness = max(0, pixel.brightness - 0.1)
        board_pixel.brightness = max(0, pixel.brightness - 0.1)

    @classmethod
    def draw_main_background(cls):
        """
        Draws the default background to the display.
        NOTE: The display defaults to potrait mode layout.

        TODO: allow for customization
        """
        display.root_group = main_display_group

        # Draw a green background
        color_bitmap = displayio.Bitmap(DISPLAY_HEIGHT, DISPLAY_WIDTH, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0x00FF00  # Bright Green

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

        main_display_group.append(bg_sprite)

        # Draw a smaller inner rectangle
        inner_bitmap = displayio.Bitmap(220, 150, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0xAA0088  # Purple
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=10, y=10)
        main_display_group.append(inner_sprite)
        display.rotation = 270

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
        display.root_group = groups[index]
        while True:
            if tsc.touched and not touch_state:
                point = tsc.touch
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

                display.root_group = groups[index]
            if not tsc.touched and touch_state:
                touch_state = False
