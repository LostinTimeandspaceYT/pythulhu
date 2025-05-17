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
        pass

    def select_character(self, game_key):
        characters = list(FileManager.list_characters(game_key))
        selector = SelectorPanel(
            context=self.ui,
            title="Select Character",
            options=characters,
            on_select=lambda character: self._finalize_runner(game_key, character)
        )
        self.ui.cache_panel("char_selector", selector)
        self.ui.transition_to("char_selector")

    def select_and_build_runner(self):
        selector = SelectorPanel(self.ui, "Select Game", list(self.GAMES.keys()), on_select=lambda game: self.select_character(game))
        self.ui.cache_panel("game_selector", selector)
        self.ui.transition_to("game_selector")

    def _finalize_runner(self, game_key: str, character_name: str):
        character_path = FileManager.get_character_path(game_key, character_name)
        # TODO: pass in path to Game Runner?
        character = PulpCharacter(character_path)  # or whatever type is right

        game = self.games[game_key]()
        pool = PanelPool()

        runner = GameRunner(
            name=game_key,
            ui_context=self.ui,
            panel_pool=pool,
            game_rules=game,
            character=character
        )
        self.ui.cache_panel("runner", runner)
        self.ui.transition_to("runner")
