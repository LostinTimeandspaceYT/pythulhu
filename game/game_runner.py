from ui_context import UIContext

MAIN_MENU = "main"


class GameRunner:
    def __init__(self, ui_context: UIContext, game):
        self.ui = ui_context
        self.game = game

    def start(self):
        self.ui.set_home(MAIN_MENU)
        panel = self.game.get_panel_pool().get(MAIN_MENU)
        self.ui.cache_panel(MAIN_MENU, panel)
        self.ui.transition_to(MAIN_MENU)
        while not self.ui.should_exit:
            self.ui.manager.poll()
            self.ui.manager.update()
            if self.ui.active_panel and hasattr(self.ui.active_panel, "update"):
                self.ui.active_panel.update()

    def stop(self):
        self.ui.should_exit = True
        if hasattr(self.game, "get_panel_pool"):
            self.game.get_panel_pool().clear()
