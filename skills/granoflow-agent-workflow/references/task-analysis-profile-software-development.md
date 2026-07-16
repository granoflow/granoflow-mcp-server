# Software Development Task Work Profile

Apply this Profile only when the task involves code, tests, builds, or an
engineering repository, including code-bearing MCP, Agent, or Skill work. Use
it as an omission check, not a fixed rendered section. Add only triggered
requirements to the most relevant Work Document core or optional section:

- current behavior, expected behavior, and reproduction evidence;
- affected modules and explicit non-goals;
- database table/schema judgment and evidence;
- UI judgment and evidence;
- API, compatibility, migration, authorization, and release impact;
- lint, format, type/static analysis, tests, build, and runtime smoke gates;
- the real user-visible surface that must be rechecked;
- rollback and stop conditions.

Use `external-skill-routing.md` to select relevant engineering capabilities
from host-visible Skill metadata. Do not maintain a complete third-party Skill
catalog or copy a Skill's diagnosis, TDD, architecture, or implementation
method into this Profile. Ordinary copywriting, manga, animation, non-code
research, and general administration do not route through an engineering Skill
collection merely because their files happen to live in a repository.

If no relevant Skill is available, is allowed only by explicit user invocation,
is declined, or fails, continue with the model fallback while retaining every
gate below.

Passing tests alone is not final Evidence when a user-visible API, page, package,
registry, or deployed surface changed. Grill for false-success signals, missing
old-data handling, hidden permissions, expanded scope, and unverifiable runtime
claims.
