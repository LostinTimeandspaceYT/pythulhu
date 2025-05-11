import gc
from time import sleep

class UIContext:
    def __init__(self, hal, manager, character, nav_buttons):
        self.hal = hal
        self.manager = manager
        self.character = character
        self.nav_buttons = nav_buttons
        self.active_panel = None
        self.prev_panel = None
        self.panels = {}

    def register_panel(self, name: str, panel) -> None:
        self.panels[name] = panel

    def get_panel(self, name: str):
        return self.panels.get(name)

    def switch_to(self, name: str):
        next_panel = self.get_panel(name)
        if not next_panel:
            return
        if self.active_panel:
            self.active_panel.detach_from()
            self.prev_panel = self.active_panel
        self.active_panel = next_panel
        next_panel.attach_to()

    def transition_to(self, name: str, delay_secs: float=0.5):
        gc.collect()
        if self.active_panel:
            self.active_panel.detach_from()
            self.prev_panel = self.active_panel
            self.active_panel = None
        if delay_secs > 0.0:
            sleep(delay_secs)
        self.switch_to(name)

    def transition_with_effect(self, name: str, effect_callback):
        gc.collect()
        if self.active_panel:
            self.active_panel.detach_from()
            self.prev_panel = self.active_panel
            self.active_panel = None
        if effect_callback is not None:
            effect_callback()

    def transition_back(self, delay_secs: float=0.5):
        gc.collect()
        if self.active_panel:
            self.active_panel.detach_from()
            self.active_panel = None
        if delay_secs > 0.0:
            sleep(delay_secs)
        if self.prev_panel:
            self.active_panel, self.prev_panel = self.prev_panel, self.active_panel
            self.active_panel.attach_to()

    def go_back(self):
        if self.active_panel:
            self.active_panel.detach_from()

        if self.prev_panel:
            self.active_panel, self.prev_panel = self.prev_panel, self.active_panel
            self.active_panel.attach_to()

    def reset(self):
        self.hal.clear_display()
        gc.collect()
        self.hal.reset_display()
        self.manager.buttons.clear()

