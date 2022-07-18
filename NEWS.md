# News / Release Notes

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