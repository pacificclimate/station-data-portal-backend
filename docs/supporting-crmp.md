# Supporting CRMP while it is behind PyCDS head revision (deprecated)

## Deprecation notice

The CRMP/PCDS database has been moved to a new platform running PG 10.
Therefore there is no need for the special CRMP-compatible branch and the
releases it contains. From this point onward, there will be only main
releases.

This documentation is retained only for historical purposes (e.g, it is
referenced in NEWS.md).

## Key points

To use this backend with CRMP, we must use an early release of PyCDS.
To do this, we maintain a separate branch, `crmp`, and release from it too.

Basic rules:

- All development work is done primarily on `master`; that is, `master`
  is the base branch for all PRs.
- Unit tests are written for `master` branch only. Failing unit tests on
  `crmp` are expected. `python-ci` skips tests on `crmp` branch.

Development hints:

- When merging changes in `Pipfile`to `crmp`:
  - Be careful not to change the correct version for PyCDS on this branch.
  - Run `pipenv lock` (or `pipenv install --dev`) and commit the updated 
    `Pipfile.lock` to branch `crmp`.
- If you change between `master` and `crmp` branches while running tests or 
  running the server (or some other use), you should update 
  the Pipenv environment each time. Otherwise you will be using an 
  incompatible version of PyCDS and potentially of other packages.
  - In a local Pipenv environment, issue `pipenv install --dev`. 
  - If you are running a Docker test container, 
    restart it (it recreates the Pipenv environment for you).

Releases and lifecycle:

- Releases are made both from `master` and `crmp`, usually in lockstep.
- Before creating a new release:
  - Merge `master` into `crmp`.
  - Adjust the version of PyCDS in branch `crmp` as necessary to
    remain at a compatible release. (This usually means ensuring it is
    still at its old value)
- Release numbering:
   - Branch `master`: Versions numbered >= 10.
   - Branch `crmp`: Versions numbered >= 1, < 10. This will give us a little
     flexibility in version numbering. God forbid we need more than 9.x.
   - IMPORTANT: Previously, the maximum major version number for `crmp` was 
     2 (not 9). This was overly optimistic. We now have `master` versions 
     numbered 3.x, which is a problem I hope to gloss over, hide, or leave 
     behind, mainly by skipping major version number 3 in future `crmp` releases.
- Branch `crmp` will be terminated when CRMP has been moved to a modern
  server and migrated to the head revision of PyCDS. Thereafter only
  `master` branch will be used for releases.


## Problem analysis

CRMP database is stuck at PyCDS revision 8fd8f556c548. It cannot be migrated until it is hosted on a version of PG >= 10.

PyCDS is now at a much later revision, with at least one incompatible change to the ORM (`publish` column in `meta_stations`).

metnorth database is or soon will be at the head revision.

We need to connect this backend (in different instances) to both CRMP and metnorth. That requires using two different releases of PyCDS (3.2.0 for CRMP; >= 3.3.0 for metnorth).

In both backends, we will in general need the most recent work. (In particular we will need the results of #25 .) We cannot simply use an earlier (also not yet released) version of SDPB.

## Solution options

### Option (preferred): Create two release branches for this project

- Branch `master`: For databases migrated to PyCDS head revision (or
  thereabouts; currently metnorth only). On this branch the latest version
  (or thereabouts) of PyCDS will be specified.
- Branch `crmp`: For `crmp` as it is now and at any future PyCDS revisions
  significantly short of the head revision. In this branch, a version of
  PyCDS will be specified that is compatible with the current state of the
  CRMP database.

Rules:

- All development work will be done primarily on `master`; that is, `master`
  will be the base branch for all PRs.
- Unit tests will be written for `master` branch only. Failing unit tests on
  `crmp` are expected. Update `python-ci` to skip tests on `crmp` branch.
- After changes are merged to `master`, `master` branch will be merged into
  `crmp`, and the version of PyCDS in branch `crmp` adjusted as necessary to
  remain at a compatible release.
- Releases will be made both from `master` and `crmp`, ideally in lockstep.
- Release numbering:
   - As yet, there are no official releases of this project. That makes
     things easier.
   - Branch `master`: Versions numbered >= 3.
   - Branch `crmp`: Versions numbered >= 1, < 3. This will give us a little
     flexibility in version numbering. God forbid we need more than 2.x.
- Branch `crmp` will be terminated when CRMP has been moved to a modern
  server and migrated to the head revision of PyCDS. Thereafter only
  `master` branch will be used for releases.

This option has been tested by specifying PyCDS 3.2.0 against (the latest)
version of this repo.

### Option (dispreferred): Make ad-hoc changes to CRMP

- Add `publish` column in `meta_stations`.
- This will have to be manually backed out before migrating CRMP to later
  revisions of PyCDS.
- There's no guarantee that this will work even now (non-null columns, anyone?)
  nor for future revisions of PyCDS.
- This sounds like a bad idea. 
