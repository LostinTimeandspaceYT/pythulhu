import gc
from hardware import HAL
from touch_ui import TouchManager, TouchButton, LightTouchButton
from coc_character import PulpCharacter
from file_manager import FileManager
from menu import Menu, PagedMenu
from character_summary import CharacterSummaryPanel
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

    panel = SkillsPanel(context)
    panel.show()
    context.active_panel = panel

    nav_buttons["prev"].callback = lambda b: panel.prev_page()
    nav_buttons["next"].callback = lambda b: panel.next_page()
    nav_buttons["back"].callback = go_to_menu("main")
    activate_nav_buttons("prev", "next", "back")

def show_character_sections_menu(button):
    context.reset()

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
        paged_menu = PagedMenu(
            name=section,
            lines=ana.get_section_lines(section),
            hal=HAL,
            manager=manager,
            on_back=show_character_sections_menu
        )
        paged_menu.show()
    return handler

def show_character_sheet_menu(button):

    context.reset()

    summary_panel = CharacterSummaryPanel(ana)
    summary_panel.show(HAL)
    context.active_panel = summary_panel

    back_button = TouchButton("back", 90, 200, 140, 30, "Back", callback=go_to_menu("main"))
    back_button.attach_to(HAL.root_group)
    back_button.register(manager)

# Define menus
main_buttons = [
    TouchButton("skills", 50, 80, 220, 30, "Skills", callback=show_skills_menu),
    TouchButton("quit", 50, 130, 220, 30, "Quit", callback=lambda b: print("Quit"))
]

menus["main"] = Menu("Main", main_buttons, hal=HAL, manager=manager)

# Show initial screen
menus["main"].show()

while True:
    manager.poll()
    manager.update()

    if context.active_panel and hasattr(context.active_panel, "update"):
        context.active_panel.update()
