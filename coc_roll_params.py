# TODO: Decide if a base RollParams class is needed.

class CthulhuRollParams:
    def __init__(self, *, name: str, base_val: int, bonus: int=0, penalty: int=0, difficulty: str="Normal"):
        self.name = name
        self.base_val = base_val
        self.bonus = bonus
        self.penalty = penalty
        self.difficulty = difficulty
        self._can_push = True
        self._can_spend_luck = True
        self.can_improve = True

    def __str__(self):
        return f"Bonus: {self.bonus}, Penalty: {self.penalty}, Difficulty: {self.difficulty}"

    def update(self, key: str, value):
        if hasattr(self, key):
            setattr(self, key, value)

    def as_dict(self):
        return {
            "Bonus": self.bonus,
            "Penalty": self.penalty,
            "Difficulty": self.difficulty
        }

    @property
    def can_push(self):
        return self._can_push

    @can_push.setter
    def can_push(self, value: bool):
        self._can_push = value
        if value:
            self._can_spend_luck = False

    @property
    def can_spend_luck(self):
        return self._can_spend_luck

    @can_spend_luck.setter
    def can_spend_luck(self, value: bool):
        self._can_spend_luck = value
        if value:
            self._can_push = False

    def can_push_and_spend(self):
        self._can_push = True
        self._can_spend_luck = True
