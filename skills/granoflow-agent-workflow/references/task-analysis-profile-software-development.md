# Software Development Task Work Profile

Apply this Profile only when the task involves code, tests, builds, or an
engineering repository, including code-bearing MCP, Agent, or Skill work. Use
it as an omission check, not a fixed rendered section. Add only triggered
requirements to the most relevant Work Document core or optional section:

Read `task-analysis-finalization.md` for every UI software task. Analysis owns
the pre-prototype Logic Draft, user-confirmed Screen Content Contract,
Responsive Prototype Bundle v2, post-prototype logical Technical Package, and
digest reconciliation. Planning must consume that package rather than
redesigning product behavior.

Read `software-structural-budget.md` when Project Definition, Planning,
execution, or Delivery needs file and function/method limits. It is the single
owner of numeric defaults, initialization, forecast, and reconciliation rules.

Read `plan-design-gate.md` when Planning or Readiness covers software code
edits. It is the single owner of the minimal sufficient Design Package
(Markdown verification test cases traced to Analysis, flowchart, data
disposition, task-local libraries, UI↔data binding when UI, prototype↔Task Work
truth check via `prototype-doc-coverage`) and fail-closed codes
`plan_design_gate_missing` / `plan_design_gate_incomplete` /
`plan_test_cases_missing` / `prototype_plan_truth_*`.

Read `prototype-doc-coverage.md` when a task `ui_prototype` is finalized,
rematched, or the user asks to change it. Analysis **Must** (1) inventory every
task-owned UI surface into `prototype_html_coverage` with high-fidelity HTML,
(2) declare `prototype_widget_reuse` against `widgets.yaml` (same role ⇒ reuse;
`widget_reuse_required` if not), and (3) map every material prototype
page/control/state/copy/flow into Task Work **and** Project Work with no
`missing`/`conflict` before Analysis close.

- current behavior, expected behavior, and reproduction evidence;
- a semantic minimum-change budget covering required changes, allowed
  touchpoints, and protected surfaces across UI, code, API, data, and
  dependencies;
- affected modules and explicit non-goals, including any architecture, design
  system, state management, dependency, public-contract, schema, rename, or
  cleanup work that is not authorized;
- logical data/schema impact judgment and current-system evidence; new physical
  tables, columns, indexes, migrations, API signatures, and class decomposition
  remain Planning decisions;
- UI judgment and evidence;
- API, compatibility, migration, authorization, and release impact;
- lint, format, type/static analysis, tests, build, and runtime smoke gates
  (Static Hygiene Suite locked in Project Work `engineering.quality_gates` per
  `static-quality-gate.md`; Delivery/Layer B must produce `quality_gate_run`
  evidence—not optional prose);
- a Plan Design Gate package for every software Plan that will edit code (and
  for light `not_required` software edits), with
  `plan_design_gate_status: passed` before Readiness may pass—see
  `plan-design-gate.md`;
- a pre-execution `Structural Change Forecast` for every software Plan (and for
  light `not_required` software edits), with Hard Gate statuses from
  `software-structural-budget.md` (`present_in_plan` → `notice_emitted` →
  `reconciled`);
- Task Integration Test Policy: if copy-only / 文字验证, **no** automated
  tests (`copy_change_tests_forbidden`); else judge whether **unit tests
  suffice**; default to no new integration tests; only when insufficient, add
  at most **2** task-local integration tests and **do not execute** them
  (manual run later)—see `task-work-document-workflow.md` and
  `user-visible-copy-boundary.md`;
- Reality Boundary anti-drift check: read
  `granoflow-review-card-draft/references/reality-boundary-cards.md`
  Anti-Drift Lifecycle. Analysis/Plan **Must** enumerate the **full**
  `reality_boundary_index` into `reality_boundary_index_review` (every row
  `related` + `disposition`; unrelated → `unrelated`). Do **not** use vector
  top-k as relatedness authority (`similar` is leak-net only, filter by full
  `fact_id`). Set `reality_boundary_check_status` /
  `reality_boundary_fact_ids` / `reality_boundary_will_change`. Every
  `will_change` **Must** carry non-empty `verification_refs` (and Plan
  verification rows that cite `fact_id` / `note_id` / `card_ids`). **Always display** a Plan card notice: itemized list when any
  `will_change`/card write is planned, otherwise one line
  「本次迭代无卡片变更」(`none: true`). Set `card_change_plan_notice` with
  `shown_to_user: true`. Before Readiness, run
  `lint_plan_reality_boundary.py` (prefer `--snapshot`). Fail as
  `reality_boundary_check_missing`,
  `reality_boundary_will_change_without_verification`, or
  `card_change_plan_notice_missing` when omitted or lint-red;
- Route UI Truth anti-drift check: read
  `granoflow-review-card-draft/references/route-ui-truth-cards.md`
  Anti-Drift Lifecycle when the task touches user-visible routes/screens.
  Enumerate full `route_ui_truth_index` into `route_ui_truth_index_review`,
  set `route_ui_truth_*` fields, require verification refs for `will_change`,
  share `card_change_plan_notice` (`kind: route_ui_truth`). Vision: freshness
  skip when `screenshot_at >= ui_changed_at`; otherwise auto-run route + op
  vision in interactive and unattended (no cost ask/skip). Before
  Readiness run `lint_plan_route_ui_truth.py` (prefer `--snapshot`). Fail as
  `route_ui_truth_check_missing`,
  `route_ui_truth_will_change_without_verification`, or
  `card_change_plan_notice_missing` when omitted or lint-red;
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
claims. Reject a Plan step that cannot map to the confirmed Outcome or Evidence.
If implementation discovers a new UI region, module, API, schema, dependency,
or architectural change outside the budget, stop before that change and request
scope confirmation or split it into a follow-up task. Do not treat adjacent
cleanup as implicit permission for a drive-by refactor.
