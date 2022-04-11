import math
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
# @pytest.mark.parametrize("province", ["BC"])
# def test_histories_list(province, compact, group_vars_in_database):
#     print_timing(
#         histories.list,
#         "histories",
#         province=province,
#         compact=compact,
#         group_vars_in_database=group_vars_in_database,
#     )
#
#
# @pytest.mark.parametrize("compact", [False, True])
# @pytest.mark.parametrize("group_vars_in_database", [False, True])
# @pytest.mark.parametrize("province", ["BC"])
# @pytest.mark.parametrize("expand", [None, "histories"])
# def test_stations_list(province, compact, expand, group_vars_in_database):
#     print_timing(
#         stations.list,
#         "stations",
#         # print_example=True,
#         province=province,
#         compact=compact,
#         group_vars_in_database=group_vars_in_database,
#         expand=expand,
#     )
#
#
# def test_crmp_network_geoserver():
#     print_timing(crmp_network_geoserver.list, "crmp_network_geoserver")


def print_tabular(formats, sep=" | ", **values):
    layout = sep.join(f"{{{f}}}" for f in formats)
    print(layout.format(**values))


def print_history_timing_table():
    formats = (
        "province!s:<5",
        "group_vars_in_database!s:<15",
        "compact!s:<8",
        "time!s:>10",
        "item_count!s:>10"
    )
    print()
    print_tabular(
        formats,
        compact="compact",
        group_vars_in_database="grp vars in db",
        province="prov",
        time=f"time ({units})",
        item_count="# items",
    )
    print()
    for province in ("BC",):
        for group_vars_in_database in (True, False):
            for compact in (False, True):
                args = dict(
                    compact=compact,
                    group_vars_in_database=group_vars_in_database,
                    province=province,
                )
                t = timing(histories.list, **args)
                print_tabular(
                    formats,
                    **args,
                    time=round(t['elapsed'] * multiplier),
                    item_count=len(t["value"]),
                )


def print_station_timing_table():
    formats = (
        "province!s:<5",
        "group_vars_in_database!s:<15",
        "compact!s:<8",
        "expand!s:<10",
        "time!s:>10",
        "item_count!s:>10"
    )
    print()
    print_tabular(
        formats,
        compact="compact",
        group_vars_in_database="grp vars in db",
        province="prov",
        expand="expand",
        time=f"time ({units})",
        item_count="# items",
    )
    print()
    for province in ("BC",):
        for group_vars_in_database in (False, True):
            for compact in (False, True):
                for expand in (None, "histories"):
                    args = dict(
                        compact=compact,
                        group_vars_in_database=group_vars_in_database,
                        province=province,
                        expand=expand,
                    )
                    t = timing(stations.list, **args)
                    print_tabular(
                        formats,
                        **args,
                        time=round(t['elapsed'] * multiplier),
                        item_count=len(t["value"]),
                    )


def print_cng_timing_table():
    formats = (
        "time!s:>10",
        "item_count!s:>10"
    )
    print()
    print_tabular(
        formats,
        time=f"time ({units})",
        item_count="# items",
    )
    print()
    args = dict()
    t = timing(crmp_network_geoserver.list, **args)
    print_tabular(
        formats,
        **args,
        time=round(t['elapsed'] * multiplier),
        item_count=len(t["value"]),
    )


def test_print_timing_tables():
    # The first use of a session appears to incurs a kind of startup cost of
    # about 200 ms. In these tests, the session is created with package scope,
    # is so common to all here. The first print_cng_timing_table() is to absorb
    # the startup cost; the final one is more accurate.
    print_cng_timing_table()
    print_history_timing_table()
    print_station_timing_table()
    print_cng_timing_table()
