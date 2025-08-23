from adafruit_display_text.label import Label
import terminalio
from panels.base_panel import BasePanel
from panels.nav_mixin import PanelNavigationMixin
from call_of_cthulhu.coc_roll_params import CthulhuRollParams
from call_of_cthulhu.coc_combat_result_panel import CthulhuCombatResultPanel


class CthulhuCombatRollPanel(BasePanel, PanelNavigationMixin):
    PARAM_KEYS = ["Bonus", "Penalty", "Difficulty", "Confirm"]
    __slots__ = (
        "game",
        "character",
        "labels",
        "selected_index",
        "last_encoder_position",
        "bonus",
        "penalty",
        "difficulty",
        "confirm_selected",
        "_diffs",
        "_warning_text",
    )

    def __init__(self, game, context):
        super().__init__(context)
        PanelNavigationMixin.__init__(self)
        self.game = game
        self.character = game.character
        self.labels = []
        self._diffs = list(self.game.DIFFICULTY_LEVELS.keys())

        self._reset_state()
        self._init_labels()

    def attach_to(self):
        super().attach_to()
        self._reset_state()
        self.context.hide_nav_button("prev")
        self.context.show_nav_button(
            "back", callback=lambda b: self.context.return_home()
        )
        self.context.hide_nav_button("next")
        self.render_labels()

    def detach_from(self):
        for label in self.labels:
            label.text = ""
        return super().detach_from()

    def _reset_state(self):
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.bonus = 0
        self.penalty = 0
        self.difficulty = "Normal"
        self.confirm_selected = False
        self._warning_text = ""

    def _init_labels(self):
        """Initialize Label objects once and reuse them."""
        y = 10
        # One for Weapon name & dmg, the rest for the params
        for _ in range(2 + len(self.PARAM_KEYS)):
            lbl = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(lbl)
            self.group.append(lbl)
            y += 20
        self.render_labels()

    def _current_weapon(self):
        return getattr(self.character, "current_weapon", None)

    def _normalize_weapon(self, w):
        if isinstance(w, dict):
            return {(k.strip() if isinstance(k, str) else k): v for k, v in w.items()}
        return {}

    def _weapon_name(self):
        w = self._normalize_weapon(self._current_weapon())
        return w.get("Name", "—")

    def _weapon_damage_str(self):
        w = self._normalize_weapon(self._current_weapon())
        dmg = w.get("Damage")
        return dmg if (isinstance(dmg, str) and len(dmg.strip()) > 0) else "—"

    def _get_skill_val_for_weapon(self, wname: str) -> int:
        """
        Find a skill value matching the weapon name.
        Supports dict skills with Current/Value.
        """
        skills = getattr(self.character, "skills", {})
        v = skills.get(wname)
        if isinstance(v, int):
            return v
        if isinstance(v, dict):
            for k in ("Current", "Value", "current", "value"):
                if k in v and isinstance(v[k], int):
                    return v[k]
        return 0

    def _warn(self, msg: str):
        self._warning_text = msg
        self.render_labels()

    def render_labels(self):
        y = 10
        if self._warning_text:
            self.labels[0].text = self._warning_text
            self.labels[0].y = y
            y += 20
            # Keep DMG line blank while warning is visible
            self.labels[1].text = ""
            self.labels[1].y = y
            y += 20
        else:
            # Two-line header to avoid overflow
            self.labels[0].text = "Weapon: %s" % self._weapon_name()
            self.labels[0].y = y
            y += 20
            self.labels[1].text = "DMG: %s" % self._weapon_damage_str()
            self.labels[1].y = y
            y += 20

        param_dict = {
            "Bonus": self.bonus,
            "Penalty": self.penalty,
            "Difficulty": self.difficulty,
            "Confirm": self.confirm_selected,
        }

        self.render_option_labels(
            labels=self.labels[1:],
            start_y=y,
            selected_index=self.selected_index,
            param_keys=self.PARAM_KEYS,
            param_values=param_dict,
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
            levels = self._diffs
            idx = levels.index(self.difficulty)
            idx = (idx + (1 if increment else -1)) % len(levels)
            self.difficulty = levels[idx]

        elif key == "Bonus":
            delta = 1 if increment else -1
            self.bonus = max(0, min(3, self.bonus + delta))

        elif key == "Penalty":
            delta = 1 if increment else -1
            self.penalty = max(0, min(3, self.penalty + delta))

        self.render_labels()

    def _perform_roll(self):
        wname = self._weapon_name()
        if wname == "—":
            self._warn("Equip a weapon first!")
            return

        base_val = self._get_skill_val_for_weapon(wname)

        roll_params = CthulhuRollParams(
            name=wname,
            base_val=base_val,
            bonus=self.bonus,
            penalty=self.penalty,
            difficulty=self.difficulty,
            can_spend_luck=True,
            can_push=True,
            can_improve=True,
        )

        roll = self.game.roll_skill(self.bonus, self.penalty)
        result = self.game.evaluate_roll(roll, params=roll_params)

        damage_total = None
        if self.game.is_success(result, roll_params):
            dmg_params = CthulhuRollParams(name=wname, base_val=0, extra_tag="damage")
            damage_total = self.game.roll_damage(dmg_params)

        panel = CthulhuCombatResultPanel(
            self.game,
            self.context,
            result=result,
            params=roll_params,
            weapon=self._current_weapon(),
            damage=damage_total,
        )
        prev = self.context.active_panel
        if prev:
            prev.detach_from()
            self.context.remove_panel("combat_roll")
        self.context.cache_panel("combat_result", panel)
        self.context.transition_to("combat_result", 1)

        self.confirm_selected = False
        self.render_labels()

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
                self.modify_selected_param(
                    increment=(current_position > self.last_encoder_position)
                )
            self.last_encoder_position = current_position

            # Clear an warning on next user interaction
            if self._warning_text:
                self._warning_text = ""
                self.render_labels()

        # When we're finally ready to roll
        if self.mode == "select" and self.confirm_selected:
            self._perform_roll()
            self.confirm_selected = False
            self.render_labels()
