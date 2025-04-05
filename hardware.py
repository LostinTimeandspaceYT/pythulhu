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
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

# Configure seesaw pin used to read knob button presses
# The internal pull up is enabled to prevent floating input
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

# TODO: Game Interface component
button = digitalio.DigitalIO(seesaw, 24)
encoder = rotaryio.IncrementalEncoder(seesaw)
pixel = neopixel.NeoPixel(seesaw, 6, 1)
pixel.brightness = 0.5

# Metro's on-board Neopixel
# TODO: Game Interface component
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

# TODO: Game Interface component
display = adafruit_ili9341.ILI9341(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Make the display context
main_splash = displayio.Group()
display.root_group = main_splash

irq_dio = None
tsc = adafruit_tsc2007.TSC2007(board.I2C(), irq=irq_dio)


# TODO: refactor to use Adafuit Slideshow.
def show_title_touch_screen():
    logo = FileManager.get_image_path("LogoLTS")
    pythulhu = FileManager.get_image_path("pythulhu")
    splash = displayio.Group()
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
                    displayio.release_displays()
                    break

            display.root_group = groups[index]
        if not tsc.touched and touch_state:
            touch_state = False
