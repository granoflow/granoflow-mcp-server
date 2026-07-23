# Plan Design Gate

Single owner for the **minimal sufficient** software Planning package that a
cold-start Agent can implement without guessing. Structural line budgets stay in
`software-structural-budget.md`. Schema/data attachment rules stay in
`task-authoring-quality-contract.md`. This gate answers: _what must be in the
Plan so execution is controllable, and so Analysis requirements are verifiable
in code?_

Load via `granoflow_bundled_skill_reference` (`referenceId: plan-design-gate`)
when software Planning, Readiness, or pre-execution review runs.

## When It Applies

| Case                                                                                                                | Gate                                      |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Software profile (or any task that will edit code, tests, or build files) and Planning is `required` or `confirmed` | **required**                              |
| `planning_status: not_required` but the task will still edit code/tests/build                                       | **required** (compact form allowed)       |
| Non-software work, or software Analysis-only with no code edit                                                      | `plan_design_gate_status: not_applicable` |

Do not invent a second Planning template. Put Gate content under the existing
`Recommended Approach`, `Database / Migration`, `Structural Change Forecast`,
`Verification Plan`, and `Execution Plan` sections (see
`task-work-document-template.md`).

For UI software tasks, Planning must first load the passed
`analysis_technical_package` and record its SHA. Inherited logical flows, state
models, permissions, and UI-to-data bindings may be referenced by exact
section/evidence ref instead of copied. Planning owns only the physical and
implementation decisions layered on that logical authority.

## Minimal Sufficient Set

Every required Gate must include all of the following. Omit nothing by claiming
"obvious"; if an item is truly N/A, say so with a one-line basis.

1. **Verification test cases (Markdown table)** — the primary Plan artifact for
   landing Analysis into code. Each hard Analysis requirement (Outcome,
   Evidence item, protected surface, false-success exclusion) maps to at least
   one row. Prefer this over UML for proving "done". Columns (localize headers;
   keep semantics):

   | Case ID | Traces to (Outcome / Evidence / Scope / Risk) | Preconditions | Steps | Expected | Kind (unit / widget / manual) | False-success exclusion |

   Rules:

   - Every protected surface and every Evidence bullet that this task claims
     gets ≥1 case.
   - `Kind=unit` or `widget` must be implementable as automated tests in
     Execution; `manual` stays on a short hand-test list and must not be
     silently dropped.
   - If a case cannot run yet (missing upstream fixture), mark
     `blocked_by_dependency:<task-or-artifact>` — do not pretend it passed.
   - Do **not** maintain a separate Acceptance Path Map when this table already
     carries traceability in **Traces to**. A short path map is optional only
     when it reduces duplication for multi-acceptance portfolios.
   - Delivery and readiness claims must tick these rows; an Outcome with no
     matching passed/blocked-explained case fails closed as incomplete
     evidence.

2. **Operation flowchart** (Mermaid `flowchart`) — main path plus failure and
   protected-surface branches that implementers must not collapse. Required when
   the task has non-trivial control flow; a current Analysis Technical Package
   flow may be referenced by SHA instead of duplicated. Planning adds a new
   flow only for implementation sequencing that the logical flow does not own.

3. **Data structure disposition** — inherit the logical disposition from the
   Analysis Technical Package, then add the physical Planning decision in
   frontmatter `data_disposition` plus a short table or bullets with basis:
   - `unchanged` — consume existing schema/contracts; no invent-on-the-fly
   - `extend` — additive fields/contracts; follow data_model / json_contracts
     writeback rules
   - `breaking` — incompatible change; stop unless already authorized and
     attachments updated

   Explicit `unchanged` with basis is required when nothing changes. Do not
   leave disposition implied.

4. **External libraries** — only packages this task will call that sit outside
   the language/runtime core (for Flutter: not the Dart/Flutter SDK itself).
   For each: name, `approved` / `needs_decision`, and the **concrete capability**
   used. New capability-critical libraries require Project Work
   `dependencies.approved` update before continuing (`needs_decision` → stop).

5. **UI ↔ data binding** — **only when** the task has a UI change or confirmed
   `ui_prototype`. Reference the passed Analysis binding by SHA and add only
   physical field/event/API mappings needed for implementation. Do not
   duplicate or silently override product behavior. Non-UI tasks omit this
   subsection.

5b. **Prototype ↔ Task Work truth check** — when a confirmed `ui_prototype`
exists, load `prototype-doc-coverage` and emit `prototype_plan_truth`.
Re-diff the **current App prototype** against Task Work. On conflict:
the prototype owns visual presentation while the accepted Screen Content
Contract owns product behavior. Notify the user with recommendation items;
behavior changes reopen Analysis and update the Content Contract before HTML
and Task/Project Work; lint
`lint_prototype_doc_coverage.py --kind plan_truth`. Do **not** set
`plan_design_gate_status: passed` while
`prototype_plan_truth.status: conflict` and
`user_resolution: pending` (`prototype_plan_truth_conflict`).

6. **User-visible copy (locale-bound)** — when the task introduces or changes
   user-visible strings, inventory final copy for the Plan locale. Locale
   resolution (hard): user-explicit product/UI language if given; else the
   language of the current user↔AI conversation. Multilingual products: Plan
   designs **only** that locale; other locales are Execution work. Full rules:
   `milestone-plan-acceptance-pack.md` (Copy Language).

7. **Structural Change Forecast** — concrete expected files/symbols per
   `software-structural-budget.md`. Uncertain names may be `provisional` /
   `expected`; vague "lib/ related pages" alone fails this Gate.

### Optional diagrams (add only when they help implementation)

| Diagram           | Add when                                            |
| ----------------- | --------------------------------------------------- |
| State diagram     | Multiple durable UI/domain states or failure kinds  |
| Sequence diagram  | Cross-module collaboration that a flowchart hides   |
| Class / ER sketch | This task creates or extends persisted model shapes |

**Do not** add class/sequence/full UML suites that do not change how code will
be written. Decorative diagrams fail Review as noise, not as Gate credit. Prefer
expanding the **test case table** when the gap is "how do we know Analysis
landed," not "draw another diagram."

## Forbidden Hollow Plans

Fail closed when Planning for a Gate-required task has any of:

- missing or empty verification test case table;
- Analysis Outcome / Evidence / protected surfaces with no traced test case
  row;
- an Execution Plan step whose Action is only generic "implement Outcome" /
  "minimal change" **without** referencing the test cases, flowchart,
  disposition, libraries, UI binding (if UI), or Forecast files;
- Forecast that cites only line counts or "related modules" with no paths;
- listing every Project Work dependency instead of **task-local** libraries;
- `data_disposition` missing while claiming readiness;
- UI task missing UI ↔ data binding against the **current** App prototype;
- UI task missing or stale `analysis_technical_package_sha256`, or Planning
  restating conflicting logical behavior instead of reopening Analysis;
- UI task with unresolved `prototype_plan_truth` conflict
  (`prototype_plan_truth_conflict` / `prototype_plan_truth_docs_stale`);
- user-visible copy in Scope without a locale-bound copy inventory
  (`plan_copy_missing` / `plan_copy_locale_unresolved`).

Codes:

- `plan_design_gate_missing` — Gate required but section/metadata absent
- `plan_design_gate_incomplete` — present but missing a required item above
- `plan_test_cases_missing` — verification table absent or untraced to Analysis
- `plan_copy_missing` / `plan_copy_locale_unresolved` — see acceptance pack
- `prototype_plan_truth_conflict` / `prototype_plan_truth_unnotified` /
  `prototype_plan_truth_docs_stale` / `prototype_plan_truth_sot_invalid` —
  see `prototype-doc-coverage.md`

## Metadata

```yaml
plan_design_gate_status: not_applicable | pending | passed
plan_design_diagrams: [] # e.g. [flowchart, state] — diagrams actually included
data_disposition: not_applicable | unchanged | extend | breaking
analysis_technical_package_sha256: null | <64 lowercase hex>
```

- Set `pending` while drafting or awaiting the normal Plan acceptance gate.
  Ordinary users are not required to approve inherited professional notation.
- Set `passed` only after the Gate content is complete **and** (interactive)
  the user has accepted it, or (unattended) a valid current authorization
  covers Planning confirmation and the Gate is complete with no
  `needs_decision` library.
- Readiness Grill must not set `readiness_grill_status: passed` while status is
  `pending` or the Gate is incomplete (`plan_design_gate_incomplete` /
  `plan_test_cases_missing`).
- Do not request `execution_authorization` / start code edits while Gate is
  required and not `passed`.

## Recommended Approach Shape

Under `## Recommended Approach`, use these subsections when triggered (localize
heading language to the user; keep semantics):

- `### Verification Test Cases` (required for Gate-required software Plans)
- `### Operation Flow`
- `### State Model` (optional)
- `### Collaboration Sequence` (optional)
- `### Domain Model` (optional; prefer data_model attachment when schema changes)
- `### Data Structure Disposition`
- `### External Libraries`
- `### UI ↔ Data Binding` (UI only)
- `### User-visible Copy` (when strings change; selected locale only)

Keep a short prose lead-in for the approach; do not replace Outcome/Scope.
Fold former "Acceptance Path Map" content into the test case **Traces to**
column unless a separate map truly reduces duplication.

## Readiness And Execution

1. Planning discussion for software work **builds** the Gate—including the test
   case table—before claiming the Plan is executable.
2. Readiness Grill checks Gate completeness together with prototype, forecast,
   and other readiness prerequisites; incomplete or untraced test cases block
   `passed`.
3. Before the first edit, still show Structural Change Forecast
   (`notice_emitted`) per `software-structural-budget.md` — Gate `passed` does
   not waive that notice.
4. Execution implements automated cases first where `Kind` allows, then manual
   rows; Delivery ticks each row (`passed` / `failed` / `blocked_by_dependency`
   with reason). When the task belongs to a milestone with an accepted
   `milestone-plan-acceptance-pack`, treat that pack as the primary
   milestone-level alignment reference (copy / schema / flows / UML / TC
   inventory) per `milestone-plan-acceptance-pack.md` § Implementation And
   Delivery Reference; Task Work remains the per-task execution authority.
5. If execution discovers the flowchart, disposition, Forecast, test cases, or
   accepted pack content are wrong, revise Task Work (and the pack version when
   milestone-accepted content changes) before continuing; do not silently
   invent a parallel design only in chat.

## Relationship To Other Contracts

| Concern                                           | Owner                                          |
| ------------------------------------------------- | ---------------------------------------------- |
| Minimal implementable Plan package                | **this file**                                  |
| Milestone Plan closeout + copy locale surface     | `milestone-plan-acceptance-pack.md`            |
| File/function size forecast and notice            | `software-structural-budget.md`                |
| DB/JSON/constants artifacts when schema changes   | `task-authoring-quality-contract.md`           |
| Prototype visual confirmation                     | UI Change Prototype Mandate / quality contract |
| Discussion adjustments writeback                  | `discussion-writeback-contract.md`             |
| Discussion change impact fan-out                  | `change-impact-fanout.md`                      |
| Prototype → product-truth writeback               | `prototype-product-truth-writeback.md`         |
| Prototype → Task/Project Work coverage + Plan SoT | `prototype-doc-coverage.md`                    |
| Integration test count / manual-run policy        | Task Integration Test Policy in workflow docs  |

## Milestone Closeout And Implement

When **all** in-scope tasks for a milestone finish Plan Design Gate drafting,
emit and (interactive) accept one
`milestone-plan-acceptance-pack` Markdown before treating milestone Planning as
closed. Per-task `plan_design_gate_status: passed` alone is not enough.

After acceptance, Execution and Delivery for that milestone **Must** use the
pack as described in `milestone-plan-acceptance-pack.md` (Implementation And
Delivery Reference).
