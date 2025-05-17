import gc
from time import sleep
from player_character import PlayerCharacter
from touch_ui import TouchManager
from hardware import HAL

class UIContext:
    def __init__(self, hal, manager, character, nav_buttons):
        self.hal: HAL = hal
        self.manager: TouchManager = manager
        self.character: PlayerCharacter = character
        self.nav_buttons = nav_buttons
        self.active_panel = None
        self.home = None
        self.should_exit = False
        self.panel_cache = {}  # keyed by name/type

    def get_cached_panel(self, name):
        return self.panel_cache.get(name)

    def cache_panel(self, name, panel):
        self.panel_cache[name] = panel

    def release_panel(self, name):
        panel = self.panel_cache.pop(name, None)
        if panel:
            panel.detach_from()
            del panel
            gc.collect()

    def clear_cached_panels(self):
        for name in list(self.panel_cache.keys()):
            self.release_panel(name)

    def get_panel(self, name: str):
        return self.panel_cache.get(name)

    def switch_to(self, name: str):
        next_panel = self.get_panel(name)
        if not next_panel:
            return
        if self.active_panel:
            self.active_panel.detach_from()
        self.active_panel = next_panel
        next_panel.attach_to()

    def transition_to(self, name: str, delay_secs: float=0.5):
        gc.collect()
        if self.active_panel:
            self.active_panel.detach_from()
            self.active_panel = None
        if delay_secs > 0.0:
            sleep(delay_secs)
        self.switch_to(name)


    def set_home(self, name: str):
        self.home = name

    def return_home(self):
        if self.home:
            self.transition_to(self.home)
        else:
            self.transition_to("main")

    def hide_nav_button(self, name: str):
        btn = self.nav_buttons.get(name)
        if btn:
            btn.remove_from(self.hal.root_group)
            self.manager.unregister(btn)

    def show_nav_button(self, name: str, callback=None):
        btn = self.nav_buttons.get(name)
        if btn:
            if callback:
                btn.callback = callback
            btn.attach_to(self.hal.root_group)
            btn.register(self.manager)

    def reset(self):
        self.hal.clear_display()
        gc.collect()
        self.hal.reset_display()
        self.manager.buttons.clear()

