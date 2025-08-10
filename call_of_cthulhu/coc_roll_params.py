class CthulhuRollParams:
    """
    Generic roll parameters for CoC.
    - `extra_dice`: list of (num_dice, sides) tuples for any follow-up rolls.
      Panels decide WHEN to use these (e.g., on fail for SAN loss, on success for damage).
    """

    def __init__(
        self,
        name,
        base_val,
        bonus=0,
        penalty=0,
        difficulty="Normal",
        can_spend_luck=True,
        can_push=True,
        can_improve=True,
        extra_dice=None,
        extra_tag=None,
    ):
        self.name = name
        self.base_val = base_val
        self.bonus = bonus
        self.penalty = penalty
        self.difficulty = difficulty

        self.can_improve = can_improve
        self.can_spend_luck = can_spend_luck
        self.can_push = can_push
        # list[(int num, int sides)]
        self.extra_dice = extra_dice or []
        self.extra_tag = extra_tag

    # convenience: returns a string like "1d6+1d4"
    def extra_dice_str(self):
        if not self.extra_dice:
            return ""
        parts = []
        for num, sides in self.extra_dice:
            parts.append(f"{num}d{sides}")
        return "+".join(parts)

    def __str__(self):
        return f"Bonus: {self.bonus}, Penalty: {self.penalty}, Difficulty: {self.difficulty}"

    def update(self, key: str, value):
        if hasattr(self, key):
            setattr(self, key, value)

    def as_dict(self):
        return {
            "Bonus": self.bonus,
            "Penalty": self.penalty,
            "Difficulty": self.difficulty,
        }
