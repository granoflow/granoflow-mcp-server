# Software Development Task Analysis Profile

Add only the following material to section 8 of the base analysis template:

- current behavior, expected behavior, and reproduction evidence;
- affected modules and explicit non-goals;
- database table/schema judgment and evidence;
- UI judgment and evidence;
- API, compatibility, migration, authorization, and release impact;
- lint, format, type/static analysis, tests, build, and runtime smoke gates;
- the real user-visible surface that must be rechecked;
- rollback and stop conditions.

Passing tests alone is not final Evidence when a user-visible API, page, package,
registry, or deployed surface changed. Grill for false-success signals, missing
old-data handling, hidden permissions, expanded scope, and unverifiable runtime
claims.
