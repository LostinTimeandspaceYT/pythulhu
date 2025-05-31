from panels.base_panel import BasePanel
from adafruit_display_text.label import Label
import terminalio

class SelectorPanel(BasePanel):
    def __init__(self, context, title: str, options: list[str], on_select, on_cancel=None):
        super().__init__(context)
        self.title = title
        self.options = options
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.labels = []
        self._init_labels()

    def _init_labels(self):
        y = 10
        for _ in range(len(self.options) + 1):  # +1 for title
            label = Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=10, y=y)
            self.labels.append(label)
            self.group.append(label)
            y += 20
        self.render_labels()

    def render_labels(self):
        self.labels[0].text = self.title
        self.labels[0].y = 10
        start_y = 30

        self.render_option_labels(
            labels=self.labels,
            start_y=start_y,
            selected_index=self.selected_index,
            param_keys=self.options,
            param_values={opt: "" for opt in self.options}  # no values, just labels
        )

    def attach_to(self):
        super().attach_to()
        self.context.hide_nav_button("prev")
        self.context.hide_nav_button("next")

        if self.on_cancel:
            self.context.show_nav_button("back", callback=self._handle_cancel)
        else:
            self.context.hide_nav_button("back")

    def _handle_cancel(self):
        if callable(self.on_cancel):
            self.on_cancel()

    def move_selection_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.render_labels()

    def move_selection_down(self):
        if self.selected_index < len(self.options) - 1:
            self.selected_index += 1
            self.render_labels()

    def update(self):
        super().update()

        pos = self.hal.get_encoder_position()
        if pos != self.last_encoder_position:
            if pos > self.last_encoder_position:
                self.move_selection_down()
            else:
                self.move_selection_up()
            self.last_encoder_position = pos

        if self.hal.is_button_pressed():
            while self.hal.is_button_pressed():
                pass  # debounce
            self.on_select(self.options[self.selected_index])
