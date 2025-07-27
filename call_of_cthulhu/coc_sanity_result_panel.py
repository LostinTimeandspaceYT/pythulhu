from adafruit_display_text.label import Label
import terminalio
from panels.base_panel import BasePanel
from call_of_cthulhu.coc_dice import CthulhuDice


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
        "die_size",
        "san_loss_amount",
        "madness_triggered",
        "mode",
    )

    PARAM_KEYS = ["Change Die", "Roll SAN Loss", "Acknowledge"]
    DIE_OPTIONS = [1, 2, 3, 4, 6, 8, 10, 12, 20, 100]

    def __init__(self, game, context, *, result, params, on_complete):
        super().__init__(context)
        self.game = game
        self.result = result
        self.roll_params = params
        self.on_complete = on_complete

        self.die_size = 6
        self.san_loss_amount = None
        self.madness_triggered = False

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
        total = 10  # summary, message, die display, result, madness, options (3)
        for _ in range(total):
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        color = self.result.stylize(
            self.game.DIFFICULTY_LEVELS[self.roll_params.difficulty]
        )
        self.hal.fill_all_pixels(color)

        self.labels[0].text = self.result.summary()
        self.labels[0].color = color
        self.labels[0].y = 10

        self.labels[1].text = "SUCCESS" if self.result.passed() else "FAILED"
        self.labels[1].y = 40

        if self.result.success_level < 1:
            self.labels[2].y = 64
            self.labels[2].text = (
                f"You lose {self.san_loss_amount} SAN"
                if self.san_loss_amount is not None
                else ""
            )
            self.labels[3].y = 88
            self.labels[3].text = "BOUT OF MADNESS!" if self.madness_triggered else ""
        else:
            self.labels[2].text = ""
            self.labels[3].text = ""
            self.labels[4].text = ""

        options = {
            "Change Die": f"1d{self.die_size}",
            "Roll SAN Loss": False,
            "Acknowledge": self.confirm_selected,
        }

        self.render_option_labels(
            labels=self.labels[5:],
            start_y=130,
            selected_index=self.selected_index,
            param_keys=self.PARAM_KEYS,
            param_values=options,
        )

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
        if self.selected_index < len(self.PARAM_KEYS) - 1:
            self.selected_index += 1
            self.render_labels()

    def modify_selected_param(self, increment=True):
        key = self.PARAM_KEYS[self.selected_index]

        if key == "Acknowledge":
            self.confirm_selected = not self.confirm_selected

        if self.result.passed():
            # prevent users from tampering with results if passed
            return

        elif key == "Change Die":
            idx = self.DIE_OPTIONS.index(self.die_size)
            idx = (
                (idx + 1) % len(self.DIE_OPTIONS)
                if increment
                else (idx - 1) % len(self.DIE_OPTIONS)
            )
            self.die_size = self.DIE_OPTIONS[idx]

        elif key == "Roll SAN Loss":
            self.roll_san_loss()

        self.render_labels()

    def roll_san_loss(self):
        self.san_loss_amount = CthulhuDice.roll(1, self.die_size)
        self.game.character.set_sanity(
            self.game.character.current_sanity - self.san_loss_amount
        )
        if self.san_loss_amount >= 5:
            self.madness_triggered = True

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
            self.confirm_selected = False
            self.on_complete()
