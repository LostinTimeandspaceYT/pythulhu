import terminalio
import displayio
from adafruit_display_text import label
from hardware import HAL
from coc_character import PulpCharacter
from file_manager import FileManager

FileManager.mount_sdcard()
ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)

HAL.draw_main_background()

# Draw a label
text_group = displayio.Group(scale=3, x=40, y=40)
text = f"{ana.name}"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
text_group.append(text_area)  # Subgroup for text scaling
HAL.main_splash().append(text_group)

# Draw another label
pos_text_group = displayio.Group(scale=2, x=40, y=80)
pos_text = "Skill:"
pos_text_area = label.Label(terminalio.FONT, text=pos_text, color=0xFFFF00)
pos_text_group.append(pos_text_area)
HAL.main_splash().append(pos_text_group)

last_position = -1
color = 0  # start at red

while True:
    # negate the position to make clockwise rotation positive
    position = -HAL.get_encoder_position()

    if position != last_position:
        tmp = position % len(ana.skills)
        pos_text_area.text = f"{ana.skills[tmp]}: {ana.get_value_at(ana.skills[tmp])}"
        if not HAL.is_button_pressed():
            # Change the LED color.
            if position > last_position:  # Advance forward through the colorwheel.
                color += 1
            else:
                color -= 1  # Advance backward through the colorwheel.
            color = (color + 256) % 256  # wrap around to 0-256
            HAL.fill_all_pixels(color)

        else:  # If the button is pressed...
            # ...change the brightness.
            pos_text_area.text += f"\nRolled: {ana.roll_skill(0,0)}"
            if position > last_position:
                HAL.increase_all_pixel_brightness()

            else:
                HAL.decrease_all_pixel_brightness()

    last_position = position
