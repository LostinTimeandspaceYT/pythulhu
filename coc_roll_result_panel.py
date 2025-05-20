from adafruit_display_text.label import Label
import terminalio
from coc_game import CthulhuGame
from base_panel import BasePanel

class CthulhuRollResultPanel(BasePanel):
    __slots__ = (
        "game", "result", "roll_params", "on_complete", "threshold", "cost",
        "selected_index", "last_encoder_position", "mode", "spend_luck", "push",
        "confirm_selected", "labels"
    )
    PARAM_KEYS = ["Spend Luck", "Push", "Confirm"]

    def __init__(self, game, context, *, result, params, on_complete):
        super().__init__(context)
        self.game = game
        self.result = result
        self.roll_params = params
        self.on_complete = on_complete

        self.threshold = CthulhuGame.get_val_at_threshold(params.base_val, params.difficulty)
        self.cost = CthulhuGame.get_luck_cost(self.result, self.threshold)

        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.mode = "select"
        self.spend_luck = False
        self.push = False
        self.confirm_selected = False
        self.labels = []

        self._init_labels()
        self.attach_to()

    def _init_labels(self):
        y = 10
        for _ in range(len(self.PARAM_KEYS) + 2):  # +1 for result, +1 for spacing
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        y = 10
        summary_text = self.result.summary()
        if self.labels[0].text != summary_text:
            self.labels[0].text = summary_text
        self.labels[0].color = self.result.stylize(CthulhuGame.DIFFICULTY_LEVELS[self.roll_params.difficulty])
        self.labels[0].y = y
        y += 30

        options = {
            "Spend Luck": self.spend_luck,
            "Push": self.push,
            "Confirm": self.confirm_selected
        }

        self.render_option_labels(
            labels=self.labels,
            start_y=y,
            selected_index=self.selected_index,
            param_keys=self.PARAM_KEYS,
            param_values=options
        )


    def detach_from(self):
        for label in self.labels:
            label.text = ""
        return super().detach_from()

    def move_selection_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.render_labels()

    def move_selection_down(self):
        if self.selected_index < len(self.PARAM_KEYS) - 1:
            self.selected_index += 1
            self.render_labels()

    def modify_selected_param(self, increment=True):
        key = self.PARAM_KEYS[self.selected_index]
        if key == "Spend Luck":
            if self.cost < self.game.character.current_luck:
                self.spend_luck = not self.spend_luck
                self.push = not self.spend_luck
        elif key == "Push":
            self.push = not self.push
            self.spend_luck = not self.push
        elif key == "Confirm":
            self.confirm_selected = not self.confirm_selected

        self.render_labels()

    def finalize_roll(self):
        if self.spend_luck:
            if self.cost <= self.game.character.current_luck:
                self.game.character.set_luck(self.game.character.current_luck - self.cost)
                self.result.success_level += 1
                self.result.outcome += f"\nSpent {self.cost} Luck"
        elif self.push:
            new_roll = self.game.character.roll_skill(self.roll_params.bonus, self.roll_params.penalty)
            self.result = CthulhuGame.evaluate_roll(new_roll, self.roll_params)
            self.result.outcome += "\n(Pushed)"

        self.on_complete(self.result)

    def update(self):
        super().update()

        pos = self.hal.get_encoder_position()
        if pos != self.last_encoder_position:
            if self.mode == "select":
                if pos > self.last_encoder_position:
                    self.move_selection_down()
                else:
                    self.move_selection_up()
            elif self.mode == "edit":
                self.modify_selected_param(increment=(pos > self.last_encoder_position))
            self.last_encoder_position = pos

        if self.hal.is_button_pressed():
            self.modify_selected_param()
            while self.hal.is_button_pressed():
                pass
        
        if self.confirm_selected:
            self.confirm_selected = False
            self.finalize_roll()


    #         luck_cost = CthulhuGame.get_luck_cost(self.result, threshold)
    #         if luck_cost and luck_cost <= self.game.character.current_luck:
    #             self.pending_luck_cost = luck_cost
    #             self.result.outcome += f"\nCan spend {luck_cost} Luck to pass"
    #             # Wait for user confirmation before proceeding

    # else:
    #     # if they fumbled, passed, or already pushed.
    #     if self.result.success_level < 0 or self.pushed == True:
    #         return

    #     if self.result.success_level >= diff:
    #         return

    #     push = self.game.character.roll_skill(
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
