from adafruit_display_text.label import Label
import terminalio
from coc_game import CthulhuGame
from base_panel import BasePanel

class CthulhuRollResultPanel(BasePanel):
    __slots__ = (
        "game", "result", "roll_params", "on_complete", "threshold", "cost",
        "selected_index", "last_encoder_position", "mode", "roll_mode",
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
        self.passed = self.result.success_level >= CthulhuGame.DIFFICULTY_LEVELS[self.roll_params.difficulty]
        self.PARAM_KEYS = ["Confirm"] if self.passed else ["Spend Luck", "Push", "Confirm"]

        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.mode = "select"
        self.roll_mode = None
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
        summary_text = self.result.summary()

        # Optionally add Luck preview
        if self.roll_mode == 'luck' and self.cost <= self.game.character.current_luck:
            current = self.game.character.current_luck
            new_val = current - self.cost
            summary_text += f"\nLuck: {current} -> {new_val} (Cost: {self.cost})"

        self.labels[0].text = summary_text
        self.labels[0].color = self.result.stylize(
            CthulhuGame.DIFFICULTY_LEVELS[self.roll_params.difficulty]
        )
        self.labels[0].y = 10

        line_count = summary_text.count('\n') + 1
        y = 10 + line_count * 25 # Ajust spacing based on line count

        options = {
            "Spend Luck": self.roll_mode == 'luck',
            "Push": self.roll_mode == 'push',
            "Confirm": self.confirm_selected
        }

        self.render_option_labels(
            labels=self.labels[1:],
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
                self.roll_mode = 'luck' if self.roll_mode != 'luck' else None
        elif key == "Push":
                self.roll_mode = 'push' if self.roll_mode != 'push' else None
        elif key == "Confirm":
            self.confirm_selected = not self.confirm_selected

        self.render_labels()

    def finalize_roll(self):
        if self.roll_mode == 'luck':
            if self.cost <= self.game.character.current_luck:
                self.game.character.set_luck(self.game.character.current_luck - self.cost)
                self.result.success_level += 1
                self.result.outcome += f"\nSpent {self.cost} Luck"
        elif self.roll_mode == 'push':
            new_roll = self.game.character.roll_skill(self.roll_params.bonus, self.roll_params.penalty)
            self.result = CthulhuGame.evaluate_roll(new_roll, self.roll_params)
            self.result.outcome += "\n(Pushed)"

        self.on_complete(self.result)

    def update(self):
        super().update()  # handles button press + mode toggle
        current_position = self.hal.get_encoder_position()
        if current_position != self.last_encoder_position:
            if self.mode == "select":
                if current_position > self.last_encoder_position:
                    self.move_selection_down()
                else:
                    self.move_selection_up()
            elif self.mode == "edit":
                self.modify_selected_param(increment=(current_position > self.last_encoder_position))
            self.last_encoder_position = current_position

        # When we're finally ready to try again
        if self.mode == "select" and self.confirm_selected:
            self.confirm_selected = False
            self.finalize_roll()

