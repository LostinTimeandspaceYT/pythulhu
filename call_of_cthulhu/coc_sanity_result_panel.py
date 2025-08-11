from adafruit_display_text.label import Label
import terminalio
from panels.base_panel import BasePanel
from call_of_cthulhu.coc_dice import CthulhuDice
from call_of_cthulhu.coc_roll_params import CthulhuRollParams


class CthulhuSanityResultPanel(BasePanel):
    __slots__ = (
        "game",
        "result",
        "roll_params",
        "on_complete",
        "selected_index",
        "last_encoder_position",
        "confirm_selected",
        "labels",
        "san_loss_amount",
        "san_loss_rolled",
        "bout_triggered",
        "int_val",
        "int_result",
        "mode",
    )

    PARAM_KEYS = ["Roll SAN Loss", "Confirm"]

    def __init__(self, game, context, *, result, params, on_complete):
        super().__init__(context)
        self.game = game
        self.result = result
        self.roll_params = params
        self.on_complete = on_complete

        self.san_loss_amount = None
        self.san_loss_rolled = False
        self.bout_triggered = False

        # For potential bouts
        self.int_val = None
        self.int_result = None

        self.confirm_selected = False
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.mode = "select"
        self.labels = []

        self._init_labels()
        self.attach_to()

    def _init_labels(self):
        self.labels = []
        y = 10
        # 0 summary, 1 success/fail, 2 SAN loss, 3 INT result line, 4 Bout line, 5+ options
        total = 11
        for _ in range(total):
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def _san_tuple(self):
        # Pull (count, sides) from params.extra_dice (fallback to 1d6)
        if self.roll_params and getattr(self.roll_params, "extra_dice", None):
            n, s = self.roll_params.extra_dice[0]
            return int(n), int(s)
        return 1, 6

    def render_labels(self):
        color = self.result.stylize(
            self.game.DIFFICULTY_LEVELS[self.roll_params.difficulty]
        )
        self.hal.fill_all_pixels(color)

        self.labels[0].text = self.result.summary()
        self.labels[0].color = color
        self.labels[0].y = 10

        passed = self.result.passed()
        self.labels[1].text = "SUCCESS" if passed else "FAILED"
        self.labels[1].y = 40

        # Lines that only show when the SAN check failed
        if not passed:
            # SAN loss line
            self.labels[2].y = 64
            self.labels[2].text = (
                f"You lose {self.san_loss_amount} SAN"
                if self.san_loss_amount is not None
                else ""
            )
            # INT result line (only if we rolled it)
            self.labels[3].y = 88
            self.labels[3].text = (
                f"INT roll: {self.int_result.outcome}"
                if self.int_result is not None
                else ""
            )
            # Bout line (only if the INT roll was a success)
            self.labels[4].y = 112
            self.labels[4].text = "BOUT OF MADNESS!" if self.bout_triggered else ""
        else:
            self.labels[2].text = ""
            self.labels[3].text = ""
            self.labels[4].text = ""

        n, s = self._san_tuple()
        option_keys = self.PARAM_KEYS if not passed else ["Confirm"]

        options = {}
        if not passed:
            rolled_tag = " (done)" if self.san_loss_rolled else f" ({n}d{s})"
            options["Roll SAN Loss"] = rolled_tag
        options["Confirm"] = self.confirm_selected

        self.render_option_labels(
            labels=self.labels[5:],
            start_y=150,
            selected_index=self.selected_index if not passed else 0,
            param_keys=option_keys,
            param_values=options,
        )

    def attach_to(self):
        super().attach_to()
        self.context.hide_nav_button("prev")
        self.context.hide_nav_button("back")
        self.context.hide_nav_button("next")

    def detach_from(self):
        self.hal.fill_all_pixels(0)
        for label in self.labels:
            label.text = ""
        return super().detach_from()

    def move_selection_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.render_labels()

    def move_selection_down(self):
        max_idx = 1 if not self.result.passed() else 0  # when passed, only "Confirm"
        if self.selected_index < max_idx:
            self.selected_index += 1
            self.render_labels()

    def modify_selected_param(self, increment=True):
        key_list = self.PARAM_KEYS if not self.result.passed() else ["Confirm"]
        key = key_list[self.selected_index]

        if key == "Confirm":
            self.confirm_selected = not self.confirm_selected

        elif key == "Roll SAN Loss":
            if not self.san_loss_rolled:
                self.roll_san_loss()

        self.render_labels()

    def roll_san_loss(self):
        n, s = self._san_tuple()
        if self.result.outcome == "fumble":
            self.san_loss_amount = n * s

        else:
            # Roll SAN loss from tuple (count, sides)
            total = 0
            for _ in range(n):
                total += CthulhuDice.roll(1, s)
            self.san_loss_amount = total

        self.san_loss_rolled = True
        # Apply loss immediately
        self.game.character.set_sanity(
            self.game.character.current_sanity - self.san_loss_amount
        )

        if self.san_loss_amount >= 5:
            self.int_val = int(self.game.character.characteristics["INT"])
            int_roll = self.game.roll_skill(bonus_die=0, penalty_die=0)
            int_params = CthulhuRollParams(
                name="INT",
                base_val=self.int_val,
                bonus=0,
                penalty=0,
                difficulty="Normal",
                can_improve=False,
                can_push=False,
                can_spend_luck=False,
            )
            self.int_result = self.game.evaluate_roll(int_roll, params=int_params)
            self.bout_triggered = self.int_result.passed()

    def _can_confirm(self):
        if self.result.passed():
            return True
        return self.san_loss_rolled

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

        if self.mode == "select" and self.confirm_selected and self._can_confirm():
            self.confirm_selected = False
            self.on_complete()
        elif self.confirm_selected and not self._can_confirm():
            self.confirm_selected = False
            self.render_labels()
