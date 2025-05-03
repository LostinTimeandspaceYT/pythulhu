from hardware import HAL
from coc_character import PulpCharacter
from file_manager import FileManager
from touch_ui import TouchManager, TouchRegion, TouchButton
import time

FileManager.mount_sdcard()

# from sprite_example import run_example
# run_example()

ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)

HAL.init()
print(ana)

last_position = 0
color = 0

touch_ui = TouchManager(HAL.tsc)

def on_inventory_tap(pos):
    print("Touched inventory:", pos)

def on_stats_touch(pos):
    print("Touched stats:", pos)

# NOTE: for a good feel for a region, remember x = 1.33 * y
btn = TouchButton("inventory", 10, 200, 140, 30, "Inventory", on_inventory_tap)
btn.attach_to(HAL.root_group)
btn.register(touch_ui)
# touch_ui.draw_coordinate_overlay(HAL.root_group)
touch_ui.draw_debug_overlay(HAL.root_group)

while True:
    touch_ui.poll()
    touch_ui.update()
    time.sleep(.025)