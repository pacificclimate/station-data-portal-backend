from itertools import groupby


def foo():
    return True


def dictIsSubset(a, b):
    """Return boolean indicating if dict a is a subset of dict b"""
    return set(a.items()).issubset(set(b.items()))


def omit(d, keys):
    """Return a dict with the indicated keys omitted."""
    return {k: d[k] for k in d if k not in keys}


def find(items, cond, default=None):
    """Find first item in iterable that satisfies condition cond"""
    return next((item for item in items if cond(item)), default)


def groupby_dict(items, key):
    return {k: list(g) for k, g in groupby(sorted(items, key=key), key=key)}
