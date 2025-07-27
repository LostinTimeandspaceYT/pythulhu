from game.dice import Dice
from random import randint


class CthulhuDice(Dice):

    @classmethod
    def roll_skill(cls, bonus: int, penalty: int) -> int:
        """Rolls a skill check using bonus/penalty dice."""
        modifier = abs(bonus - penalty)

        if modifier == 0:
            return cls.roll(1, 100)

        ones = randint(0, 9)
        tens_rolls = {randint(0, 9) * 10 for _ in range(modifier + 1)}
        tens = min(tens_rolls) if bonus > penalty else max(tens_rolls)

        total = tens + ones
        if total == 0:
            return (
                sorted(tens_rolls)[1]
                if bonus > penalty and len(tens_rolls) > 1
                else 100
            )
        return total
