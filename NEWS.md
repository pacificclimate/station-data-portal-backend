# News / Release Notes

## 11.2.1

*Release date: 2023-Aug-28*

Minor changes that affect only development and deployment.

Changes:
- [Fix CMD in Dockerfile](https://github.com/pacificclimate/station-data-portal-backend/pull/68)
- [Fix Python CI](https://github.com/pacificclimate/station-data-portal-backend/pull/67)

## 11.2.0

*Release date: 2023-Aug-25*

Major change: Added attribute "tags" to /variables response that uses a single source of truth in the database to classify variables (including by climatology/observation).
User-facing changes:
- [Add attribute to /variables distinguishing observation from climatology variables](https://github.com/pacificclimate/station-data-portal-backend/pull/52)

Internal changes:
- [Loosen dependency version constraints](https://github.com/pacificclimate/station-data-portal-backend/pull/62)
- [Clean up (remove) superseded docker local test infrastructure](https://github.com/pacificclimate/station-data-portal-backend/pull/60)
- [Apply Black](https://github.com/pacificclimate/station-data-portal-backend/pull/59)
- [Convert to Poetry](https://github.com/pacificclimate/station-data-portal-backend/pull/54)

## 11.0.1

*Release date: 2022-Aug-16*

Previous release did not include updates to `NEWS.md` and `setup.py`.

## 11.0.0

*Release date: 2022-Aug-16*

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

*Release date: 2022-Aug-16*

Changes:
- [Handle histories without observations; fix station histories](https://github.com/pacificclimate/station-data-portal-backend/pull/42)
- [Accept provinces query parameter in /variables, /networks, /frequencies, /observations/counts as well](https://github.com/pacificclimate/station-data-portal-backend/pull/40)

## 2.2.0 (crmp) / 10.2.0 (master)

*Release date: 2022-Jul-22*

Changes:

- [Add station count to /networks response ](https://github.com/pacificclimate/station-data-portal-backend/pull/38)

## 2.1.0 (crmp) / 10.1.0 (master)

*Release date: 2022-Jul-18*

Changes:

- [Add provinces qp to /stations](https://github.com/pacificclimate/station-data-portal-backend/pull/37)

## 2.0.0 (crmp) / 10.0.0 (master)

*Release date: 2022-Jun-02*

**IMPORTANT**: The version numbering scheme has changed to allow `crmp` major 
versions up to 9, and to use `master` major versions >= 10. This is the first 
release in the new version numbering scheme. For more details on this, see
[Supporting CRMP while it is behind PyCDS head revision](docs/supporting-crmp.md).

**Note**: These are breaking changes. Contents of some responses have changed.

Changes:

- [Improve performance of /stations endpoint](https://github.com/pacificclimate/station-data-portal-backend/pull/34)

## 1.0.1 (crmp) / 3.0.1 (master)

*Release date: 2022-Apr-01*

Note: This release includes a change pinning PyCDS to version 3.3.0 on 
both branches (from 3.2.0 on crmp and 4.0.0 on master). This adds 
some (non-breaking) features for crmp branch and establishes compatibility 
with the current dbnorth database at this date.

Changes:
- [Update to Python >= 3.7](https://github.com/pacificclimate/station-data-portal-backend/pull/33). 


## 1.0.0 (crmp) / 3.0.0 (master)

*Release date: 2022-Feb-02*

Initial release for both branches.

DEPRECATED: This release used PyCDS 4.0.0 on branch master, which is not 
compatible with dbnorth database at the time of release.