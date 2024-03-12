import datetime
import math
from itertools import product
from statistics import mean
import os
import pprint
import pytest
from sdpb.api import crmp_network_geoserver, histories, stations
from sdpb.timing import timing


# Use this fixture in all tests in this file.
pytestmark = pytest.mark.usefixtures("flask_app")


multiplier = 1000
units = "ms"


def print_timing(f, label, print_example=False, **kwargs):
    t = timing(f, **kwargs)
    print("")
    value = t["value"]
    print(
        f"{label}"
        f"({kwargs}): "
        f"{len(value)} items; elapsed {t['elapsed'] * 1000} {units}"
    )
    if print_example:
        print("Example item")
        pprint.pprint(value[math.floor(len(value) / 2)])


# @pytest.mark.parametrize("compact", [False, True])
# @pytest.mark.parametrize("provinces", ["BC"])
# def test_histories_list(provinces, compact):
#     print_timing(
#         histories.list,
#         "histories",
#         provinces=provinces,
#         compact=compact,
#     )
#
#
# @pytest.mark.parametrize("compact", [False, True])
# @pytest.mark.parametrize("provinces", ["BC"])
# @pytest.mark.parametrize("expand", [None, "histories"])
# def test_stations_list(provinces, compact, expand):
#     print_timing(
#         stations.list,
#         "stations",
#         # print_example=True,
#         provinces=provinces,
#         compact=compact,
#         expand=expand,
#     )
#
#
# def test_crmp_network_geoserver():
#     print_timing(crmp_network_geoserver.list, "crmp_network_geoserver")


# def test_repeats_option(repeats):
#     print(f"repeats = {repeats}")


boolean = (False, True)


def dict_iter(*spec):
    """
    spec = tuple of (key_name, key_iterable)
    return iterable of dicts with keys key_name over cartesian product of
    iterables.
    :param spec:
    :return:
    """
    names = tuple(item[0] for item in spec)
    iterables = tuple(item[1] for item in spec)
    prod = product(*iterables)
    return ({name: value for name, value in zip(names, values)} for values in prod)


def print_tabular(formats, sep=" | ", **values):
    layout = sep.join(f"{{{f}}}" for f in formats)
    print(layout.format(**values))


def print_div():
    print("-" * 60)


def print_example(ts):
    print("example")
    examples = ts[0]["value"]
    pprint.pprint(examples[math.floor(len(examples) / 2)])


time_stat_formats = (
    "time_total!s:>14",
    "time_min!s:>14",
    "time_mean!s:>14",
    "time_max!s:>14",
    # "time_std!s:>14",
)


time_stat_titles = dict(
    time_total=f"tot time ({units})",
    time_min=f"min time ({units})",
    time_mean=f"mean time ({units})",
    time_max=f"max time ({units})",
    # time_std=f"std time",
)


def time_stat_values(timings):
    times = [t["elapsed"] * multiplier for t in timings]
    return dict(
        time_total=round(sum(times)),
        time_min=round(min(times)),
        time_mean=round(mean(times)),
        time_max=round(max(times)),
        # time_std = round(stdev(times)),
    )


def print_history_timing_table(provinces, repeats=1, delay=10):
    formats = (
        "provinces!s:<5",
        "compact!s:<8",
        "include_uri!s:<8",
        *time_stat_formats,
        "item_count!s:>10",
    )
    print()
    print_div()
    print("Histories")
    print()
    print_tabular(
        formats,
        compact="compact",
        include_uri="incl uri",
        provinces="prov",
        **time_stat_titles,
        item_count="# items",
    )
    for nv in dict_iter(
        ("compact", boolean),
        ("include_uri", boolean),
    ):
        args = {**nv, "provinces": provinces}
        ts = timing(histories.collection, repeats=repeats, delay=delay, **args)
        print_tabular(
            formats,
            **args,
            **time_stat_values(ts),
            item_count=len(ts[0]["value"]),
        )
        # print_example(ts)
    print_div()


def print_station_timing_table(provinces, repeats=1, delay=10):
    formats = (
        "provinces!s:<5",
        "compact!s:<8",
        "expand!s:<10",
        *time_stat_formats,
        "item_count!s:>10",
    )
    print()
    print_div()
    print("Stations")
    print_tabular(
        formats,
        compact="compact",
        provinces="prov",
        expand="expand",
        **time_stat_titles,
        item_count="# items",
    )
    for nv in dict_iter(
        ("compact", boolean),
        ("expand", ("histories", None)),
    ):
        args = {**nv, "provinces": provinces}
        ts = timing(stations.collection, repeats=repeats, delay=delay, **args)
        print_tabular(
            formats,
            **args,
            **time_stat_values(ts),
            item_count=len(ts[0]["value"]),
        )
    print_div()


def print_cng_timing_table(repeats=1, delay=10):
    formats = (*time_stat_formats, "item_count!s:>10")
    print()
    print_div()
    print("CNG")
    print()
    print_tabular(formats, **time_stat_titles, item_count="# items")
    args = dict()
    ts = timing(crmp_network_geoserver.collection, repeats=repeats, delay=delay, **args)
    print_tabular(
        formats, **args, **time_stat_values(ts), item_count=len(ts[0]["value"])
    )
    print_div()


def print_run_sep():
    print("=" * 60)


def test_print_timing_tables(items, repeats, delay):
    items = items.split(",")

    def is_item(what):
        return "*" in items or what in items

    dsn = os.getenv("PCDS_DSN")
    db = "crmp" if "crmp" in dsn else "metnorth"
    provinces = "BC" if db == "crmp" else None
    print()
    print_run_sep()
    print(
        f"{datetime.datetime.now()} "
        f"Performance test "
        f"database = {db}, "
        f"items = {items}, "
        f"repeats = {repeats}, "
        f"delay = {delay}, "
    )
    # The first use of a session appears to incur a kind of startup cost of
    # about 200 ms. In these tests, the session is created with package scope,
    # is so common to all here. The first print_cng_timing_table() is to absorb
    # the startup cost; the final one is more accurate.
    print_cng_timing_table(repeats=1)

    if is_item("history"):
        print_history_timing_table(provinces, repeats=repeats, delay=delay)
    if is_item("station"):
        print_station_timing_table(provinces, repeats=repeats, delay=delay)
    if is_item("cng"):
        print_cng_timing_table(repeats=repeats, delay=delay)
    print_run_sep()
