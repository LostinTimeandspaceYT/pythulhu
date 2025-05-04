from player_character import PlayerCharacter
from coc_dice import CthulhuDice

CHAR = "Characteristics"
HP = "Hit Points"
MP = "Magic Points"
SAN = "Sanity"

class CthulhuCharacter(PlayerCharacter):

    def __init__(self, fpath: str):
        super().__init__(fpath)
        self.prev_skill_modifier: int = 0  # used when pushing rolls.
        self.current_weapon: dict = {}
        self.skills_to_improve: list[str] = []  # Used during Development phase

    def __str__(self):
        return f"{self.name} ({self.pronoun}) — HP: {self.current_hp}, SAN: {self.current_sanity}, MP: {self.current_mp}"

    def str_plus_siz(self) -> int:
        return (
            self.characteristics["STR"]
            + self.characteristics["SIZ"]
        )

    def damage_bonus(self) -> tuple:
        """Returns a tuple (num_dice, num_side) such that -2 and -1 are const"""
        val = self.str_plus_siz()
        if val <= 64:
            return (-2, 1)
        elif 65 <= val <= 84:
            return (-1, 1)
        elif 85 <= val <= 124:
            return (0, 0)
        elif 125 <= val <= 164:
            return (1, 4)
        else:
            return (1, 6)

    def roll_damage(self, dmg_die: tuple) -> int:
        if self.db[0] == 0:
            return CthulhuDice.roll(*dmg_die)
        else:  # to prevent empty range
            return CthulhuDice.roll_multiple([dmg_die, self.db])

    def render_summary_lines(self, max_lines: int = 15) -> list[str]:
        lines = [
            f"Name: {self.name}",
            f"Pronoun: {self.pronoun}" if hasattr(self, "pronoun") else "",
            f"Age: {self.age}",
        ]

        if hasattr(self, "current_hp"):
            lines.append(f"HP: {self.current_hp}")
        if hasattr(self, "current_mp"):
            lines.append(f"MP: {self.current_mp}")
        if hasattr(self, "current_sanity"):
            lines.append(f"Sanity: {self.current_sanity}")
        if hasattr(self, "current_luck"):
            lines.append(f"Luck: {self.current_luck}")

        lines += ["", "Characteristics:"]


        for stat, val in self.characteristics.items():
            if isinstance(val, dict):
                lines.append(f"  {stat}: {val.get('Current', '-')}/{val.get('Maximum', '-')}")
            else:
                lines.append(f"  {stat}: {val}")

        if len(lines) > max_lines:
            return lines[:max_lines - 1] + ["(... more ...)"]

        # Truncate if needed
        return lines[:max_lines]

    def cast_spell(self, spell_name: str):
        print(f"Casting {spell_name}!")
        # TODO: Flesh out spell logic

    def roll_skill(self, bonus_die: int, penalty_die: int):
        return CthulhuDice.roll_skill(bonus_die, penalty_die)

    def roll_skill_by_name(self, name: str, bonus_die: int = 0, penalty_die: int = 0) -> str:
        skills = self.skills
        skill_val = None

        for skill, value in skills.items():
            if isinstance(value, dict):
                # Check nested subskills (e.g., "Firearms": {"Handgun": 60})
                if name in value:
                    skill_val = value[name]
                    break
            elif skill == name:
                skill_val = value
                break

        if skill_val is None:
            raise ValueError(f"Skill '{name}' not found")

        if isinstance(skill_val, dict):
            skill_val = skill_val.get("Current", 0)

        roll = self.roll_skill(bonus_die, penalty_die)

        outcome = "Success" if roll <= skill_val else "Failure"
        if roll <= self.get_skill_at_difficulty(skill_val, "Extreme"):
            outcome = "Extreme Success"
        elif roll <= self.get_skill_at_difficulty(skill_val, "Hard"):
            outcome = "Hard Success"
        elif roll >= self.get_fumble(skill_val):
            outcome = "Fumble"

        return f"Rolled {roll} vs {skill_val} — {outcome}"

    def get_skill_at_difficulty(self, skill_val: int, level: str) -> int:
        scale = {"Normal": 1, "Hard": 0.5, "Extreme": 0.2}
        return int(skill_val * scale.get(level, 1))

    def get_fumble(self, skill_val):
        return 100 if skill_val >= 50 else 96

    def change_hit_points(self, amount: int):
        self.sheet[CHAR][HP]["Current"] += amount

    def change_magic_points(self, amount: int):
        self.sheet[CHAR][MP]["Current"] += amount

    def change_sanity(self, amount: int):
        self.sheet[CHAR][SAN]["Current"] += amount

    def get_weapon_names(self):
        return [weapon["Name"] for weapon in self.weapons.values()]

    def set_current_weapon(self, selection: int):
        keys = list(self.weapons.keys())
        if 0 <= selection < len(keys):
            self.current_weapon = self.weapons[keys[selection]]
        else:
            raise IndexError("Invalid weapon selection")

    @property
    def characteristics(self):
        return self.sheet[CHAR]

    @property
    def pronoun(self):
        return self.sheet["Pronoun"]

    @property
    def skills(self):
        return self.sheet["Skills"]

    @property
    def db(self):
        return self.damage_bonus()

    @property
    def weapons(self):
        return self.sheet["Combat"]["Weapons"]

    @property
    def current_sanity(self):
        return self.sheet[CHAR][SAN]["Current"]

    @property
    def current_hp(self):
        return self.characteristics[HP]["Current"]

    @property
    def current_mp(self):
        return self.characteristics[MP]["Current"]

    @property
    def current_luck(self):
        return self.characteristics["Luck"]



class PulpCharacter(CthulhuCharacter):

    def __init__(self, fpath: str):
        super().__init__(fpath)

    # Modifiers
    def change_luck(self, amount: int):
        """similar to other change methods"""
        self.characteristics["Luck"] += amount

    @property
    def archetype(self):
        return self.sheet["Archetype"]

    @property
    def talents(self):
        return self.get_keys(self.sheet["Pulp Talents"])
