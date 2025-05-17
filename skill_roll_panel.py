from adafruit_display_text.label import Label
import terminalio
from base_panel import BasePanel
from coc_game import CthulhuGame
from coc_character import CthulhuCharacter
from coc_roll_params import CthulhuRollParams
from coc_roll_result_panel import CthulhuRollResultPanel 


class SkillRollPanel(BasePanel):
    # Explicit display order
    PARAM_KEYS = ["Bonus", "Penalty", "Difficulty", "Confirm"]

    def __init__(self, context, skill_name, cancel_callback):
        super().__init__(context)
        self.character: CthulhuCharacter = context.character
        self.cancel_callback = cancel_callback
        skill_val = self.character.get_value_at(skill_name)
        if isinstance(skill_val, dict):
            skill_val = skill_val.get("Current", 0)

        self.skill_name = skill_name
        self.skill_val = skill_val
        self.result = None
        self.bonus = 0
        self.penalty = 0
        self.difficulty = "Normal"
        self.confirm_selected = False
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.labels = []
        self._init_labels()

    def _init_labels(self):
        """Initialize Label objects once and reuse them."""
        y = 10
        for _ in range(len(self.PARAM_KEYS) + 1):
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        y = 10
        self.labels[0].text = f"Skill: {self.skill_name} ({self.skill_val})"
        self.labels[0].y = y
        y += 20
        param_dict = {
            "Bonus": self.bonus,
            "Penalty": self.penalty,
            "Difficulty": self.difficulty,
            "Confirm": self.confirm_selected
        }
        self.render_option_labels(
            labels=self.labels,
            start_y=y,
            selected_index=self.selected_index,
            param_keys=self.PARAM_KEYS,
            param_values=param_dict
        )

    def on_mode_change(self):
        self.render_labels()

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

        if key == "Confirm":
            self.confirm_selected = not self.confirm_selected

        elif key == "Difficulty":
            levels = list(CthulhuGame.DIFFICULTY_LEVELS.keys())
            idx = levels.index(self.difficulty)
            idx = (idx + 1) % len(levels) if increment else (idx - 1) % len(levels)
            self.difficulty = levels[idx]

        elif key == "Bonus":
            delta = 1 if increment else -1
            self.bonus = max(0, min(3, self.bonus + delta))

        elif key == "Penalty":
            delta = 1 if increment else -1
            self.penalty = max(0, min(3, self.penalty + delta))

        self.render_labels()


    def reset(self, skill_name: str):
        self.skill_name = skill_name
        self.skill_val = self.character.get_value_at(skill_name)
        if isinstance(self.skill_val, dict):
            self.skill_val = self.skill_val.get("Current", 0)

        self.bonus = 0
        self.penalty = 0
        self.difficulty = "Normal"
        self.confirm_selected = False
        self.selected_index = 0
        self.mode = "select"
        self.last_encoder_position = self.hal.get_encoder_position()
        self.result = None
        self.render_labels()

    def attach_to(self):
        super().attach_to()
        self.context.hide_nav_button("prev")
        self.context.show_nav_button("back", callback=self.cancel_callback)
        self.context.hide_nav_button("next")

    def roll(self):
        if self.result is None:
            roll = self.character.roll_skill(
                bonus_die=self.bonus,
                penalty_die=self.penalty
            )
            roll_params = CthulhuRollParams(
                name=self.skill_name,
                base_val=self.skill_val,
                bonus=self.bonus,
                penalty=self.penalty,
                difficulty=self.difficulty
            )
            self.result = CthulhuGame.evaluate_roll(roll, params=roll_params)

            # TODO: Here, let's just create the result panel regardless.
            # and let the result panel handle marking skills for improvement.
            # if self.result.success_level >= roll_params.diff_level:
            #     # TODO: Some skills cannot be improved, added flag in roll_params
            #     self.character.mark_skill_for_improvement(self.skill_name)
            panel = CthulhuRollResultPanel(
                context=self.context,
                result=self.result,
                params=roll_params,
                on_complete=self.cancel_callback
            )
            prev = self.context.active_panel
            if prev:
                prev.detach_from()
                del self.context.panels["roll"]
            self.context.cache_panel("roll_result", panel)
            self.context.transition_to("roll_result")
            return


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
        if self.mode == "select" and self.confirm_selected:
            self.roll()
            self.confirm_selected = False
            self.render_labels()
