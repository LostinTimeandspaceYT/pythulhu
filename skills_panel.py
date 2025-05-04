import displayio
from text_viewport import TextViewport
from random import randint

class SkillsPanel:
    def __init__(self, character, x=10, y=10, width=300, height=160, lines_per_column=7):
        self.character = character
        self.group = displayio.Group()
        self.lines_per_column = lines_per_column
        self.total_lines_per_page = lines_per_column * 2
        self.selected_index = 0

        # Left viewport
        self.left_view = TextViewport(
            x=x,
            y=y,
            width=width // 2 - 5,
            height=height,
            max_lines=lines_per_column,
            line_height=14,
            show_background=True,
            background_color=0x111133  # Dark blue
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

        self.page = 0
        self.all_lines = self.get_all_skill_lines()
        self.total_pages = (len(self.all_lines) + self.total_lines_per_page - 1) // self.total_lines_per_page

    def get_all_skill_lines(self) -> list[str]:
        sheet = self.character.sheet
        skills = sheet.get("Skills", {})
        lines = []

        for skill, value in skills.items():
            # If it's a nested dict (e.g., Language or Firearms)
            if isinstance(value, dict):
                lines.append(f"{skill}:")  # parent header
                for subskill, subval in value.items():
                    # Handle either raw value or nested dict with "Current"
                    if isinstance(subval, dict):
                        val = subval.get("Current", "-")
                    else:
                        val = subval
                    lines.append(f"  {subskill}: {val}")
            else:
                # Top-level skill
                if isinstance(value, dict):
                    val = value.get("Current", "-")
                else:
                    val = value
                lines.append(f"{skill}: {val}")

        return lines

    def update(self):
        start = self.page * self.total_lines_per_page
        end = min(start + self.total_lines_per_page, len(self.all_lines))
        page_lines = self.all_lines[start:end]

        mid = self.lines_per_column
        left = page_lines[:mid]
        right = page_lines[mid:]

        # Add a visual indicator to selected line
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
            self.update()

    def move_selection_down(self):
        if self.selected_index < len(self.all_lines) - 1:
            self.selected_index += 1
            if self.selected_index >= (self.page + 1) * self.total_lines_per_page:
                self.page += 1
            self.update()

    def roll_selected_skill(self):
        line = self.all_lines[self.selected_index].strip()

        # Remove arrow or spacing
        line = line.lstrip(">").strip()
        if ":" in line:
            skill_name = line.split(":", 1)[0].strip()
            try:
                result = self.character.roll_skill_by_name(skill_name)
                print(result)  # You can later show this on-screen
            except Exception as e:
                print(f"Skill roll failed: {e}")

    def show(self, hal):
        self.update()
        hal.root_group.append(self.group)

    def clear(self):
        self.viewport.set_lines([])

    def hide(self, hal):
        if self.group in hal.root_group:
            hal.root_group.remove(self.group)

    def next_page(self):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.update()
