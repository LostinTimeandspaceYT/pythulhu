import displayio
from adafruit_display_text.label import Label
import terminalio
from base_panel import BasePanel


class SkillRollPanel(BasePanel):
    def __init__(self, context, skill_name, confirm_callback, cancel_callback):
        super().__init__(context)
        self.character = context.character
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

        skill_val = self.character.get_value_at(skill_name)
        if isinstance(skill_val, dict):
            skill_val = skill_val.get("Current", 0)

        self.skill_name = skill_name
        self.skill_val = skill_val

        self.roll_params = {
            "Difficulty": "Normal",
            "Bonus": 0,
            "Penalty": 0
        }

        self.param_keys = list(self.roll_params.keys())
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()

        self.labels = []
        self._init_labels()

        self.result_label = Label(terminalio.FONT, text="", color=0xFFFF00, x=10, y=130)
        self.group.append(self.result_label)

    def _init_labels(self):
        """Initialize Label objects once and reuse them."""
        y = 10
        for i in range(len(self.param_keys)):
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        """Update text for each label instead of reallocating them."""
        y = 10
        for i, key in enumerate(self.param_keys):
            prefix = "> " if i == self.selected_index else "  "
            self.labels[i].text = f"{prefix}{key}: {self.roll_params[key]}"
            self.labels[i].y = y
            y += 20

    def on_mode_change(self):
        self.render_labels()

    def move_selection_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.render_labels()

    def move_selection_down(self):
        if self.selected_index < len(self.param_keys) - 1:
            self.selected_index += 1
            self.render_labels()

    def modify_selected_param(self, increment=True):
        key = self.param_keys[self.selected_index]
        if key == "Difficulty":
            levels = ["Normal", "Hard", "Extreme"]
            current = self.roll_params[key]
            idx = levels.index(current)
            idx = (idx + 1) % len(levels) if increment else (idx - 1) % len(levels)
            self.roll_params[key] = levels[idx]

        elif key in ("Bonus", "Penalty"):
            delta = 1 if increment else -1
            self.roll_params[key] = max(0, min(3, self.roll_params[key] + delta))

        self.render_labels()

    def roll(self):
        result = self.character.roll_skill_by_name(
            self.skill_name,
            bonus_die=self.roll_params["Bonus"],
            penalty_die=self.roll_params["Penalty"]
        )
        self.result_label.text = result
        if self.confirm_callback:
            self.confirm_callback(result)

    def update(self):
        super().update()  # handles button press and mode toggle

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
