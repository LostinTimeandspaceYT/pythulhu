from ui_context import UIContext
from file_manager import FileManager
from game_runner import GameRunner
from panel_pool import PanelPool
from selector_panel import SelectorPanel
from coc_game import CthulhuGame
from coc_character import CthulhuCharacter, PulpCharacter

class GameFactory:
    GAMES = {"call_of_cthulhu": CthulhuGame, "pulp_cthulhu": CthulhuGame}
    def __init__(self, ui_context: UIContext):
        self.ui = ui_context

    def select_character(self, game_key, on_runner_ready):
        characters = list(FileManager.list_characters(game_key))
        selector = SelectorPanel(
            context=self.ui,
            title="Select Character",
            options=characters,
            on_select=lambda character: on_runner_ready(self._build_runner(game_key, character)),
            on_cancel=lambda: self.ui.transition_to("game_selector")
        )
        self.ui.cache_panel("char_selector", selector)
        self.ui.transition_to("char_selector")

    def select_and_build_runner(self, on_runner_ready):
        selector = SelectorPanel(self.ui, "Select Game", list(self.GAMES.keys()), on_select=lambda game: self.select_character(game, on_runner_ready))
        self.ui.cache_panel("game_selector", selector)
        self.ui.transition_to("game_selector")

    def _build_runner(self, game_key: str, character_name: str) -> GameRunner:
        character_path = FileManager.get_character_path(game_key, character_name)
        character = PulpCharacter(character_path)
        game = self.GAMES[game_key]()
        game.bind_character(character)
        game.setup_panels(self.ui)
        return GameRunner(
            ui_context=self.ui,
            game=game,
        )

