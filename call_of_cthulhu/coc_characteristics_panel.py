from panels.base_panel import BasePanel
from adafruit_display_text import label
from panels.nav_mixin import PanelNavigationMixin
from panels.text_viewport import TextViewport

class CthulhuCharacteristicsPanel(BasePanel, PanelNavigationMixin):
    def __init__(self, game, context):
        super().__init__(context)
        PanelNavigationMixin.__init__(self)
        self.game = game
        self.character = game.character
        self.page_index = 0
        self.selected_index = 0
        self.options = [
            ["STR", "CON", "SIZ", "DEX", "APP",], ["INT", "POW", "EDU", "Luck", "Sanity"]
        ]
        self.last_encoder_position = self.hal.get_encoder_position()
        self.awaiting_release = False
        self.left_view = TextViewport(
            x=10, y=10,
            width=140, height=200,
            max_lines=len(self.options[0]), line_height=22,
            show_background=False
        )
        self.right_view = TextViewport(
            x=160, y=10,
            width=140, height=200,
            max_lines=len(self.options[1]), line_height=22,
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

    def format_line(self, key):
        val = self.get_value(key)
        hard = "-"
        extreme = "-"
        if isinstance(val, int):
            vals = self.game.get_diff_level_thresholds(val)
            hard = vals["Hard"]
            extreme = vals["Extreme"]
        return f"{key:<4} {val:>3} ({hard}/{extreme})"

    def render(self):
        page_lines = self.options[0] + self.options[1]
        mid = len(self.options[0])
        left_keys = page_lines[:mid]
        right_keys = page_lines[mid:]
        left_lines = [self.format_line(key) for key in left_keys]
        right_lines = [self.format_line(key) for key in right_keys]
        self.apply_marker(left_lines=left_lines, right_lines=right_lines, selected_index=self.selected_index)
        self.left_view.set_lines(left_lines)
        self.right_view.set_lines(right_lines)

    def get_value(self, key):
        val = None
        if key == "Sanity":
            val = self.character.current_sanity
        elif key == "Luck":
            val = self.character.current_luck
        else:
            val = self.character.characteristics[key]

        return val if val is not None else 0

    def update(self):
        current_position = self.hal.get_encoder_position()
        if current_position < self.last_encoder_position:
            if self.move_selection_up(self.options):
                self.render()

        elif current_position > self.last_encoder_position:
            if self.move_selection_down(self.options):
                self.render()
        self.last_encoder_position = current_position

        if self.hal.is_button_pressed():
            if not self.awaiting_release:
                self.perform_roll()
                self.awaiting_release = True
        else:
            self.awaiting_release = False

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
