import gc
from hardware import HAL
from touch_ui import TouchManager, LightTouchButton
from file_manager import FileManager
from game_factory import GameFactory
from game_runner import GameRunner
from ui_context import UIContext

# NOTE: Order is important here!
FileManager.mount_sdcard()
HAL.init()
manager = TouchManager(HAL.tsc)
nav_buttons = {
    "prev": LightTouchButton("prev", 10, 200, 80, 30, "Prev"),
    "next": LightTouchButton("next", 230, 200, 80, 30, "Next"),
    "back": LightTouchButton("back", 110, 200, 100, 30, "Back"),
}
context = UIContext(
    hal=HAL,
    manager=manager,
    nav_buttons=nav_buttons
)
gc.collect()

def start_main_menu():
    from game_factory import GameFactory
    from game_runner import GameRunner

    def start_game(runner: GameRunner):
        print("[DEBUG] Game setup complete.")
        runner.start()

    print("[DEBUG] Starting game factory setup...")
    factory = GameFactory(ui_context=context)
    factory.select_and_build_runner(on_runner_ready=start_game)


gc.collect()
print("[DEBUG] Before game factory, mem_free:", gc.mem_free())

# Kick off game AFTER initial boot
start_main_menu()

while not context.should_exit:
    manager.poll()
    manager.update()

    if context.active_panel and hasattr(context.active_panel, "update"):
        context.active_panel.update()
