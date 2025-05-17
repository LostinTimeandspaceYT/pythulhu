import gc
from time import sleep

class UIContext:
    def __init__(self, hal, manager, character, nav_buttons):
        self.hal = hal
        self.manager = manager
        self.character = character
        self.nav_buttons = nav_buttons
        self.active_panel = None
        self.panels = {}
        self.panel_stack = []
        self.home = None
        self.should_exit = False

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
        self.active_panel = next_panel
        next_panel.attach_to()

    def transition_to(self, name: str, delay_secs: float=0.5):
        gc.collect()
        if self.active_panel:
            self.active_panel.detach_from()
            self.panel_stack.append(self.active_panel)
            self.active_panel = None
        if delay_secs > 0.0:
            sleep(delay_secs)
        self.switch_to(name)

    def transition_with_effect(self, name: str, effect_callback):
        gc.collect()
        if self.active_panel:
            self.active_panel.detach_from()
            self.panel_stack.append(self.active_panel)
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
        if self.panel_stack:
            self.active_panel = self.panel_stack.pop()
            self.active_panel.attach_to()

    def clear_panel_stack(self):
        self.panel_stack.clear()

    def set_home(self, name: str):
        if name in self.panels:
            self.home = name
        else:
            raise ValueError(f"Panel {name} is not registered")

    def return_home(self):
        self.panel_stack.clear()
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

