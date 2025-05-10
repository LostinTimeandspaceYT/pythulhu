from roll_result import RollResult

DIFFICULTY_LEVELS = {
    "Normal": 1,
    "Hard": 2,
    "Extreme": 3
}

SUCCESS_LEVELS = {
    "Fumble": 0,
    "Fail": 0,
    "Normal": 1,
    "Hard": 2,
    "Extreme": 3,
    "Critical": 4
}

def evaluate_roll(roll: int, skill_val: int, *, bonus=0, penalty=0) -> RollResult:
    thresholds = {
        "Normal": int(skill_val),
        "Hard": int(0.5 * skill_val),
        "Extreme": int(0.2 * skill_val)
    }

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

    level_key = outcome.split()[0]  # e.g. "Hard", "Fail"
    level = SUCCESS_LEVELS.get(level_key, 0)

    return RollResult(roll, skill_val, outcome, level)
