from panels.base_panel import BasePanel
from panels.text_viewport import TextViewport
from call_of_cthulhu.coc_dice import CthulhuDice


class CthulhuDevelopmentPhasePanel(BasePanel):
    __slots__ = (
        "game",
        "character",
        "skills",
        "results",
        "left_view",
        "step_index",
        "finished",
        "on_complete",
    )

    def __init__(self, game, context, on_complete=None):
        super().__init__(context)
        self.game = game
        self.character = game.character
        self.skills = list(self.character.skills_to_improve)
        self.character.skills_to_improve.clear()
        self.results = []
        self.step_index = 0
        self.finished = False
        self.on_complete = on_complete

        self.left_view = TextViewport(
            x=10,
            y=10,
            width=300,
            height=220,
            max_lines=10,
            line_height=20,
            show_background=False,
        )
        self.group.append(self.left_view.group)

        if not self.skills:
            self.finished = True
            self.results = ["No skills marked for improvement."]
            self.context.show_nav_button("back", callback=self._complete)
        else:
            self.results = [
                "Development Phase",
                f"{len(self.skills)} skill(s) to improve...",
                "---",
                "Tap NEXT to begin",
            ]
            self.context.show_nav_button("next", callback=self._advance)

        self.left_view.set_lines(self.results[-10:])

    def _advance(self, button=None):
        if self.finished:
            return

        if self.step_index == 0:
            # First press, clear intro
            self.results = []

        if self.step_index < len(self.skills):
            # Handle next skill improvement
            skill = self.skills[self.step_index]
            base_val = self.character.get_value_at(skill)
            roll = CthulhuDice.roll(1, 100)
            line = f"{skill} ({base_val}%) → Rolled {roll}: "

            if roll > base_val:
                increase = CthulhuDice.roll(1, 10)
                new_val = base_val + increase
                self.character.sheet["Skills"][skill]["Current"] = new_val
                line += f"Improved by {increase} → {new_val}"
            else:
                line += "No improvement."

            self.results.append(line)
            self.step_index += 1
            self.left_view.set_lines(self.results[-10:])
            return

        # Skill improvement is finished, now perform luck refresh
        self.results.append("---")
        self.game.perform_luck_refresh(self.results)
        self.finished = True

        self.left_view.set_lines(self.results[-10:])
        self.context.hide_nav_button("next")
        self.context.show_nav_button("back", callback=self._complete)

    def _complete(self, button=None):
        if self.on_complete:
            self.on_complete()
        else:
            self.context.return_home()

    def attach_to(self):
        super().attach_to()
        if self.finished:
            self.context.show_nav_button("back", callback=self._complete)
        else:
            self.context.show_nav_button("next", callback=self._advance)
