from adafruit_display_text.label import Label
import terminalio
from panels.base_panel import BasePanel
from call_of_cthulhu.coc_roll_params import CthulhuRollParams
from call_of_cthulhu.coc_sanity_result_panel import CthulhuSanityResultPanel


class CthulhuSanityRollPanel(BasePanel):
    PARAM_KEYS = ["Bonus", "Penalty", "Difficulty", "Confirm"]
    __slots__ = (
        "cancel_callback",
        "sanity_val",
        "result",
        "difficulty",
        "confirm_selected",
        "selected_index",
        "last_encoder_position",
        "labels",
        "game",
        "bonus",
        "penalty",
    )

    def __init__(self, game, context, cancel_callback=None):
        super().__init__(context)
        self.game = game
        self.cancel_callback = cancel_callback
        self.labels = []
        self._reset_state()
        self._init_labels()

    def _reset_state(self):
        self.result = None
        self.sanity_val = self.game.character.current_sanity
        self.difficulty = "Normal"
        self.bonus = 0
        self.penalty = 0
        self.confirm_selected = False
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()

    def _init_labels(self):
        y = 10
        for _ in range(len(self.PARAM_KEYS) + 1):
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        y = 10
        self.labels[0].text = "Sanity Check (%d)" % self.sanity_val
        self.labels[0].y = y
        y += 20
        param_dict = {
            "Bonus": self.bonus,
            "Penalty": self.penalty,
            "Difficulty": self.difficulty,
            "Confirm": self.confirm_selected,
        }
        self.render_option_labels(
            labels=self.labels,
            start_y=y,
            selected_index=self.selected_index,
            param_keys=self.PARAM_KEYS,
            param_values=param_dict,
        )

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
            levels = list(self.game.DIFFICULTY_LEVELS.keys())
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

    def attach_to(self):
        super().attach_to()
        self.context.hide_nav_button("prev")
        self.context.show_nav_button("back", callback=self.cancel_callback)
        self.context.hide_nav_button("next")

    def detach_from(self):
        for label in self.labels:
            label.text = ""
        return super().detach_from()

    def roll(self):
        if self.result is None:
            roll = self.game.character.roll_skill(
                bonus_die=self.bonus,
                penalty_die=self.penalty,
            )
            roll_params = CthulhuRollParams(
                name="Sanity",
                base_val=self.sanity_val,
                bonus=self.bonus,
                penalty=self.penalty,
                difficulty=self.difficulty,
            )
            self.result = self.game.evaluate_roll(roll, params=roll_params)

            panel = CthulhuSanityResultPanel(
                game=self.game,
                context=self.context,
                result=self.result,
                params=roll_params,
                on_complete=self.context.return_home,
            )
            prev = self.context.active_panel
            if prev:
                prev.detach_from()
                self.context.remove_panel("roll")
            self.context.cache_panel("roll_result", panel)
            self.context.transition_to("roll_result", 1)
            self.result = None

    def update(self):
        super().update()
        current_position = self.hal.get_encoder_position()
        if current_position != self.last_encoder_position:
            if self.mode == "select":
                if current_position > self.last_encoder_position:
                    self.move_selection_down()
                else:
                    self.move_selection_up()
            elif self.mode == "edit":
                self.modify_selected_param(
                    increment=(current_position > self.last_encoder_position)
                )
            self.last_encoder_position = current_position

        if self.mode == "select" and self.confirm_selected:
            self.roll()
            self.confirm_selected = False
            self.render_labels()
