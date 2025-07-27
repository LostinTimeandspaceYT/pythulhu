from panels.base_panel import BasePanel
from panels.text_viewport import TextViewport


class CthulhuEquipmentPanel(BasePanel):
    def __init__(self, game, context):
        super().__init__(context)
        self.game = game
        self.character = game.character
        self.weapons = list(self.character.weapons.items())

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
        self.context.show_nav_button("back", callback=lambda b: self.context.return_home())
        self.render()

    def detach_from(self):
        return super().detach_from()

    def format_weapon_lines(self) -> list[str]:
        lines = []
        for _, data in self.weapons:
            if isinstance(data, dict):
                normalized = {k.strip(): v for k, v in data.items()}
                weapon_name = normalized.get("Name", "Unnamed Weapon")
                lines.append(f"{weapon_name}")  # use "Name" field
                for k, v in normalized.items():
                    if k.lower() != "name":
                        val = v if v not in [None, ""] else "—"
                        lines.append(f"  {k}: {val}")
                lines.append("")  # spacing between weapons
            else:
                lines.append(f"{data}")
        return lines

    def render(self):
        lines = self.format_weapon_lines()
        mid = (len(lines) + 1) // 2  # Split roughly in half
        self.left_view.set_lines(lines[:mid])
        self.right_view.set_lines(lines[mid:])
