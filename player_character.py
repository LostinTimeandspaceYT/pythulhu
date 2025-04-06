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
        self.character_sheet = JSONParser.load_json_file(fpath)

    def __call__(self):
        return self.character_sheet

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
        return JSONParser.get_value_at_key(self.character_sheet, key)

    def get_keys(self, d: dict) -> list[str]:
        """Helper method to get a list of keys, such as skills
        or characteristics.

        Args:
            d (dict): base dictionary to iterate over

        Returns:
            list[str]: a list of key:value pairs
        """
        return JSONParser.get_keys(d)

    @property
    def age(self):
        return self.character_sheet["Age"]

    @property
    def name(self):
        return self.character_sheet["Name"]
