# skills_panel.py

from text_viewport import TextViewport
from base_panel import BasePanel

class SkillsPanel(BasePanel):
    def __init__(self, context, x=10, y=10, width=300, height=160, lines_per_column=7):
        super().__init__(context)
        self.character = context.character
        self.lines_per_column = lines_per_column
        self.total_lines_per_page = lines_per_column * 2
        self.selected_index = 0
        self.page = 0

        self.last_encoder_position = self.hal.get_encoder_position()
        self.awaiting_release = False

        # Left viewport
        self.left_view = TextViewport(
            x=x,
            y=y,
            width=width // 2 - 5,
            height=height,
            max_lines=lines_per_column,
            line_height=14,
            show_background=True,
            background_color=0x111133
        )

        # Right viewport
        self.right_view = TextViewport(
            x=x + width // 2 + 5,
            y=y,
            width=width // 2 - 5,
            height=height,
            max_lines=lines_per_column,
            line_height=14,
            show_background=True,
            background_color=0x111133
        )

        self.group.append(self.left_view.group)
        self.group.append(self.right_view.group)

        self.all_lines = self.get_all_skill_lines()
        self.total_pages = (len(self.all_lines) + self.total_lines_per_page - 1) // self.total_lines_per_page

    def get_all_skill_lines(self) -> list[str]:
        sheet = self.character.sheet
        skills = sheet.get("Skills", {})
        lines = []

        for skill, value in skills.items():
            if isinstance(value, dict):
                lines.append(f"{skill}:")
                for subskill, subval in value.items():
                    val = subval.get("Current", "-") if isinstance(subval, dict) else subval
                    lines.append(f"  {subskill}: {val}")
            else:
                val = value.get("Current", "-") if isinstance(value, dict) else value
                lines.append(f"{skill}: {val}")

        return lines

    def update(self):
        current_position = self.hal.get_encoder_position()
        if current_position < self.last_encoder_position:
            self.move_selection_up()
        elif current_position > self.last_encoder_position:
            self.move_selection_down()
        self.last_encoder_position = current_position

        if self.hal.is_button_pressed():
            if not self.awaiting_release:
                self.roll_selected_skill()
                self.awaiting_release = True
        else:
            self.awaiting_release = False

    def show(self):
        self.update_page()
        super().show()

    def hide(self):
        super().hide()

    def next_page(self):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.update_page()

    def update_page(self):
        start = self.page * self.total_lines_per_page
        end = min(start + self.total_lines_per_page, len(self.all_lines))
        page_lines = self.all_lines[start:end]

        mid = self.lines_per_column
        left = page_lines[:mid]
        right = page_lines[mid:]

        selected_rel = self.selected_index - start
        if 0 <= selected_rel < self.total_lines_per_page:
            if selected_rel < mid:
                left[selected_rel] = "> " + left[selected_rel]
            else:
                right[selected_rel - mid] = "> " + right[selected_rel - mid]

        self.left_view.set_lines(left)
        self.right_view.set_lines(right)

    def move_selection_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.page * self.total_lines_per_page:
                self.page -= 1
            self.update_page()

    def move_selection_down(self):
        if self.selected_index < len(self.all_lines) - 1:
            self.selected_index += 1
            if self.selected_index >= (self.page + 1) * self.total_lines_per_page:
                self.page += 1
            self.update_page()

    def roll_selected_skill(self):
        line = self.all_lines[self.selected_index].strip()
        line = line.lstrip(">").strip()

        if ":" in line:
            skill_name = line.split(":", 1)[0].strip()
            self.open_skill_roll_panel(skill_name)

    def open_skill_roll_panel(self, skill_name: str):
        from skill_roll_panel import SkillRollPanel

        def close_panel(_result=None):
            self.roll_panel.detach_from()
            self.show()

        self.roll_panel = SkillRollPanel(
            context=self.context,
            skill_name=skill_name,
            confirm_callback=None,
            cancel_callback=close_panel
        )

        self.hal.clear_display()
        self.hal.reset_display()
        self.manager.buttons.clear()
        self.context.active_panel.detach_from()  # detach previous panel
        self.context.active_panel = self.roll_panel

        self.roll_panel.attach_to()
