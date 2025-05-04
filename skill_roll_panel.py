import displayio
from adafruit_display_text.label import Label
import terminalio
from touch_ui import TouchButton, LightTouchButton

class SkillRollPanel:
    def __init__(self, character, skill_name, confirm_callback, cancel_callback):
        self.character = character
        self.skill_name = skill_name
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

        self.group = displayio.Group()
        self.bonus_dice = 0
        self.penalty_dice = 0
        self.difficulty_levels = ["Normal", "Hard", "Extreme"]
        self.difficulty_index = 0

        # Title label
        self.title = Label(terminalio.FONT, text=f"Roll: {skill_name}", color=0xFFFFFF, x=10, y=10)
        self.group.append(self.title)

        # Bonus/Penalty Controls
        self.bonus_label = Label(terminalio.FONT, text="Bonus Dice: 0", color=0xFFFFFF, x=10, y=40)
        self.group.append(self.bonus_label)

        self.bonus_minus = LightTouchButton("bonus_minus", 180, 34, 20, 20, "-", callback=self.decrease_bonus)
        self.bonus_plus = LightTouchButton("bonus_plus", 210, 34, 20, 20, "+", callback=self.increase_bonus)

        # Difficulty
        self.difficulty_label = Label(terminalio.FONT, text="Difficulty: Normal", color=0xFFFFFF, x=10, y=70)
        self.group.append(self.difficulty_label)

        # Result display
        self.result_label = Label(terminalio.FONT, text="", color=0xFFFF00, x=10, y=110)
        self.group.append(self.result_label)

        # Action buttons
        self.roll_btn = TouchButton("roll", 180, 180, 100, 30, "Roll", callback=confirm_callback)

    def attach_to(self, root_group, manager):
        root_group.append(self.group)
        for btn in [self.bonus_minus, self.bonus_plus, self.roll_btn]:
            btn.attach_to(root_group)
            btn.register(manager)

    def detach_from(self, root_group, manager):
        if self.group in root_group:
            root_group.remove(self.group)
        for btn in [self.bonus_minus, self.bonus_plus, self.cancel_btn, self.roll_btn]:
            btn.remove_from(root_group)
            btn.unregister(manager)

    def increase_bonus(self, button):
        self.bonus_dice += 1
        self.update_bonus_label()

    def decrease_bonus(self, button):
        if self.bonus_dice > 0:
            self.bonus_dice -= 1
        self.update_bonus_label()

    def update_bonus_label(self):
        self.bonus_label.text = f"Bonus Dice: {self.bonus_dice}"

    def update_difficulty(self):
        self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulty_levels)
        self.difficulty_label.text = f"Difficulty: {self.difficulty_levels[self.difficulty_index]}"

    def roll(self, button):
        difficulty = self.difficulty_levels[self.difficulty_index]
        result = self.character.roll_skill_by_name(
            self.skill_name,
            bonus_die=self.bonus_dice,
            penalty_die=0  # Add penalty logic if needed
        )
        self.result_label.text = result
        if self.confirm_callback:
            self.confirm_callback(result)
