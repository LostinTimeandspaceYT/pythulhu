class RollResult:
    def __init__(self, roll: int, outcome: str, level: int):
        """
        A monad-like wrapper for games to display roll results to the screen.
        Args:
            roll (int): What the actual roll was
            outcome (str): description to display on screen
            level (int): 0 = fail, 1 = pass, but can be extended if needed.
        """
        self.roll = roll
        self.outcome = outcome
        self.success_level = level

    def __str__(self):
        return self.summary()

    def passed(self, difficulty: int = 1) -> bool:
        return self.success_level >= difficulty

    def stylize(self, difficulty: int) -> int:
        if self.outcome.startswith("Critical"):
            return 0x00FFFF  # cyan
        elif self.passed(difficulty):
            return 0x00FF00  # green
        else:
            return 0xFF0000  # red

    def summary(self) -> str:
        return f"Rolled {self.roll}: {self.outcome}"
