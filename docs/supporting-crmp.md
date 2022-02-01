# Supporting CRMP while it is behind PyCDS head revision

## Key points

CRMP requires a backend that uses an early release of PyCDS.
To do this, we maintain a separate branch, `crmp`.

- All development work is done primarily on `master`; that is, `master`
  is the base branch for all PRs.
- Unit tests are written for `master` branch only. Failing unit tests on
  `crmp` are expected. `python-ci` skips tests on `crmp` branch.
- After changes are merged to `master`, `master` branch is merged into
  `crmp`, and the version of PyCDS in branch `crmp` adjusted as necessary to
  remain at a compatible release.
- Releases is made both from `master` and `crmp`, ideally in lockstep.
- Release numbering:
   - Branch `master`: Versions numbered >= 3.
   - Branch `crmp`: Versions numbered >= 1, < 3. This will give us a little
     flexibility in version numbering. God forbid we need more than 2.x.
- Branch `crmp` will be terminated when CRMP has been moved to a modern
  server and migrated to the head revision of PyCDS. Thereafter only
  `master` branch will be used for releases.


## Problem

CRMP database is stuck at PyCDS revision 8fd8f556c548. It cannot be migrated until it is hosted on a version of PG >= 10.

PyCDS is now at a much later revision, with at least one incompatible change to the ORM (`publish` column in `meta_stations`).

metnorth database is or soon will be at the head revision.

We need to connect this backend (in different instances) to both CRMP and metnorth. That requires using two different releases of PyCDS (3.2.0 for CRMP; >= 3.3.0 for metnorth).

In both backends, we will in general need the most recent work. (In particular we will need the results of #25 .) We cannot simply use an earlier (also not yet released) version of SDPB.

## Solutions

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
