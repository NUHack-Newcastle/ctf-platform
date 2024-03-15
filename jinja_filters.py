from typing import Iterable

import datetime
import pendulum


def unique(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def merge_dicts(x: dict, y: dict):
    return x | y


def friendly_timedelta(dt: datetime):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pendulum.local_timezone())
    return pendulum.instance(dt).diff_for_humans()


def is_dict_subset(x: dict, y: dict) -> bool:
    for k, v in x.items():
        if k not in y:
            return False
        if y[k] != v:
            return False
    return True


def in_any(x: Iterable[object], y: object) -> bool:
    return any(y in i for i in x)

def add_ordinal_suffix(number: int) -> str:
    s = str(number)
    if s[-1] == '1':
        return s+'st'
    if s[-1] == '2':
        return s+'nd'
    if s[-1] == '3':
        return s+'rd'
    return s+'th'



custom_filters = {
    'unique': unique,
    'merge_dicts': merge_dicts,
    'is_dict_subset': is_dict_subset,
    'in_any': in_any,
    'any': any,
    'all': all,
    'friendly_timedelta': friendly_timedelta,
    'add_ordinal_suffix': add_ordinal_suffix
}
