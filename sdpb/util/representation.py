import dateutil.parser


def dict_from_row(row):
    """Return a dict version of a SQLAlchemy result row"""
    return dict(zip(row.keys(), row))


def dicts_from_rows(rows):
    """
    Return a list of dicts constructed from a list of SQLAlchemy result rows
    """
    return [dict_from_row(row) for row in rows]


def date_rep(date):
    return date.isoformat() if date else None


def float_rep(x):
    return float(x) if x is not None else None


def is_expanded(item, expand):
    items = (expand or "").split(",")
    return item in items or "*" in items


def parse_date(s):
    if s is None:
        return None
    return dateutil.parser.parse(s)


def obs_stats_rep(obs_stats):
    return {
        "min_obs_time": obs_stats and date_rep(obs_stats.min_obs_time),
        "max_obs_time": obs_stats and date_rep(obs_stats.max_obs_time),
        # "obs_count": int(obs_stats.obs_count),
    }
