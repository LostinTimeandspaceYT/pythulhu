import board
import terminalio
import displayio
from adafruit_display_text import label
import adafruit_tsc2007
import adafruit_ili9341
import neopixel as np
from character_sheet import PulpCharacter
from file_manager import FileManager

# For the rotary Encoder
from rainbowio import colorwheel
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel

# Support both 8.x.x and 9.x.x. Change when 8.x.x is discontinued as a stable release.
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
seesaw = seesaw.Seesaw(i2c, addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

# Configure seesaw pin used to read knob button presses
# The internal pull up is enabled to prevent floating input
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)

button_held = False

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

board_pixel = np.NeoPixel(board.NEOPIXEL, 1)
pixel = neopixel.NeoPixel(seesaw, 6, 1)
board_pixel.brightness = 0.5
pixel.brightness = 0.5

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
main_splash = displayio.Group()
display.root_group = main_splash

irq_dio = None
tsc = adafruit_tsc2007.TSC2007(board.I2C(), irq=irq_dio)

FileManager.mount_sdcard()
ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)


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


# show_title_touch_screen()
display.rotation = 270

# Draw a green background
color_bitmap = displayio.Bitmap(DISPLAY_HEIGHT, DISPLAY_WIDTH, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

main_splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(220, 150, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=10, y=10)
main_splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(scale=3, x=40, y=40)
text = f"{ana.name}"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
text_group.append(text_area)  # Subgroup for text scaling
main_splash.append(text_group)

# Draw another label
pos_text_group = displayio.Group(scale=2, x=40, y=80)
pos_text = "Skill:"
pos_text_area = label.Label(terminalio.FONT, text=pos_text, color=0xFFFF00)
pos_text_group.append(pos_text_area)
main_splash.append(pos_text_group)
display.root_group = main_splash

last_position = -1
color = 0  # start at red

while True:
    # negate the position to make clockwise rotation positive
    position = -encoder.position

    if position != last_position:
        tmp = position % len(ana.skills)
        pos_text_area.text = f"{ana.skills[tmp]}: {ana.get_value_at(ana.skills[tmp])}"
        if button.value:
            # Change the LED color.
            if position > last_position:  # Advance forward through the colorwheel.
                color += 1
            else:
                color -= 1  # Advance backward through the colorwheel.
            color = (color + 256) % 256  # wrap around to 0-256
            pixel.fill(colorwheel(color))
            board_pixel.fill(colorwheel(color))

        else:  # If the button is pressed...
            # ...change the brightness.
            if position > last_position:  # Increase the brightness.
                pixel.brightness = min(1.0, pixel.brightness + 0.1)
                board_pixel.brightness = min(1.0, pixel.brightness + 0.1)

            else:  # Decrease the brightness.
                pixel.brightness = max(0, pixel.brightness - 0.1)
                board_pixel.brightness = max(0, pixel.brightness - 0.1)

    last_position = position
