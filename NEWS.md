# News / Release Notes

## 12.2.0

_Release date: 2026-Aug-05_

Changes:

- [Add configurable DragonflyDB/Redis caching for metadata API responses.](https://github.com/pacificclimate/station-data-portal-backend/pull/95)

## 12.1.0

_Release date: 2026-Jun-10_

Changes:

- [add SQLAlchemy connection pool customisation, readyz route](https://github.com/pacificclimate/station-data-portal-backend/pull/93)

## 12.0.0

_Release date: 2026-May-28_

Due to the scale of the updates this is a major version update.

Changes:

- [Connexion 2->3 migration, Updated Pycds to 5.0, Sqlalchemy 2.0, revised docker build, dev tooling, updated secured github actions](https://github.com/pacificclimate/station-data-portal-backend/pull/92)

## 11.4.2

_Release date: 2025-Apr-10_

Changes:

- [Enable SQLAlechemy's pre-ping feature to reduce risk of dropped database connections](https://github.com/pacificclimate/station-data-portal-backend/pull/90)

## 11.4.1

_Release date: 2024-Apr-04_

Changes:

- [Provide a default sort order when requesting observations](https://github.com/pacificclimate/station-data-portal-backend/pull/80)
- [Fix observation counts endpoint due to ambiguous table joins](https://github.com/pacificclimate/station-data-portal-backend/pull/80)

## 11.4.0

_Release date: 2024-Mar-22_

This version adds `/stations/{station_id}/variables` , `/stations/{station_id}/variables/{variable_id}` and `/stations/{station_id}/variables/{variable_id}/observations/` to the API. These endpoint provide information about a variable in the context of a station and allow request some observations to support a "data preview" functionality in the front end.

Changes:

- [Update postgres version](https://github.com/pacificclimate/station-data-portal-backend/pull/79)
- [Remove get_all_vars_by_hx function and clean up tests depending on it](https://github.com/pacificclimate/station-data-portal-backend/pull/82)
- [Add endpoints describing variables in association with a station](https://github.com/pacificclimate/station-data-portal-backend/pull/83)

## 11.3.0

_Release date: 2023-Nov-03_

This version transfers the weather anomaly backend into this service.

Changes:

- [Transfer endpoints of Weather Anomaly Data Service to this service](https://github.com/pacificclimate/station-data-portal-backend/pull/72)

## 11.2.2

_Release date: 2023-Sep-18_

Changes:

- [Normalize date inputs to /observations/counts](https://github.com/pacificclimate/station-data-portal-backend/pull/70)

## 11.2.1

_Release date: 2023-Aug-28_

Minor changes that affect only development and deployment.

Changes:

- [Fix CMD in Dockerfile](https://github.com/pacificclimate/station-data-portal-backend/pull/68)
- [Fix Python CI](https://github.com/pacificclimate/station-data-portal-backend/pull/67)

## 11.2.0

_Release date: 2023-Aug-25_

Major change: Added attribute "tags" to /variables response that uses a single source of truth in the database to classify variables (including by climatology/observation).
User-facing changes:

- [Add attribute to /variables distinguishing observation from climatology variables](https://github.com/pacificclimate/station-data-portal-backend/pull/52)

Internal changes:

- [Loosen dependency version constraints](https://github.com/pacificclimate/station-data-portal-backend/pull/62)
- [Clean up (remove) superseded docker local test infrastructure](https://github.com/pacificclimate/station-data-portal-backend/pull/60)
- [Apply Black](https://github.com/pacificclimate/station-data-portal-backend/pull/59)
- [Convert to Poetry](https://github.com/pacificclimate/station-data-portal-backend/pull/54)

## 11.0.1

_Release date: 2022-Aug-16_

Previous release did not include updates to `NEWS.md` and `setup.py`.

## 11.0.0

_Release date: 2022-Aug-16_

The major change in this release is updating to PyCDS 4.0.0.

- [Retire crmp branch](https://github.com/pacificclimate/station-data-portal-backend/pull/50)
- [Update documentation](https://github.com/pacificclimate/station-data-portal-backend/pull/48)
- [Update PyCDS to ver 4.0.0](https://github.com/pacificclimate/station-data-portal-backend/pull/45)

### Important: Special crmp releases retired

The CRMP/PCDS database has been moved to a new platform running PG 10.
Therefore there is no need to maintain the special CRMP-compatible branch and
the releases it contains. From this point onward, there will be only main
releases numbered 11 and higher.

## 2.3.0 (crmp) / 10.3.0 (master)

_Release date: 2022-Aug-16_

Changes:

- [Handle histories without observations; fix station histories](https://github.com/pacificclimate/station-data-portal-backend/pull/42)
- [Accept provinces query parameter in /variables, /networks, /frequencies, /observations/counts as well](https://github.com/pacificclimate/station-data-portal-backend/pull/40)

## 2.2.0 (crmp) / 10.2.0 (master)

_Release date: 2022-Jul-22_

Changes:

- [Add station count to /networks response ](https://github.com/pacificclimate/station-data-portal-backend/pull/38)

## 2.1.0 (crmp) / 10.1.0 (master)

_Release date: 2022-Jul-18_

Changes:

- [Add provinces qp to /stations](https://github.com/pacificclimate/station-data-portal-backend/pull/37)

## 2.0.0 (crmp) / 10.0.0 (master)

_Release date: 2022-Jun-02_

**IMPORTANT**: The version numbering scheme has changed to allow `crmp` major
versions up to 9, and to use `master` major versions >= 10. This is the first
release in the new version numbering scheme. For more details on this, see
[Supporting CRMP while it is behind PyCDS head revision](docs/supporting-crmp.md).

**Note**: These are breaking changes. Contents of some responses have changed.

Changes:

- [Improve performance of /stations endpoint](https://github.com/pacificclimate/station-data-portal-backend/pull/34)

## 1.0.1 (crmp) / 3.0.1 (master)

_Release date: 2022-Apr-01_

Note: This release includes a change pinning PyCDS to version 3.3.0 on
both branches (from 3.2.0 on crmp and 4.0.0 on master). This adds
some (non-breaking) features for crmp branch and establishes compatibility
with the current dbnorth database at this date.

Changes:

- [Update to Python >= 3.7](https://github.com/pacificclimate/station-data-portal-backend/pull/33).

## 1.0.0 (crmp) / 3.0.0 (master)

_Release date: 2022-Feb-02_

Initial release for both branches.

DEPRECATED: This release used PyCDS 4.0.0 on branch master, which is not
compatible with dbnorth database at the time of release.
