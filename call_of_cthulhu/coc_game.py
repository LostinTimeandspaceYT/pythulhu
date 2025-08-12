from call_of_cthulhu.coc_characteristics_panel import CthulhuCharacteristicsPanel
from call_of_cthulhu.coc_development_panel import CthulhuDevelopmentPhasePanel
from call_of_cthulhu.coc_dice import CthulhuDice
from call_of_cthulhu.coc_equipment_panel import CthulhuEquipmentPanel
from call_of_cthulhu.coc_roll_params import CthulhuRollParams
from call_of_cthulhu.coc_sanity_roll_panel import CthulhuSanityRollPanel
from call_of_cthulhu.coc_skills_panel import CthulhuSkillsPanel
from call_of_cthulhu.coc_stats_panel import CthulhuStatsPanel
from call_of_cthulhu.coc_combat_roll_panel import CthulhuCombatRollPanel
from game.roll_result import RollResult
from panels.main_menu_panel import MainMenuPanel
from panels.panel_pool import PanelPool
from touch_ui import LightTouchButton

BUTTON_WIDTH = 220
BUTTON_HEIGHT = 30
BUTTON_LEFT = 25
BUTTON_CENTER = 80
BUTTON_RIGHT = 120


class CthulhuGame:
    _instance = None

    DIFFICULTY_LEVELS = {"Normal": 1, "Hard": 2, "Extreme": 3}

    SUCCESS_LEVELS = {
        "Fumble": -1,
        "Fail": 0,
        "Normal": 1,
        "Hard": 2,
        "Extreme": 3,
        "Critical": 4,
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
        buttons = [
            LightTouchButton(
                "skills",
                BUTTON_LEFT,
                BUTTON_HEIGHT,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Skills",
                callback=lambda b: self.open_panel(context, "skills"),
            ),
            LightTouchButton(
                "characteristics",
                BUTTON_RIGHT,
                BUTTON_HEIGHT,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Characteristics",
                callback=lambda b: self.open_panel(context, "characteristics"),
            ),
            LightTouchButton(
                "stats",
                BUTTON_LEFT,
                BUTTON_CENTER,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Stats",
                callback=lambda b: self.open_panel(context, "stats"),
            ),
            LightTouchButton(
                "equipment",
                BUTTON_RIGHT,
                BUTTON_CENTER,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Equipment",
                callback=lambda b: self.open_panel(context, "equipment"),
            ),
            LightTouchButton(
                "development",
                BUTTON_LEFT,
                BUTTON_RIGHT,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Development",
                callback=lambda b: self.open_panel(context, "development"),
            ),
            LightTouchButton(
                "sanity",
                BUTTON_RIGHT,
                BUTTON_RIGHT,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Sanity",
                callback=lambda b: self.open_panel(context, "sanity"),
            ),
            LightTouchButton(
                "combat",
                BUTTON_LEFT,
                BUTTON_RIGHT + 60,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Combat",
                callback=lambda b: self.open_panel(context, "combat"),
            ),
            LightTouchButton(
                "exit",
                BUTTON_RIGHT,
                BUTTON_RIGHT + 60,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Save & Exit",
                callback=lambda b: self.save_and_exit(context),
            ),
        ]
        panel.add_buttons(buttons)
        return panel

    def setup_panels(self, context):
        pool = self.get_panel_pool()
        pool.register_factory("main", lambda: self.build_main_menu(context))
        pool.register_factory("skills", lambda: CthulhuSkillsPanel(self, context))
        pool.register_factory(
            "characteristics", lambda: CthulhuCharacteristicsPanel(self, context)
        )
        pool.register_factory("combat", lambda: CthulhuCombatRollPanel(self, context))
        pool.register_factory("stats", lambda: CthulhuStatsPanel(self, context))
        pool.register_factory("equipment", lambda: CthulhuEquipmentPanel(self, context))
        pool.register_factory("sanity", lambda: CthulhuSanityRollPanel(self, context))
        pool.register_factory(
            "development", lambda: CthulhuDevelopmentPhasePanel(self, context)
        )

    def save_and_exit(self, context):
        if self.character:
            self.character.save()
        context.should_exit = True

    def open_panel(self, context, name: str):
        panel = self.get_panel_pool().get(name)
        context.cache_panel(name, panel)
        context.transition_to(name)

    def perform_luck_refresh(self, result_log=None):
        """Perform a luck refresh for the active character."""
        current = self.character.current_luck
        roll = CthulhuDice.roll(1, 100)
        gained = CthulhuDice.roll(2, 10) if roll > current else CthulhuDice.roll(1, 10)
        self.character.characteristics["Luck"] += gained

        if result_log is not None:
            result_log.append(
                f"Luck Refresh — Rolled {roll}, Gained {gained}, New: {self.character.current_luck}"
            )

    @classmethod
    def roll_skill(self, bonus_die: int, penalty_die: int) -> int:
        return CthulhuDice.roll_skill(bonus_die, penalty_die)

    @classmethod
    def get_diff_level_thresholds(cls, val: int) -> dict:
        return {"Normal": int(val), "Hard": int(val * 0.5), "Extreme": int(val * 0.2)}

    @classmethod
    def get_val_at_threshold(cls, val: int, difficulty: str = "Normal") -> int:
        return cls.get_diff_level_thresholds(val)[difficulty]

    @classmethod
    def is_success(cls, result: RollResult, params: CthulhuRollParams):
        return result.success_level >= cls.DIFFICULTY_LEVELS[params.difficulty]

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

    @classmethod
    def roll_damage(cls, params: CthulhuRollParams):
        pass

    def _parse_damage_spec(self, weapon):
        """
        Returns (dice_list, wants_db)
          - dice_list: list of (num, sides)
          - wants_db: True if the spec includes 'db'
        Accepts weapon['Damage'] as:
          - string like '1d8+db' or '1d6+1d4'
          - tuple (num, sides)
          - list of tuples [(num, sides), ...]
        """
        wants_db = False
        dmg = weapon.get("Damage")

        if dmg is None:
            return ([], False)

        # string like "1d8+db" or "1d6+1d4"
        if isinstance(dmg, str):
            s = dmg.replace(" ", "").lower()
            parts = [p for p in s.split("+") if p]
            dice = []
            for p in parts:
                if p == "db":
                    wants_db = True
                    continue
                if "d" in p:
                    n_str, s_str = p.split("d", 1)
                    try:
                        n = int(n_str) if n_str else 1
                        sides = int(s_str)
                        dice.append((n, sides))
                    except ValueError:
                        # ignore malformed segment
                        continue
                else:
                    # Support constants like "+1" → (1,1) and "-1" → (-1,1)
                    try:
                        k = int(p)
                        dice.append((k, 1))
                    except ValueError:
                        continue
            return (dice, wants_db)

        # Non-string formats aren’t expected by contract; return empty
        return ([], False)
