import gc

class UIContext:
    def __init__(self, hal, manager, character, nav_buttons):
        self.hal = hal
        self.manager = manager
        self.character = character
        self.nav_buttons = nav_buttons
        self.active_panel = None

    def reset(self):
        self.HAL.clear_display()
        gc.collect()
        self.HAL.reset_display()
        self.manager.buttons.clear()

