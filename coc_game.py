from roll_result import RollResult
from coc_roll_params import CthulhuRollParams

class CthulhuGame:
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
    def evaluate_roll(cls, roll, params: CthulhuRollParams) -> RollResult:
        thresholds = cls.get_diff_level_thresholds(params.base_val)

        if roll >= 96 and params.base_val < 50 or roll == 100:
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


    # @classmethod
    # def evaluate_roll(cls, roll: int, skill_val: int, bonus=0, penalty=0) -> RollResult:
    #     thresholds = cls.get_diff_level_thresholds(skill_val)

    #     if roll >= 96 and skill_val < 50 or roll == 100:
    #         outcome = "Fumble"
    #     elif roll == 1 and bonus == 0 and penalty == 0:
    #         outcome = "Critical Success"
    #     elif roll <= thresholds["Extreme"]:
    #         outcome = "Extreme Success"
    #     elif roll <= thresholds["Hard"]:
    #         outcome = "Hard Success"
    #     elif roll <= thresholds["Normal"]:
    #         outcome = "Normal Success"
    #     else:
    #         outcome = "Fail"

    #     level_key = outcome.split()[0]  # "Hard", "Fail", etc.
    #     level = cls.SUCCESS_LEVELS.get(level_key, 0)

    #     return RollResult(roll, outcome, level)

    @classmethod
    def get_luck_cost(cls, result: RollResult, threshold: int) -> int | None:
        if result.success_level < 0:
            return None  # Account for fumble
        cost = result.roll - threshold
        return cost if cost > 0 else None
