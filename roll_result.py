
class RollResult:
    def __init__(self, roll: int, skill_val: int, outcome: str, level: int):
        self.roll = roll
        self.skill_val = skill_val
        self.outcome = outcome
        self.level = level

    def passed(self, difficulty: int = 1) -> bool:
        return self.level >= difficulty


    def stylize(self, difficulty: str = "Normal") -> int:
        if self.outcome.startswith("Critical"):
            return 0x00FFFF  # cyan
        elif self.passed(difficulty):
            return 0x00FF00  # green
        else:
            return 0xFF0000  # red

    def summary(self) -> str:
        return f"{self.roll} vs {self.skill_val}: {self.outcome}"
