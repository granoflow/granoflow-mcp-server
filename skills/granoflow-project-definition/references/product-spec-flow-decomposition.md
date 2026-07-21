# Product Spec Flow Decomposition

Apply during Project Definition Step 1 when building
`product_spec_coverage`, and again when Baseline screen mapping would freeze a
single-screen journey. This contract prevents thin docs from shipping
underspecified task flows.

**Owner:** user **operation flow** shape (serial gates vs parallel ops) — **not**
risk labels and not a vague “complexity” score. Platform-coupled /
hard-to-deliver surfaces still use the separate high-risk feasibility Tech Note
in `project-artifact-workflows.md`. Do not use “high risk” as the reason to
force extra screens.

## Mandatory Pass: Draw The Operation Flowchart First

For **every** adopted primary journey in
`product_spec_coverage.journey_coverage`:

1. **Draw an operation flowchart** of user actions, system waits, and decision
   points (even when product docs name only one screen). Record it under
   `decomposition.operation_flow`.
2. **Classify gates:** mark each mid-flow stop that must finish before the next
   user job makes sense as a **serial gate**. Ops the user can complete on one
   surface before a single final confirm are **parallel** (not serial).
3. **Conclude page count** from the flowchart — never skip the pass:

| Flowchart shape | `conclusion` |
| --------------- | ------------ |
| Exactly **one** user operation, and no mid-flow serial gate (same-page empty / loading / error states allowed) | `keep_cohesive` (one page) |
| **Multiple** operations that can run **concurrently / same screen**, with only a **final confirm** | `keep_cohesive` (one page) |
| Operations that must run **step-by-step** (serial gates: confirm → wait → review, compare-then-commit, wizard steps, etc.) | `split` (multi-page; one primary job or wait phase per page) |
| Flowchart incomplete or page-count judgment is decision-changing | `needs_user_decision` |

| `conclusion` | Meaning |
| ------------ | ------- |
| `split` | Adopt the multi-page screen set (write into `screen_ids` + `screen_coverage`) |
| `keep_cohesive` | Keep one page (or the pre-pass cohesive set); document the rejected multi-page split |
| `needs_user_decision` | Interactive waits; unattended fails closed |

Fail closed:

- `flow_decomposition_pass_missing` — no pass recorded for an adopted journey
- `flow_decomposition_operation_flow_missing` — no `operation_flow` with at
  least one `user_operations` entry (or equivalent non-empty summary + ops)
- `flow_decomposition_conclusion_missing` — pass exists but no conclusion
- `flow_decomposition_split_without_screens` — `split` but
  `concluded_screen_ids` has fewer than two screens
- `flow_decomposition_split_without_serial_gate` — `split` but `serial_gates`
  is empty
- `flow_decomposition_keep_with_serial_gates` — `keep_cohesive` but
  `serial_gates` is non-empty (inconsistent with one-page rule)
- `flow_decomposition_keep_without_rejected_split` — `keep_cohesive` without a
  non-empty `rejected_split_summary`

## Serial Gate Vs Same-Page State

**Serial gate (forces multi-page when present):** the next user job is
meaningless until the previous phase completes or is explicitly confirmed —
for example confirm-before-execute, long wait before result, compare-before-
commit, wizard step N after step N−1.

**Same-page state (does not force multi-page):** empty / loading / inline error
for the **same** user operation. Prefer states on one page unless a wait or
decision is a distinct phase the user must inhabit.

Long-running work: even when the product names “one import,”
confirm → progress wait → result review are serial gates → `split`.

Risk / platform difficulty never appears in this judgment.

## Stress Path (acceptance observability)

After the conclusion, every adopted `acceptance_id` linked from the journey
must have a `stress_path` that a beginner can walk:

1. `entry` — how the user starts
2. `intermediate` — zero or more steps (required when conclusion is `split`
   and the acceptance spans serial phases)
3. `success_exit` — observable success
4. `failure_exit` — at least one observable failure / empty / reject path when
   the acceptance implies negative cases

Missing stress path → `journey_stress_path_incomplete` (also blocks
`product_spec_coverage.status: ready`).

## Thin Product Docs + Unattended

Thin docs do **not** waive the operation-flow pass.

| Mode | Behavior |
| ---- | -------- |
| Interactive | Show flowchart + serial-gate reading + recommendation; wait for accept / adjust / keep |
| Unattended (explicit only) | Must still draw the flow, list gates, and record conclusion. May adopt a **non-decision-changing** `split` or `keep_cohesive` with `agent_recommendation_adopted`. Must **not** invent whole journeys as `user_stated`. Decision-changing thin-doc gap fills → `needs_user_decision` / fail closed `thin_product_doc_gap_requires_user` — never silent auto-complete of an underspecified product |

Unattended Baseline visual `auto_accept_recommendation` never skips this gate.

## Project Work Fields

See `product_spec_coverage` in `project-work-document-template.md`:

- `journey_coverage[].decomposition.operation_flow`
- `journey_coverage[].decomposition.serial_gates`
- `journey_coverage[].decomposition.parallel_ops_ok`
- `journey_coverage[].decomposition` conclusion + screen summaries
- `journey_coverage[].stress_paths[]` (per acceptance)
- checklist flags for pass + conclusion + stress paths

Lint: `skills/granoflow-project-definition/scripts/lint_product_spec_coverage.py`.

## Relationship To Task Prototypes

When conclusion is `split`, later task prototypes Must cover the concluded
screens’ authorized deltas (per-page expressions inside the locked Design
System). Collapsing a concluded multi-step flow back into one prototype frame
without revising Project Work fails closed as `prototype_product_truth_violation`.
