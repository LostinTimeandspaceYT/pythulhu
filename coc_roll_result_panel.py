from base_panel import BasePanel
from roll_result import RollResult
from coc_roll_params import CthulhuRollParams

class CthulhuRollResultPanel(BasePanel):
    def __init__(self, context, *, result: RollResult, params: CthulhuRollParams, on_complete):
        super().__init__(context)
        self.character = context.character
        self.name = params.name
        self.result = result
        self.roll_params = params
        self.on_complete = on_complete



    #         luck_cost = CthulhuGame.get_luck_cost(self.result, threshold)
    #         if luck_cost and luck_cost <= self.character.current_luck:
    #             self.pending_luck_cost = luck_cost
    #             self.result.outcome += f"\nCan spend {luck_cost} Luck to pass"
    #             # Wait for user confirmation before proceeding

    # else:
    #     # if they fumbled, passed, or already pushed.
    #     if self.result.success_level < 0 or self.pushed == True:
    #         return

    #     if self.result.success_level >= diff:
    #         return

    #     push = self.character.roll_skill(
    #         bonus_die=bonus,
    #         penalty_die=penalty
    #     )
    #     self.result = CthulhuGame.evaluate_skill_roll(
    #         push,
    #         self.skill_val,
    #         bonus=bonus,
    #         penalty=penalty
    #     )
    #     self.result.outcome += "\n(Pushed)"
    #     self.pushed = True
