from hardware import HAL
from coc_character import PulpCharacter
from file_manager import FileManager
from time import sleep

FileManager.mount_sdcard()

# from sprite_example import run_example
# run_example()

ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)

HAL.init()
print(ana)

last_position = 0
color = 0

while True:
    # negate the position to make clockwise rotation positive
    position = -HAL.get_encoder_position()

    if position != last_position:
        tmp = position % len(ana.skills)
        print(f"{ana.skills[tmp]}: {ana.get_value_at(ana.skills[tmp])}")
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
            if position > last_position:
                HAL.increase_all_pixel_brightness()

            else:
                HAL.decrease_all_pixel_brightness()

    last_position = position
