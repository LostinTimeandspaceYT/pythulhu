import board
import terminalio
import displayio
from adafruit_display_text import label
from rainbowio import colorwheel
from hardware import button, display, pixel, board_pixel, encoder, DISPLAY_HEIGHT, DISPLAY_WIDTH, main_splash, tsc
from character_sheet import PulpCharacter
from file_manager import FileManager

FileManager.mount_sdcard()
ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)

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
