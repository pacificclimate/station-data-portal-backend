import datetime
import math
import os
import pprint
import pytest
from sdpb.api import (
    crmp_network_geoserver,
    histories,
    stations,
)
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
# @pytest.mark.parametrize("group_vars_in_database", [False, True])
# @pytest.mark.parametrize("provinces", ["BC"])
# def test_histories_list(provinces, compact, group_vars_in_database):
#     print_timing(
#         histories.list,
#         "histories",
#         provinces=provinces,
#         compact=compact,
#         group_vars_in_database=group_vars_in_database,
#     )
#
#
# @pytest.mark.parametrize("compact", [False, True])
# @pytest.mark.parametrize("group_vars_in_database", [False, True])
# @pytest.mark.parametrize("provinces", ["BC"])
# @pytest.mark.parametrize("expand", [None, "histories"])
# def test_stations_list(provinces, compact, expand, group_vars_in_database):
#     print_timing(
#         stations.list,
#         "stations",
#         # print_example=True,
#         provinces=provinces,
#         compact=compact,
#         group_vars_in_database=group_vars_in_database,
#         expand=expand,
#     )
#
#
# def test_crmp_network_geoserver():
#     print_timing(crmp_network_geoserver.list, "crmp_network_geoserver")


# def test_repeats_option(repeats):
#     print(f"repeats = {repeats}")


def print_tabular(formats, sep=" | ", **values):
    layout = sep.join(f"{{{f}}}" for f in formats)
    print(layout.format(**values))


def print_div():
    print("-" * 60)


def print_history_timing_table(provinces, repeats=1):
    formats = (
        "provinces!s:<5",
        "group_vars_in_database!s:<15",
        "compact!s:<8",
        "total_time!s:>14",
        "avg_time!s:>14",
        "item_count!s:>10"
    )
    print()
    print_div()
    print("Histories")
    print()
    print_tabular(
        formats,
        compact="compact",
        group_vars_in_database="grp vars in db",
        provinces="prov",
        total_time=f"tot time ({units})",
        avg_time=f"avg time ({units})",
        item_count="# items",
    )
    for group_vars_in_database in (True, False):
        for compact in (False, True):
            args = dict(
                compact=compact,
                group_vars_in_database=group_vars_in_database,
                provinces=provinces,
            )
            t = timing(histories.list, repeats=repeats, **args)
            total_time = t['elapsed'] * multiplier
            print_tabular(
                formats,
                **args,
                total_time=round(total_time),
                avg_time=round(total_time/repeats),
                item_count=len(t["values"][0]),
            )
    print_div()


def print_station_timing_table(provinces, repeats=1):
    formats = (
        "provinces!s:<5",
        "group_vars_in_database!s:<15",
        "compact!s:<8",
        "expand!s:<10",
        "total_time!s:>14",
        "avg_time!s:>14",
        "item_count!s:>10"
    )
    print()
    print_div()
    print("Stations")
    print_tabular(
        formats,
        compact="compact",
        group_vars_in_database="grp vars in db",
        provinces="prov",
        expand="expand",
        total_time=f"tot time ({units})",
        avg_time=f"avg time ({units})",
        item_count="# items",
    )
    for group_vars_in_database in (False, True):
        for compact in (False, True):
            for expand in ("histories", None):
            # for expand in (None, "histories"):
                args = dict(
                    compact=compact,
                    group_vars_in_database=group_vars_in_database,
                    provinces=provinces,
                    expand=expand,
                )
                t = timing(stations.list, repeats=repeats, **args)
                total_time = t['elapsed'] * multiplier
                print_tabular(
                    formats,
                    **args,
                    total_time=round(total_time),
                    avg_time=round(total_time/repeats),
                    item_count=len(t["values"][0]),
                )
    print_div()


def print_cng_timing_table(repeats=1):
    formats = (
        "total_time!s:>14",
        "avg_time!s:>14",
        "item_count!s:>10"
    )
    print()
    print_div()
    print("CNG")
    print()
    print_tabular(
        formats,
        total_time=f"tot time ({units})",
        avg_time=f"avg time ({units})",
        item_count="# items",
    )
    args = dict()
    t = timing(crmp_network_geoserver.list, repeats=repeats, **args)
    total_time = t['elapsed'] * multiplier
    print_tabular(
        formats,
        **args,
        total_time=round(total_time),
        avg_time=round(total_time/repeats),
        item_count=len(t["values"][0]),
    )
    print_div()


def print_run_sep():
    print("=" * 60)


# @pytest.mark.parametrize("repeats", (2,))
def test_print_timing_tables(repeats):
    dsn = os.getenv("PCDS_DSN")
    db = "crmp" if "db3." in dsn else "metnorth"
    provinces = "BC" if db == "crmp" else None
    print()
    print_run_sep()
    print(
        f"{datetime.datetime.now()} "
        f"Performance test against {db} database; "
        f"repeats = {repeats}"
    )
    # The first use of a session appears to incur a kind of startup cost of
    # about 200 ms. In these tests, the session is created with package scope,
    # is so common to all here. The first print_cng_timing_table() is to absorb
    # the startup cost; the final one is more accurate.
    print_cng_timing_table(repeats=1)
    print_history_timing_table(provinces, repeats=repeats)
    print_station_timing_table(provinces, repeats=repeats)
    print_cng_timing_table(repeats=repeats)
    print_run_sep()
