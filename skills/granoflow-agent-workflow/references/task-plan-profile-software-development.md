# Legacy Software Development Plan Profile

This file preserves legacy Plan interpretation. New Work Documents use
`task-analysis-profile-software-development.md` as the single conditional
software omission check across Analysis and applicable Planning.

When reading a legacy software Plan, preserve these requirements:

- current and expected behavior;
- change surface and explicit non-changes;
- database/migration/old-data decision;
- UI/component/copy decision;
- file and method responsibility/size budgets;
- development sequence and static gates;
- compatibility, API drift, release order, rollback, and separate release authorization;
- final user-visible or runtime evidence.

Prefer: reproduce or freeze failing Evidence, implement the smallest complete change, run targeted checks, run static/full project gates, then recheck the real user surface. A zero exit code alone is not final Evidence when the analysis names a higher-level outcome.
