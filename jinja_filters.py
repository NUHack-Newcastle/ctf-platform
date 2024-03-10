def unique(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def merge_dicts(x: dict, y: dict):
    return x | y


custom_filters = {
    'unique': unique,
    'merge_dicts': merge_dicts
}
