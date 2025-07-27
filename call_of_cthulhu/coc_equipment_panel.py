from panels.base_panel import BasePanel
from panels.text_viewport import TextViewport
from panels.nav_mixin import PanelNavigationMixin


class CthulhuEquipmentPanel(BasePanel, PanelNavigationMixin):
    def __init__(self, game, context):
        super().__init__(context)
        PanelNavigationMixin.__init__(self)
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

        self.last_encoder_position = self.hal.get_encoder_position()
        self.awaiting_release = False
        self.equipped_key = None

        self.render()

    def attach_to(self):
        super().attach_to()
        self.context.show_nav_button(
            "back", callback=lambda b: self.context.return_home()
        )
        self.selected_index = 0
        self.last_encoder_position = self.hal.get_encoder_position()
        self.render()

    def detach_from(self):
        return super().detach_from()

    def confirm_selected_weapon(self):
        try:
            weapon_key = self.weapons[self.selected_index][0]
            self.equipped_key = weapon_key
            self.character.set_current_weapon(self.selected_index)
            self.render()
        except IndexError:
            print("Invalid weapon selection")

    def format_weapon_lines(self) -> list[str]:
        lines = []
        for i, (key, data) in enumerate(self.weapons):
            if isinstance(data, dict):
                normalized = {k.strip(): v for k, v in data.items()}
                weapon_name = normalized.get("Name", "Unnamed Weapon")
                is_selected = i == self.selected_index
                is_equipped = key == self.equipped_key

                line_prefix = "> " if is_selected else "  "
                line_suffix = " [Equipped]" if is_equipped else ""

                lines.append(f"{line_prefix}{weapon_name}{line_suffix}")
                for k, v in normalized.items():
                    if k.lower() != "name":
                        val = v if v not in [None, ""] else "—"
                        lines.append(f"  {k}: {val}")
                lines.append("")  # spacer
            else:
                lines.append(str(data))
        return lines

    def render(self):
        lines = self.format_weapon_lines()
        mid = (len(lines) + 1) // 2
        left, right = self.split_for_columns(lines, mid)
        self.left_view.set_lines(left)
        self.right_view.set_lines(right)

    def update(self):
        current_position = self.hal.get_encoder_position()
        if current_position < self.last_encoder_position:
            if self.move_selection_up([self.weapons, []]):
                self.render()

        elif current_position > self.last_encoder_position:
            if self.move_selection_down([self.weapons, []]):
                self.render()

        if self.hal.is_button_pressed():
            if not self.awaiting_release:
                self.confirm_selected_weapon()
                self.awaiting_release = True
        else:
            self.awaiting_release = False

        self.last_encoder_position = current_position
