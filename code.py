import gc
from hardware import HAL
from touch_ui import TouchManager, LightTouchButton
from coc_character import PulpCharacter
from file_manager import FileManager
from menu import Menu
from skills_panel import SkillsPanel
from ui_context import UIContext

# NOTE: Order is important here!
FileManager.mount_sdcard()
HAL.init()
manager = TouchManager(HAL.tsc)
HAL.display.root_group = HAL.root_group

ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)

nav_buttons = {
    "prev": LightTouchButton("prev", 10, 200, 80, 30, "Prev"),
    "next": LightTouchButton("next", 230, 200, 80, 30, "Next"),
    "back": LightTouchButton("back", 110, 200, 100, 30, "Back"),
}

# Showing the items on the screen
menus = {}

context = UIContext(
    hal=HAL,
    manager=manager,
    character=ana,
    nav_buttons=nav_buttons
)

def activate_nav_buttons(*names):
    for name, btn in nav_buttons.items():
        if name in names:
            btn.attach_to(HAL.root_group)
            btn.register(manager)
        else:
            btn.remove_from(HAL.root_group)
            btn.unregister(manager)

def go_to_menu(menu_name):
    def inner_callback(button):
        menus[menu_name].show()
    return inner_callback

def show_skills_menu(button):
    HAL.clear_display()
    gc.collect()
    HAL.reset_display()
    manager.buttons.clear()

    panel = context.get_panel("skills")
    if panel is None:
        panel = SkillsPanel(context)
        context.register_panel("skills", panel)

    context.switch_to("skills")

    nav_buttons["prev"].callback = lambda b: panel.prev_page()
    nav_buttons["next"].callback = lambda b: panel.next_page()
    nav_buttons["back"].callback = lambda b: context.transition_back()
    activate_nav_buttons("prev", "next", "back")

# Define menus
main_buttons = [
    LightTouchButton("skills", 50, 80, 220, 30, "Skills", callback=show_skills_menu),
    LightTouchButton("quit", 50, 130, 220, 30, "Quit", callback=lambda b: print("Quit"))
]

menus["main"] = Menu("Main", main_buttons, hal=HAL, manager=manager)

# Show initial screen
menus["main"].show()

while True:
    manager.poll()
    manager.update()

    if context.active_panel and hasattr(context.active_panel, "update"):
        context.active_panel.update()
