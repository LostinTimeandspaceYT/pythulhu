from roll_result import RollResult

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
    def get_skill_thresholds(cls, skill_val: int) -> dict:
        return {
            "Normal": int(skill_val),
            "Hard": int(skill_val * 0.5),
            "Extreme": int(skill_val * 0.2)
        }

    @classmethod
    def evaluate_skill_roll(cls, roll: int, skill_val: int, bonus=0, penalty=0) -> RollResult:
        thresholds = cls.get_skill_thresholds(skill_val)

        if roll >= 96 and skill_val < 50 or roll == 100:
            outcome = "Fumble"
        elif roll == 1 and bonus == 0 and penalty == 0:
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
