"""
Module for Character sheet manipulation 
"""

__author__ = "Nathan Winslow"
__copyright__ = "MIT"

from json_parser import JSONParser


class PlayerCharacter:
    """Base class that provides a simple interface to 
    getting and setting values in a PC's character sheet.
    """

    def __init__(self, fpath: str):
        self._sheet = JSONParser.load_json_file(fpath)

    def get_value_at(self, key: str) -> any:
        """searches through `character_sheet` for an entry at `key` and
        returns the assoicated value. This method will traverse the entire
        character sheet, making it difficult to find values who share the
        same key.

        Args:
            key (str): key you want the value of. 

        Returns:
            any: value at key if it exists, None otherwise
        """
        return JSONParser.get_value_at_key(self._sheet, key)

    def get_keys(self, d: dict) -> list[str]:
        """Helper method to get a list of keys, such as skills
        or characteristics.

        Args:
            d (dict): base dictionary to iterate over

        Returns:
            list[str]: a list of key:value pairs
        """
        return JSONParser.get_keys(d)

    def render_summary_lines(self) -> list[str]:
            """Returns a list of displayable summary lines for the character sheet."""
            lines = [
                f"Name: {self.name}",
                f"Age: {self.age}",
            ]

            pronoun = self._sheet.get("Pronoun")
            if pronoun:
                lines.append(f"Pronoun: {pronoun}")

            if "Characteristics" in self._sheet:
                char = self._sheet["Characteristics"]
                lines += [
                    "",
                    "Characteristics:"
                ]
                for stat, val in char.items():
                    if isinstance(val, dict):
                        lines.append(f"  {stat}: {val.get('Current','-')}/{val.get('Max','-')}")
                    else:
                        lines.append(f"  {stat}: {val}")
            return lines

    @property
    def sheet(self):
        return self._sheet

    @property
    def age(self):
        return self._sheet["Age"]

    @property
    def name(self):
        return self._sheet["Name"]
