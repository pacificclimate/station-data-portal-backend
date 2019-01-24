def dict_from_row(row):
    """Return a dict version of a SQLAlchemy result row"""
    return dict(zip(row.keys(), row))


def dicts_from_rows(rows):
    """Return a list of dicts constructed from a list of SQLAlchemy result rows"""
    return [dict_from_row(row) for row in rows]
