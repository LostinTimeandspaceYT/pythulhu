from adafruit_display_shapes.line import Line
from panels.text_viewport import TextViewport
from panels.base_panel import BasePanel

class SkillsPanel(BasePanel):
    def __init__(self, game, context, x=10, y=10, width=300, height=160, lines_per_column=7):
        super().__init__(context)
        self.game = game
        self.lines_per_column = lines_per_column
        self.total_lines_per_page = lines_per_column * 2
        self.selected_index = 0
        self.page = 0

        self.last_encoder_position = self.hal.get_encoder_position()
        self.awaiting_release = False

        self.left_view = TextViewport(
            x=x,
            y=y,
            width=width // 2 - 5,
            height=height,
            max_lines=lines_per_column,
            line_height=14,
            show_background=False,
            background_color=0x111133,
        )

        self.right_view = TextViewport(
            x=x + width // 2 + 5,
            y=y,
            width=width // 2 - 5,
            height=height,
            max_lines=lines_per_column,
            line_height=14,
            show_background=False,
            background_color=0x111133,
        )

        self.group.append(self.left_view.group)
        self.group.append(self.right_view.group)
        # Vertical divider line between the columns
        divider_x =  width // 2
        self.divider = Line(divider_x, y, divider_x, y + height, color=0x444444)
        self.group.append(self.divider)

        self.all_lines = self.get_all_skill_lines()
        self.total_pages = (len(self.all_lines) + self.total_lines_per_page - 1) // self.total_lines_per_page

    def attach_to(self):
        super().attach_to()
        self.context.show_nav_button("prev", callback=lambda b: self.prev_page())
        self.context.show_nav_button("back", callback=lambda b: self.context.return_home())
        self.context.show_nav_button("next", callback=lambda b: self.next_page())
        self.update_page()
        self.mode = "select"
        self.last_encoder_position = self.hal.get_encoder_position()
        import gc
        gc.collect()
        print("[DEBUG] After attaching SkillsPanel, mem_free:", gc.mem_free())

    def detach_from(self):
        self.all_lines = []
        return super().detach_from()


    def get_all_skill_lines(self) -> list[str]:
        sheet = self.game.character.sheet
        skills = sheet.get("Skills", {})
        lines = []

        for skill, value in skills.items():
            if isinstance(value, dict) and not isinstance(value.get("Current"), int):
                lines.append(f"{skill}:")
                for subskill, subval in value.items():
                    val = subval.get("Current", "-") if isinstance(subval, dict) else subval
                    key = f"{subskill}"
                    mark = " !" if key in self.game.character.skills_to_improve else ""
                    lines.append(f"  {subskill}: {val}{mark}")
            else:
                val = value.get("Current", "-") if isinstance(value, dict) else value
                mark = " !" if skill in self.game.character.skills_to_improve else ""
                lines.append(f"{skill}: {val}{mark}")

        return lines

    def refresh_skills(self):
        self.all_lines = self.get_all_skill_lines()
        self.total_pages = (len(self.all_lines) + self.total_lines_per_page - 1) // self.total_lines_per_page
        self.update_page()

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
            self.selected_index = self.page * self.total_lines_per_page
            self.update_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.selected_index = self.page * self.total_lines_per_page
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
        from call_of_cthulhu.coc_skill_roll_panel import SkillRollPanel
        skill_val = self.game.character.get_value_at(skill_name)

        def close_panel(_result=None):
            self.refresh_skills()
            self.context.transition_to("main")

        self.game.get_panel_pool().release("skills")
        self.hal.clear_display()
        # Debugging. This panel uses a f***-ton of memory
        import gc
        gc.collect()
        print("[DEBUG] Released SkillsPanel:", gc.mem_free())

        roll_panel = self.context.get_panel("roll")
        if roll_panel:
            roll_panel.reset(skill_name=skill_name)
        else:
            roll_panel = SkillRollPanel(
                game=self.game,
                context=self.context,
                skill_name=skill_name,
                skill_val=skill_val,
                cancel_callback=close_panel
            )
            self.context.cache_panel("roll", roll_panel)

        self.context.transition_to("roll")
