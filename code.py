import gc
from hardware import HAL
from touch_ui import TouchManager, LightTouchButton
from coc_character import PulpCharacter
from file_manager import FileManager
from menu_panel import MenuPanel
from skills_panel import SkillsPanel
from ui_context import UIContext
import time

# NOTE: Order is important here!
FileManager.mount_sdcard()
HAL.init()
manager = TouchManager(HAL.tsc)

ana_path = FileManager.get_character_path("pulp_cthulhu", "ana_engel")
ana = PulpCharacter(ana_path)
running = True

nav_buttons = {
    "prev": LightTouchButton("prev", 10, 200, 80, 30, "Prev"),
    "next": LightTouchButton("next", 230, 200, 80, 30, "Next"),
    "back": LightTouchButton("back", 110, 200, 100, 30, "Back"),
}

context = UIContext(
    hal=HAL,
    manager=manager,
    character=ana,
    nav_buttons=nav_buttons
)

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

def exit_app(button):
    context.should_exit = True
    HAL.clear_display()
    gc.collect()
    time.sleep(1.0)
    print("Exiting game...")
    # save state, etc.


# Define menus
main_buttons = [
    LightTouchButton("skills", 50, 80, 220, 30, "Skills", callback=show_skills_menu),
    LightTouchButton("quit", 50, 130, 220, 30, "Quit", callback=exit_app)
]

main_menu = MenuPanel(context, main_buttons)
context.register_panel("main", main_menu)
context.transition_to("main")

while not context.should_exit:
    manager.poll()
    manager.update()

    if context.active_panel and hasattr(context.active_panel, "update"):
        context.active_panel.update()
