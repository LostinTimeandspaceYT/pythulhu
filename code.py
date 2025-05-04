from hardware import HAL
from touch_ui import TouchManager, TouchButton
from coc_character import PulpCharacter
from file_manager import FileManager
from menu import Menu

# NOTE: Order is important here!
FileManager.mount_sdcard()
HAL.init()
manager = TouchManager(HAL.tsc)
HAL.display.root_group = HAL.root_group

ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)
print(ana)

# Showing the items on the screen
menus = {}

def go_to_menu(menu_name):
    def inner_callback(button):
        menus[menu_name].show(HAL, manager)
    return inner_callback

def show_character_sheet_menu(button):
    HAL.clear_display()
    HAL.reset_display()
    lines = ana.render_summary_lines()
    HAL.display_multiline(lines, start_y=0, line_height=16)

    back_button = TouchButton("back", 90, 200, 140, 30, "Back", callback=go_to_menu("main"))
    back_button.attach_to(HAL.root_group)
    back_button.register(manager)

# Define menus
main_buttons = [
    TouchButton("char", 50, 50, 220, 40, "Character", callback=show_character_sheet_menu),
    TouchButton("quit", 50, 120, 220, 40, "Quit", callback=lambda b: print("Quit"))
]

menus["main"] = Menu("Main", main_buttons)

# Show initial screen
menus["main"].show(HAL, manager)

while True:
    manager.poll()
    manager.update()
