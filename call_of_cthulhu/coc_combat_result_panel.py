from panels.base_panel import BasePanel
from panels.text_viewport import TextViewport


class CthulhuCombatResultPanel(BasePanel):
    __slots__ = ("game", "result", "params", "weapon", "damage", "labels")

    def __init__(self, game, context, *, result, params, weapon, damage):
        super().__init__(context)
        self.game = game
        self.result = result
        self.params = params
        self.weapon = weapon
        self.damage = damage

        self.view = TextViewport(
            x=10,
            y=10,
            width=300,
            height=210,
            max_lines=12,
            line_height=18,
            show_background=False,
        )
        self.group.append(self.view.group)
        self._render()

    def attach_to(self):
        super().attach_to()
        self.context.show_nav_button(
            "back", callback=lambda b: self.context.return_home()
        )

    def _render(self):
        wname = (self.weapon or {}).get("Name", "—")
        lines = []
        lines.append(f"Attack: {wname}")
        lines.append(f"Roll: {self.result.roll} {self.result.outcome}")
        if self.damage is not None:
            lines.append(f"Damage: {self.damage}")
        else:
            lines.append("No damage (attack failed).")
        self.view.set_lines(lines)

    def update(self):
        pass
