from ui_context import UIContext
from panel_pool import PanelPool

class GameRunner:
    def __init__(self, ui_context: UIContext, pool: PanelPool, game):
        self.ui = ui_context
        self.panel_pool = pool
        self.game = game
        self.should_exit = False
        pass

    def start(self):
        self.context.transition_to("home")
        while not self.should_exit:
            self.ui.manager.poll()
            self.ui.manager.update()
            if self.ui.active_panel and hasattr(self.ui.active_panel, "update"):
                self.ui.active_panel.update()
