import gc
import time
from hardware import HAL
from touch_ui import TouchManager, TouchButton
from coc_character import PulpCharacter
from file_manager import FileManager
from calibrator import Calibrator

# FileManager.mount_sdcard()
# ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
# ana = PulpCharacter(ana_path)
# print(ana)

HAL.init()
touch_ui = TouchManager(HAL.tsc)
touch_ui.draw_coordinate_overlay(HAL.root_group)

# Callback
def on_pressed(btn):
    print(f"{btn.name} pressed!")
    print(HAL.get_touch())

btn_inv = TouchButton("inventory", 20, 100, 67, 50, "Inventory", on_pressed, toggle=True)
btn_inv.attach_to(HAL.root_group)
btn_inv.register(touch_ui)
btn_inv.show_debug_bounds(HAL.root_group)

btn_stats = TouchButton("stats", 20, 180, 67, 50, "Stats", on_pressed, toggle=True)
btn_stats.attach_to(HAL.root_group)
btn_stats.register(touch_ui)

# Showing the items on the screen
HAL.display.root_group = HAL.root_group

while True:
    touch_ui.poll()
    touch_ui.update()
    # time.sleep(0.025)
    # if HAL.tsc.touched:
    #     point = HAL.tsc.touch
    #     if point:
    #         scaled = touch_ui.scale_touch(point["x"], point["y"])
    #         TouchButton.draw_touch_marker(HAL.root_group, *scaled)
    