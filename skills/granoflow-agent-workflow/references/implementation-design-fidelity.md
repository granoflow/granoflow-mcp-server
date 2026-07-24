# Implementation Design Fidelity (task-local AI self-check)

Hard gate for **single-task software Delivery**: after code is written and before
the task may be marked done, the Agent **Must** verify that implementation still
matches the **Plan-phase design authority**, and that code is split by function
(methods / classes / files). This is AI-owned self-acceptance—not a user Preview
Gate and not E2E Phase B.

Complements (does not replace):

- UI `prototype-implementation-fidelity` Phase A (visual/chrome HTML)
- `milestone-plan-acceptance-pack` Delivery reconciliation
- `software-structural-budget` / Structural Forecast
- `data_artifact_stale` attachment sync

## Mandatory Load

Load before software Delivery / `acceptance_report` finalization when the task
edited code, tests, build files, schema, or workflows:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "implementation-design-fidelity"
)
```

Skipping the load when the gate applies fails closed as
`impl_design_fidelity_unread`.

## Design Authority (hard)

Compare against **Plan-confirmed** design only—not chat memory and not an
unconfirmed Analysis draft:

| Surface                             | Authority (in order)                                                                                                                                           |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Schema / tables / JSON / constants  | Task Work Plan + project `data_model` / `json_contracts` / `constants_catalog` as named in Project Work; milestone pack `data_structures` when `present: true` |
| Operation flows                     | Task Work Plan Operation flowchart; pack `flowcharts` when present                                                                                             |
| UML (state / sequence / class / ER) | Task Work Plan UML sections; pack `uml_diagrams` when present                                                                                                  |
| Modular split expectations          | Structural Change Forecast + Plan responsibility splits; pack notes when present                                                                               |

If a surface was `present: false` / `data_disposition: unchanged` with basis,
record `not_applicable` for that axis—do not invent a redesign to compare.

## When It Applies

| Case                                                        | Gate                                                                  |
| ----------------------------------------------------------- | --------------------------------------------------------------------- |
| Software task that edited code/tests/build/schema/workflows | **required**                                                          |
| Copy-only / no code edit                                    | `impl_design_fidelity.status: not_applicable`                         |
| UI chrome-only with no schema/flow/UML in Plan              | Design axes may be `not_applicable`; **modular_split** still required |

## Ledger (persist on Task Work + cite in Delivery / acceptance_report)

```yaml
impl_design_fidelity:
  schema: granoflow_impl_design_fidelity_v1
  contract_loaded: true
  status: not_applicable | pending | complete
  authority:
    plan_pack_path: <path-or-null>
    plan_pack_version: <n-or-null>
    task_work_plan_ref: <slot/hash>
  axes:
    data_structures:
      status: not_applicable | matched | diverged
      basis: <one line when not_applicable>
    flowcharts:
      status: not_applicable | matched | diverged
      basis: <one line when not_applicable>
    uml_diagrams:
      status: not_applicable | matched | diverged
      basis: <one line when not_applicable>
    modular_split:
      status: matched | needs_split | diverged_kept
      # matched = methods/classes/files follow function boundaries per Plan/forecast
      # needs_split = must revise code before Delivery
      # diverged_kept = kept a different split with better_rationale + design writeback
  declaration_emitted: true | false
  decision: matched_all | revise_to_design | keep_with_design_writeback | not_applicable
  better_rationale: <required when any axis diverged and decision keeps impl>
  diffs: [] # when any diverged: [{ axis, summary, design_ref, impl_ref }]
  design_writeback:
    status: not_applicable | pending | written_and_read_back
    slots_updated: [] # task_work_execution, milestone pack, data_model, …
    content_sha256: <when written>
```

Lint:

```bash
python3 skills/granoflow-agent-workflow/scripts/lint_implementation_design_fidelity.py \
  path/to/ledger.yaml
```

## Rules

1. Emit an explicit non-question declaration (interactive or unattended) with
   axis statuses, decision, and rationale before Delivery upload.
2. **`needs_split`** on `modular_split` → revise code (extract methods/classes/
   files by function) and re-check; do not Delivery while `needs_split`.
3. Any design axis `diverged`:
   - **`revise_to_design`**: change code to match Plan authority, re-check until
     `matched` (or justified `not_applicable`);
   - **`keep_with_design_writeback`** (allowed, including unattended): keep the
     implementation **only if** `better_rationale` explains why it is better for
     Outcome / maintainability / correctness **and** design documents are
     updated in the **same batch** (see Writeback).
4. Keeping a divergence **without** design writeback fails closed as
   `impl_design_writeback_missing`.
5. Keeping a divergence **without** `better_rationale` fails as
   `impl_design_better_rationale_missing`.
6. Do not treat form-factor / orientation-only UI differences here (owned by
   prototype Phase A carve-out).

## Writeback (required on keep)

When `decision: keep_with_design_writeback` (or any kept divergence):

1. Update **Task Work** Plan sections (Operation Flow, Domain/data disposition,
   UML notes, Structural Forecast notes) so they describe the shipped design.
2. Update the **milestone Plan acceptance pack** to a new `v<n+1>` when that
   pack’s `present: true` sections are affected; set prior pack `superseded`.
   Interactive: re-seek pack acceptance for material deltas. Unattended: emit
   pack revision notice + Plan Acceptance Link Digest entry; auto-adopt only
   under a valid unattended Planning/execution grant that covers design
   writeback.
3. Update project **`data_model` / `json_contracts` / `constants_catalog`** when
   schema/contracts changed; hash-read back (`data_artifact_stale` if skipped).
4. Apply `discussion-writeback-contract` + `change-impact-fanout` for sibling
   impact. Never leave the new design truth only in chat/`temp`.
5. Set `design_writeback.status: written_and_read_back` with slot list + hashes.

## Acceptance Report

The task `acceptance_report` HTML **Must** include a section summarizing
`impl_design_fidelity` (axis table, decision, better_rationale when any, writeback
paths/SHAs). Omitting it when the gate applies fails as
`impl_design_fidelity_report_missing`.

## Fail-Closed Codes

| Code                                   | When                                                         |
| -------------------------------------- | ------------------------------------------------------------ |
| `impl_design_fidelity_unread`          | Gate applies; reference not loaded / `contract_loaded` false |
| `impl_design_fidelity_incomplete`      | `status` not `complete`/`not_applicable` at Delivery         |
| `impl_design_fidelity_undeclared`      | `declaration_emitted` false                                  |
| `impl_design_axis_unresolved`          | Required axis still `pending` or missing                     |
| `impl_design_modular_split_unresolved` | `modular_split` is `needs_split` at Delivery                 |
| `impl_design_better_rationale_missing` | Kept divergence without better_rationale                     |
| `impl_design_writeback_missing`        | Kept divergence without design writeback readback            |
| `impl_design_fidelity_report_missing`  | acceptance_report omits the fidelity section                 |
| `impl_design_fidelity_lint_failed`     | Structural lint `ok: false`                                  |

## Must Not

- Compare only to Analysis drafts when a confirmed Plan / pack exists.
- Mark Delivery done with silent schema/flow/UML drift.
- Keep a “better” design in code while leaving Plan/pack/attachments stale.
- Use this gate to re-open product scope without Outcome/writeback.
