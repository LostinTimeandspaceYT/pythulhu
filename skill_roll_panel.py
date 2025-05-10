from adafruit_display_text.label import Label
import terminalio
from base_panel import BasePanel


class SkillRollPanel(BasePanel):
    DIFFICULTY_LEVELS = {
        "Normal": 1,
        "Hard": 2,
        "Extreme": 3
    }
    SUCCESS_LEVELS = {
        "Fumble": 0,
        "Fail": 0,
        "Normal": 1,
        "Hard": 2,
        "Extreme": 3,
        "Critical": 4
    }
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
            "Penalty": 0,
            "Confirm": False
        }

        # Explicit display order
        self.param_keys = [
            'Bonus',
            'Penalty',
            'Difficulty',
            'Confirm'
        ]
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()

        self.labels = []
        self._init_labels()

        self.result_label = Label(terminalio.FONT, text="", color=0xFFFF00, scale=2, x=10, y=130)
        self.group.append(self.result_label)

    def _init_labels(self):
        """Initialize Label objects once and reuse them."""
        y = 10
        for _ in range(len(self.param_keys) + 1):
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        y = 10
        expected_text = f"Skill: {self.skill_name} ({self.skill_val})"
        if self.labels[0].text != expected_text:
            self.labels[0].text = expected_text
        self.labels[0].y = y  # optional: skip if y never changes
        y += 20

        for i, key in enumerate(self.param_keys):
            if self.mode == "select":
                prefix = "> " if i == self.selected_index else "  "
            else:  # edit mode
                prefix = "* " if i == self.selected_index else "  "

            self.labels[i + 1].text = f"{prefix}{key}: {self.roll_params[key]}"
            self.labels[i + 1].y = y
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

        if key == "Confirm":
            self.roll_params["Confirm"] = not self.roll_params["Confirm"]

        if key == "Difficulty":
            levels = list(self.DIFFICULTY_LEVELS.keys())
            idx = levels.index(self.roll_params[key])
            idx = (idx + 1) % len(levels) if increment else (idx - 1) % len(levels)
            self.roll_params[key] = levels[idx]

        elif key in ("Bonus", "Penalty"):
            delta = 1 if increment else -1
            self.roll_params[key] = max(0, min(3, self.roll_params[key] + delta))

        self.render_labels()

    def roll(self):
        result = self.character.roll_skill(
            bonus_die=self.roll_params["Bonus"],
            penalty_die=self.roll_params["Penalty"]
        )
        self.set_result_text(result)

    def set_result_text(self, roll: int):
        thresholds = self.character.get_skill_thresholds(self.skill_val)
        if roll >= 96 and self.skill_val < 50 or roll == 100:
            actual = "Fumble"
        elif roll <= thresholds["Extreme"]:
            actual = "Extreme"
        elif roll <= thresholds["Hard"]:
            actual = "Hard"
        elif roll <= thresholds["Normal"]:
            actual = "Normal"
        elif roll == 1 and self.roll_params["Bonus"] == 0 and self.roll_params["Penalty"] == 0:
            actual = "Critical"
        else:
            actual = "Fail"

        level = self.SUCCESS_LEVELS.get(actual, 0)
        required_level = self.DIFFICULTY_LEVELS.get(self.roll_params["Difficulty"], 1)
        if level >= required_level:
            self.result_label.color = (
                0x00FFFF if level == self.SUCCESS_LEVELS["Critical"] else 0x00FF00
            )
            outcome = f"{actual} Success" 
        else:
            self.result_label.color = 0xFF0000
            outcome = actual if actual == "Fumble" else "Fail"

        self.result_label.text = f"{roll} vs {self.skill_val}: {outcome}"

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

        # When we're finally ready to roll
        if self.mode == "select" and self.roll_params.get("Confirm"):
            self.roll()
            self.roll_params["Confirm"] = False
            self.render_labels()
