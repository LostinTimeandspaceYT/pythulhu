"""
Classes for simulating Dice pools in TTRPGs
"""

__author__ = "Nathan Winslow"
__copyright__ = "MIT"

from random import seed, randint

seed(0)


class Dice:
    """A collection of classmethods class for games to use for their own needs.

    NOTE: It is not intended for users to create instances of Dice, only to
    roll them as needed. for an example of this behavior, check coc_dice.py
    """

    @classmethod
    def roll(cls, num_dice: int, num_sides: int) -> int:
        """Rolls a number of the same kind of die and returns the sum.

        e.g.
        1d20, or 2d4

        Args:
            num_dice (int): number of dice to roll
            num_sides (int): number of sides per dice

        Returns:
            int: result of the die roll
        """
        return sum([randint(1, num_sides) for _ in range(num_dice)])

    @classmethod
    def roll_multiple(cls, dice: list[tuple]) -> int:
        """Rolls multiple different kinds of dice and returns the sum

        e.g.
        1d10 + 1d4

        :param: dice is a list of 2 element tuples (num_dice, num_sides)
        """
        return sum(cls.roll(*die) for die in dice)
