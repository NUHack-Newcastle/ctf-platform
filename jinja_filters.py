from typing import Iterable


def unique(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def merge_dicts(x: dict, y: dict):
    return x | y


def is_dict_subset(x: dict, y: dict) -> bool:
    for k, v in x.items():
        if k not in y:
            return False
        if y[k] != v:
            return False
    return True


def in_any(x: Iterable[object], y: object) -> bool:
    return any(y in i for i in x)


custom_filters = {
    'unique': unique,
    'merge_dicts': merge_dicts,
    'is_dict_subset': is_dict_subset,
    'in_any': in_any
}
