from game.player_character import PlayerCharacter

CHAR = "Characteristics"
HP = "Hit Points"
MP = "Magic Points"
SAN = "Sanity"


class CthulhuCharacter(PlayerCharacter):
    def __init__(self, fpath: str):
        super().__init__(fpath)
        self.prev_skill_modifier = 0
        self.current_weapon = {}
        self.skills_to_improve: set[str] = set()

        self._improvement_path = fpath.rsplit(".", 1)[0] + ".improve.txt"
        self._load_improvements()

    def __str__(self):
        return f"{self.name} ({self.pronoun}) — HP: {self.current_hp}, SAN: {self.current_sanity}, MP: {self.current_mp}"

    def _load_improvements(self):
        try:
            with open(self._improvement_path, "r") as f:
                self.skills_to_improve = {line.strip() for line in f if line.strip()}
        except OSError:
            self.skills_to_improve = set()

    def _save_improvements(self):
        try:
            with open(self._improvement_path, "w") as f:
                for skill in sorted(self.skills_to_improve):
                    f.write(skill + "\n")
        except OSError as e:
            print("Failed to save improvements:", e)

    def str_plus_siz(self) -> int:
        return self.characteristics["STR"] + self.characteristics["SIZ"]

    def get_build(self) -> int:
        """Pg 33 of the Keeper's Handbook"""
        val = self.str_plus_siz()
        if val <= 64:
            return -2
        elif 65 <= val <= 84:
            return -1
        elif 85 <= val <= 124:
            return 0
        elif 125 <= val <= 164:
            return 1
        else:
            return 2

    def damage_bonus(self) -> tuple[int, int]:
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

    def mark_skill_for_improvement(self, skill_name: str):
        if skill_name not in self.skills_to_improve:
            self.skills_to_improve.add(skill_name)
            self._save_improvements()

    def unmark_skill(self, skill_name: str):
        if skill_name in self.skills_to_improve:
            self.skills_to_improve.remove(skill_name)
            self._save_improvements()

    def clear_improvements(self):
        self.skills_to_improve.clear()
        self._save_improvements()

    def get_improvable_skills(self) -> list[str]:
        return sorted(self.skills_to_improve)

    def cast_spell(self, spell_name: str):
        print(f"Casting {spell_name}!")
        # TODO: Flesh out spell logic

    def set_hit_points(self, value: int):
        self.sheet[CHAR][HP]["Current"] = max(0, value)

    def set_magic_points(self, value: int):
        self.sheet[CHAR][MP]["Current"] = max(0, value)

    def set_sanity(self, value: int):
        self.sheet[CHAR][SAN]["Current"] = max(0, value)

    def set_luck(self, value: int):
        self.characteristics["Luck"] = max(0, value)

    def get_weapon_names(self):
        return [weapon["Name"] for weapon in self.weapons.values()]

    def set_current_weapon(self, selection: int):
        keys = list(self.weapons.keys())
        if 0 <= selection < len(keys):
            self.current_weapon = self.weapons[keys[selection]]
        else:
            raise IndexError("Invalid weapon selection")

    def get_weapon_skill_val(self):
        skill_name = self.current_weapon.get("Skill")
        return self.get_value_at(skill_name) if skill_name else 0

    def get_weapon_dice(self):
        """
        Returns extra dice needed to roll for damage
          - dice_list: list of (num, sides)
          - If db if found, adds db to list
        Accepts weapon['Damage'] as:
          - string like '1d8+db' or '1d6+1d4'
          - tuple (num, sides)
          - list of tuples [(num, sides), ...]
        """

        dmg = self.current_weapon.get("Damage")
        if dmg is None:
            return []

        # string like "1d8+db" or "1d6+1d4"
        if isinstance(dmg, str):
            s = dmg.replace(" ", "").lower()
            parts = [p for p in s.split("+") if p]
            dice = []
            for p in parts:
                if p == "db":
                    dice.append(self.db)
                    continue
                if "d" in p:
                    n_str, s_str = p.split("d", 1)
                    try:
                        n = int(n_str) if n_str else 1
                        sides = int(s_str)
                        dice.append((n, sides))
                    except ValueError:
                        # ignore malformed segment
                        continue
                else:
                    # Support constants like "+1" → (1,1) and "-1" → (-1,1)
                    try:
                        k = int(p)
                        dice.append((k, 1))
                    except ValueError:
                        continue

            return dice

        # Non-string formats aren’t expected by contract; return empty
        return ([], False)

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
    def build(self):
        return self.get_build()

    @property
    def weapons(self):
        return self.sheet["Weapons"]

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

    @property
    def archetype(self):
        return self.sheet["Archetype"]

    @property
    def talents(self):
        return self.get_keys(self.sheet["Pulp Talents"])
