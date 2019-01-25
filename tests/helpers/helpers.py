def foo():
    return True


def dictIsSubset(a, b):
    """Return boolean indicating if dict a is a subset of dict b"""
    return set(a.items()).issubset(set(b.items()))


def omit(d, keys):
    """Return a dict with the indicated keys omitted."""
    return {k: d[k] for k in d if k not in keys}
