from panels.base_panel import BasePanel
from adafruit_display_text import label
from panels.text_viewport import TextViewport


class CthulhuEquipmentPanel(BasePanel):
    def __init__(self, game, context):
        super().__init__(context)
        self.game = game
        self.character = game.character
        self.options = [weapon for weapon in game.character.weapons.keys()]

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

    def detach_from(self):
        return super().detach_from()

    def format_weapon_lines(self):
        lines = []
        for k,v in self.character.weapons.items():
            lines.append(f"{k}: {v}")
        pass

    
    def render(self):
        left_lines = self.format_weapon_lines()
        right_lines = self.format_weapon_lines()
        if left_lines is not None:
            self.left_view.set_lines(left_lines)
        if right_lines is not None:
            self.right_view.set_lines(right_lines)
