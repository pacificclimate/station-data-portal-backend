# Performance testing

Performance tests allow us to get a feel for the performance of the
API in a production context, and to compare various approaches (SQL 
queries) to obtaining the values returned.

Performance tests require connection to (typically) a production database,
and therefore must be run inside the firewall. They are not suitable for CI or 
other cloud-based test execution.

Performance test code is mainly in `tests/performance/`; it also makes use of 
common helper functions and `conftest.py` in `tests/`.

## Running the tests

Performance tests are run against a specific production database. That 
database is specified by the environment variable `PCDS_DSN`. 

When you have set `PCDS_DSN` to the target database, run:

```
poetry run pytest tests/performance
```

## Test output

An example (somewhat outdated) of performance test output against the 
CRMP database is as shown below.

Notes:
- All tests (including CNG = crmp_network_geoserver) filter on province == BC.
- "grp vars in db" means "Perform grouping of vars by history id in the 
  database query" as opposed to in Python code after obtaining the ungrouped 
  values via a simpler query.
- "compact" means compact representation, which means not including a small 
  number of seldom-used attributes. "compact" for stations also implies 
  "compact" for the expanded histories (if present) in the stations.
- "expand" applies to stations and indicates whether to expand the history 
  items associated to each station or simply to provide URIs of associated 
  history items.
- The CNG test is run twice because the first use of a session incurs a 100 
  to 200 ms overhead. The first query absorbs that so that all other query 
  timings are comparable. 

```
--------------------
CNG

 time (ms) |    # items

       832 |       6747

--------------------
Histories

prov  | grp vars in db  | compact  |  time (ms) |    # items

BC    | True            | False    |       1337 |       6960
BC    | True            | True     |       1269 |       6960
BC    | False           | False    |       1295 |       6960
BC    | False           | True     |       1243 |       6960

--------------------
Stations

prov  | grp vars in db  | compact  | expand     |  time (ms) |    # items

BC    | False           | False    | None       |       1043 |       6695
BC    | False           | False    | histories  |       2024 |       6695
BC    | False           | True     | None       |       1085 |       6695
BC    | False           | True     | histories  |       2079 |       6695
BC    | True            | False    | None       |        880 |       6695
BC    | True            | False    | histories  |       2124 |       6695
BC    | True            | True     | None       |        816 |       6695
BC    | True            | True     | histories  |       2083 |       6695

--------------------
CNG

 time (ms) |    # items

       693 |       6747
```
