from game.roll_result import RollResult
from call_of_cthulhu.coc_roll_params import CthulhuRollParams
from panels.panel_pool import PanelPool
from call_of_cthulhu.coc_skills_panel import SkillsPanel
from panels.main_menu_panel import MainMenuPanel
from call_of_cthulhu.coc_characteristics_panel import CthulhuCharacteristicsPanel
from touch_ui import LightTouchButton

class CthulhuGame:
    _instance = None

    DIFFICULTY_LEVELS = {
        "Normal": 1,
        "Hard": 2,
        "Extreme": 3
    }

    SUCCESS_LEVELS = {
        "Fumble": -1,
        "Fail": 0,
        "Normal": 1,
        "Hard": 2,
        "Extreme": 3,
        "Critical": 4
    }

    # Singleton in Python
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CthulhuGame, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Use bind_x to attach.
        self.character = None
        self._panels = PanelPool()

    def bind_character(self, character):
        self.character = character

    def get_panel_pool(self):
        return self._panels

    def build_main_menu(self, context):
        panel = MainMenuPanel(context)

        # Add game-specific buttons
        btns = []
        skill_btn = LightTouchButton("skills", 50, 60, 220, 30, "Skills", callback=lambda b: self.open_skills_panel(context))
        btns.append(skill_btn)
        ch_btn = LightTouchButton("characteristics", 120, 60, 220, 30, "Characteristics", callback=lambda b: self.open_characteristics_panel(context))
        btns.append(ch_btn)
        for btn in btns:
            panel.add_button(btn)
        return panel

    def setup_panels(self, context):
        pool = self.get_panel_pool()
        pool.register_factory("main", lambda: self.build_main_menu(context))
        pool.register_factory("skills", lambda: SkillsPanel(self, context))
        pool.register_factory("characteristics", lambda: CthulhuCharacteristicsPanel(self, context))

    def open_characteristics_panel(self, context):
        panel = self.get_panel_pool().get("characteristics")
        context.cache_panel("characteristics", panel)
        context.transition_to("characteristics")

    def open_skills_panel(self, context):
        panel = self.get_panel_pool().get("skills")
        context.cache_panel("skills", panel)
        context.transition_to("skills")

    @classmethod
    def get_diff_level_thresholds(cls, val: int) -> dict:
        return {
            "Normal": int(val),
            "Hard": int(val * 0.5),
            "Extreme": int(val * 0.2)
        }

    @classmethod
    def get_val_at_threshold(cls, val: int, difficulty: str="Normal") -> int:
        return cls.get_diff_level_thresholds(val)[difficulty]

    @classmethod
    def is_success(cls, result: RollResult, params: CthulhuRollParams):
        return result.success_level >= cls.DIFFICULTY_LEVELS[params.difficulty]

    # TODO: TEST
    @classmethod
    def evaluate_roll(cls, roll, params: CthulhuRollParams) -> RollResult:
        thresholds = cls.get_diff_level_thresholds(params.base_val)

        if (roll >= 96 and params.base_val < 50) or roll == 100:
            outcome = "Fumble"
        elif roll == 1 and params.bonus == 0 and params.penalty == 0:
            outcome = "Critical Success"
        elif roll <= thresholds["Extreme"]:
            outcome = "Extreme Success"
        elif roll <= thresholds["Hard"]:
            outcome = "Hard Success"
        elif roll <= thresholds["Normal"]:
            outcome = "Normal Success"
        else:
            outcome = "Fail"

        level_key = outcome.split()[0]  # "Hard", "Fail", etc.
        level = cls.SUCCESS_LEVELS.get(level_key, 0)

        return RollResult(roll, outcome, level)

    @classmethod
    def get_luck_cost(cls, result: RollResult, threshold: int) -> int | None:
        if result.success_level < 0:
            return None  # Account for fumble
        cost = result.roll - threshold
        return cost if cost > 0 else None
