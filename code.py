import gc
from hardware import HAL
from touch_ui import TouchManager, TouchButton
from coc_character import PulpCharacter
from file_manager import FileManager
from menu import Menu, PagedMenu

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
        menus[menu_name].show()
    return inner_callback

def show_character_sections_menu(button):
    HAL.clear_display()
    gc.collect()
    HAL.reset_display()
    manager.buttons.clear()

    section_names = ana.get_sections()
    buttons = []
    for i, section in enumerate(section_names):
        btn = TouchButton(
            name=f"section_{section}",
            x=50,
            y=30 + i * 40,
            width=220,
            height=30,
            label_text=section,
            callback=show_section_detail(section)
        )
        btn.attach_to(HAL.root_group)
        btn.register(manager)
        buttons.append(btn)

    back_btn = TouchButton("back", 90, 200, 140, 30, "Back", callback=go_to_menu("main"))
    back_btn.attach_to(HAL.root_group)
    back_btn.register(manager)

def show_section_detail(section):
    def handler(button):
        lines = ana.get_section_lines(section)
        paged_menu = PagedMenu(
            name=section,
            lines=lines,
            hal=HAL,
            manager=manager,
            on_back=show_character_sections_menu
        )
        paged_menu.show()
    return handler

def show_character_sheet_menu(button):
    HAL.clear_display()
    gc.collect()
    HAL.reset_display()
    lines = ana.render_summary_lines()
    HAL.display_multiline(lines, start_y=10, line_height=12)

    back_button = TouchButton("back", 90, 200, 140, 30, "Back", callback=go_to_menu("main"))
    back_button.attach_to(HAL.root_group)
    back_button.register(manager)

# Define menus
main_buttons = [
    TouchButton("summary", 50, 30, 220, 30, "Summary", callback=show_character_sheet_menu),
    TouchButton("sections", 50, 80, 220, 30, "Sections", callback=show_character_sections_menu),
    TouchButton("quit", 50, 130, 220, 30, "Quit", callback=lambda b: print("Quit"))
]

menus["main"] = Menu("Main", main_buttons, hal=HAL, manager=manager)

# Show initial screen
menus["main"].show()

while True:
    manager.poll()
    manager.update()
