import json
from collections import OrderedDict


class JSONParser:
    """
    For when we must parse and sort
    complex json files ourselves.
    """

    @classmethod
    def load_json_file(cls, fpath: str):
        json_str = ""
        with open(fpath, "r") as file:
            for entry in file:
                json_str += entry
        tmp_file = json.loads(json_str)
        return cls.sort_json_file(tmp_file)

    @classmethod
    def sort_json_file(cls, d: dict):
        sorted_file = OrderedDict(sorted(d.items()))
        for k, v in sorted_file.items():
            if isinstance(v, dict) or isinstance(v, OrderedDict):
                sorted_dict = cls.sort_json_file(v)
                sorted_file.update({k: sorted_dict})
        return sorted_file

    @classmethod
    def pretty_print_keys(cls, d: dict, indent=0):
        """
        Helper for nested dictionary keys to screens.

        The default behavior is indent subentries by 2 spaces
        per depth level.

        ex.
            Language
              English
              French

            Weapons
              Firearms
                Pistol
                  .45 Automatic
                Shotgun
        """
        for k, v in d.items():
            yield "  " * indent + str(k)
            if isinstance(v, (dict, OrderedDict)):
                yield from cls.pretty_print_keys(v, indent + 1)

    @classmethod
    def get_all_vals(cls, d: dict):
        for v in d.values():
            if isinstance(v, (dict, OrderedDict)):
                yield from cls.get_all_vals(v)
            else:
                yield v

    @classmethod
    def get_keys(cls, d: dict) -> list[str]:
        return list(cls.pretty_print_keys(d))

    @classmethod
    def get_vals(cls, d: dict) -> list:
        return list(cls.get_all_vals(d))

    @classmethod
    def get_value_at_key(cls, d: dict, key: str):
        if key in d:
            return "v" if isinstance(d[key], (dict, OrderedDict)) else d[key]

        for v in d.values():
            if isinstance(v, (dict, OrderedDict)):
                value = cls.get_value_at_key(v, key)
                if value is not None:
                    return value
    
    @classmethod
    def flatten_keys(cls, d: dict, parent_key="", sep=" -> ", out=None):
        if out is None:
            out = {}
        for k, v in d.items():
            full_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, (dict, OrderedDict)):
                out[full_key] = "v"
                cls.flatten_keys(v, full_key, sep=sep, out=out)
            else:
                out[full_key] = v
        return out
