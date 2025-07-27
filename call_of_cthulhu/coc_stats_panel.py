from panels.base_panel import BasePanel
from adafruit_display_text import label
from panels.text_viewport import TextViewport


class CthulhuStatsPanel(BasePanel):
    """Read-only Panel to display an investigators stats"""

    def __init__(self, game, context):
        super().__init__(context)
        self.game = game
        self.character = game.character
        self.options = [
            ["Hit Points", "Magic Points", "Major Wound", "Unconscious", "Dying"],
            ["Sanity"],
        ]
        self.left_view = TextViewport(
            x=10,
            y=10,
            width=140,
            height=200,
            max_lines=10,
            line_height=20,
            show_background=False,
        )
        self.right_view = TextViewport(
            x=160,
            y=10,
            width=140,
            height=200,
            max_lines=8,
            line_height=20,
            show_background=False,
        )
        self.group.append(self.left_view.group)
        self.group.append(self.right_view.group)

        self.render()

    def attach_to(self):
        super().attach_to()
        self.context.show_nav_button(
            "back", callback=lambda b: self.context.return_home()
        )
        self.render()
        self.last_encoder_position = self.hal.get_encoder_position()

    def detach_from(self):
        return super().detach_from()

    def format_stat_line(self, name, val, indent=0):
        padding = " " * indent
        return f"{padding}{name}: {val}"

    def format_sanity_lines(self) -> list[str]:
        lines = []
        sanity_data = self.character.characteristics.get("Sanity", "N/A")
        if isinstance(sanity_data, dict):
            lines.append("Sanity:")
            for substat, subval in sanity_data.items():
                if isinstance(subval, bool):
                    subval_str = "Yes" if subval else "No"
                else:
                    subval_str = subval
                lines.append(self.format_stat_line(substat, subval_str, indent=1))
        else:
            if isinstance(sanity_data, bool):
                sanity_str = "Yes" if sanity_data else "No"
            else:
                sanity_str = sanity_data
            lines.append(self.format_stat_line("Sanity", sanity_str))
        return lines

    def format_physical_lines(self) -> list[str]:
        lines = []
        for stat in self.options[0]:
            value = self.character.characteristics.get(stat, "N/A")
            if isinstance(value, dict):
                lines.append(f"{stat}:")
                for substat, subval in value.items():
                    lines.append(self.format_stat_line(substat, subval, indent=1))
            else:
                if isinstance(value, bool):
                    value_str = "Yes" if value else "No"
                else:
                    value_str = value
                lines.append(self.format_stat_line(stat, value_str))
        return lines

    def render(self):
        left_lines = self.format_physical_lines()
        right_lines = self.format_sanity_lines()
        self.left_view.set_lines(left_lines)
        self.right_view.set_lines(right_lines)
