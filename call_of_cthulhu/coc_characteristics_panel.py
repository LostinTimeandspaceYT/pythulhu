from panels.base_panel import BasePanel
from adafruit_display_text import label
import terminalio
from panels.text_viewport import TextViewport

class CthulhuCharacteristicsPanel(BasePanel):
    def __init__(self, game, context):
        super().__init__(context)
        self.game = game
        self.character = game.character
        self.page_index = 0
        self.selected_index = 0
        self.options = [
            ["STR", "CON", "SIZ", "DEX", "APP",], ["INT", "POW", "EDU", "Luck"]
        ]
        self.last_encoder_position = self.hal.get_encoder_position()
        self.awaiting_release = False
        self.left_view = TextViewport(
            x=10, y=10,
            width=140, height=200,
            max_lines=5, line_height=22,
            show_background=False
        )
        self.right_view = TextViewport(
            x=160, y=10,
            width=140, height=200,
            max_lines=4, line_height=22,
            show_background=False
        )
        self.group.append(self.left_view.group)
        self.group.append(self.right_view.group)

        self.render()

    def attach_to(self):
        super().attach_to()
        self.context.show_nav_button("prev", callback=lambda b: self.prev_page())
        self.context.show_nav_button("back", callback=lambda b: self.context.return_home())
        self.context.show_nav_button("next", callback=lambda b: self.next_page())
        self.render()
        self.last_encoder_position = self.hal.get_encoder_position()

    def detach_from(self):
        return super().detach_from()

    def render(self):
        page_lines = self.options[0] + self.options[1]
        total_lines = len(page_lines)
        mid = len(self.options[0])
        left_keys = page_lines[:mid]
        right_keys = page_lines[mid:]
        left_lines = []
        right_lines = []

        for i, key in enumerate(left_keys):
            val = self.get_value(key)
            if isinstance(val, int):
                vals = self.game.get_diff_level_thresholds(val)
                hard = vals["Hard"]
                extreme = vals["Extreme"]
            else:
                hard = extreme = "-"
            text = f"{key:<4} {val:>3} ({hard}/{extreme})"
            left_lines.append(text)

        for i, key in enumerate(right_keys):
            val = self.get_value(key)
            if isinstance(val, int):
                vals = self.game.get_diff_level_thresholds(val)
                hard = vals["Hard"]
                extreme = vals["Extreme"]
            else:
                hard = extreme = "-"
            text = f"{key:<4} {val:>3} ({hard}/{extreme})"
            right_lines.append(text)

        selected = self.selected_index
        if selected  < mid:
            left_lines[selected] = "> " + left_lines[selected]
        else:
            right_lines[selected - mid] = "> " + right_lines[selected - mid]


        self.left_view.set_lines(left_lines)
        self.right_view.set_lines(right_lines)


    def get_value(self, key):
        val = None
        if key in self.character.characteristics:
            val = self.character.characteristics[key]
        elif key == "Luck":
            val = self.character.current_luck

        return val if val is not None else 0

    def update(self):
        current_position = self.hal.get_encoder_position()
        if current_position < self.last_encoder_position:
            self.move_selection_up()
        elif current_position > self.last_encoder_position:
            self.move_selection_down()
        self.last_encoder_position = current_position

        if self.hal.is_button_pressed():
            if not self.awaiting_release:
                self.perform_roll()
                self.awaiting_release = True
        else:
            self.awaiting_release = False

    def move_selection_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.render()

    def move_selection_down(self):
        total_lines = len(self.options[0]) + len(self.options[1])
        if self.selected_index < total_lines - 1:
            self.selected_index += 1
            self.render()

    def next_page(self):
        if self.page_index < len(self.options) - 1:
            self.page_index += 1
            self.selected_index = 0
            self.render()

    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.selected_index = 0
            self.render()

    def perform_roll(self):
        keys = self.options[0] + self.options[1]
        if self.selected_index >= len(keys):
            return

        key = keys[self.selected_index]
        val = self.get_value(key)
        if isinstance(val, int):
            from call_of_cthulhu.coc_skill_roll_panel import SkillRollPanel

            def close_panel(_result=None):
                self.context.transition_to("main")

            roll_panel = self.context.get_cached_panel("roll")
            if roll_panel:
                roll_panel.reset(skill_name=key, skill_val=val)
            else:
                roll_panel = SkillRollPanel(
                    game=self.game,
                    context=self.context,
                    skill_name=key,
                    skill_val=val,
                    cancel_callback=close_panel
                )
                self.context.cache_panel("roll", roll_panel)

            self.context.transition_to("roll")
