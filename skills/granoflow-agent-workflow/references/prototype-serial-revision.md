# Prototype Serial Revision (Task / Milestone UI)

Apply this contract whenever the host authors a **post-Baseline task or
milestone** `ui_prototype`. It replaces the former default dual page-expression
batch (`expr_a` / `expr_b` 2-pick) with a **serial multi-draft** line: plan →
review → draft → review → revise until blocking findings clear or the draft
cap is hit.

Project Definition **Design Spec** and **App Shell** triads do **not** use this
contract (they keep their own promote counts).

## Mandatory Load (fail closed if skipped)

Before authoring the first task/milestone HTML draft after the Content Contract
is ready, load:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-serial-revision"
)
```

Skipping fails closed as `prototype_serial_revision_unread`.
Seeing Craft Gate prose alone does **not** count.

Also load, per their own gates: `prototype-baseline-fit`,
`user-visible-copy-boundary`, `prototype-expression-brainstorm` (promote **one**
serial thesis), `task-ui-skill-pipeline`, `ui-component-effect-matrix`,
`stack-realization-notes`, and Analysis finalization contracts
(Logic Draft / Screen Content Contract).

## Authority Split (hard)

| Artifact                                 | Role                                                               |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `temp/` brief                            | Thin review input only (goals, delta, constraints, open questions) |
| Logic Draft + Screen Content Contract    | Formal product/behavior authority before HTML                      |
| `granoflow_prototype_revision_ledger_v1` | Draft history, stop reason, selection surface, recommendation      |

Do **not** treat the temp brief as a third Source of Truth. Accepted brief
decisions Must land in the Logic Draft / Content Contract before HTML, or via
`discussion-writeback-contract` after a rematch.

## Pipeline (both interactive and unattended)

```text
temp brief → update Logic Draft / Content Contract
  → effect matrix green + stack realization notes
  → pre-draft review (gstack subset + grill self-QA) when applicable
  → skill pipeline authors draft N (N starts at 1)
  → post-draft HTML review (gstack/design/skills + lint gates)
  → if blocking and N < 5 → draft N+1
  → else stop (zero_blocking | max_drafts)
  → interactive: selection surface / unattended: adopt final green
```

### Pre-draft review

1. Write a thin brief under `temp/` (or host-equivalent scratch) for reviewers.
2. **Stack deliverable gate (hard before draft 1):** build and lint
   `ui_component_effect_matrix_v1` to green. Author
   `granoflow_stack_realization_notes_v1` covering every **selected** matrix
   role (see `stack-realization-notes`). HTML Must stay inside that deliverable
   surface—no default Web-only showcase; schematic regions use `【增强实现】`
   aligned to `enhancement_schematic` notes. Fail closed
   `ui_component_effect_matrix_*` /
   `stack_realization_notes_*` /
   `prototype_revision_stack_gates_incomplete`.
3. Run applicable **report-only** reviewers (prefer gstack `/plan-ceo-review`,
   `/plan-design-review`, `prd-review`, and other MCP-preferred methods when
   their conditions apply). Every invocation Must use
   `mutation_policy: review_only` and `mutation_authorization: none`.
4. Run **grill self-QA** (AI asks and answers). Interactive may surface open
   product questions to the user via Contract Grill; unattended Must use
   `answer_source: unattended_grant` and Must **not** interview the user
   (`grill-me` user-interview mode is forbidden on the silent path).
5. Clear pre-draft **blocking** findings (or record explicit deferral that is
   not a functional stub) before authoring HTML.

### Draft authoring

Use `task-ui-skill-pipeline` capabilities (`high_fidelity_html_authoring`,
etc.). Each draft Must pass Craft Gate prerequisites for that round
(Baseline fit, chrome lock when applicable, copy boundary, skill pipeline,
component-effect matrix, stack realization notes). Persist HTML paths, package
SHA, `component_effect_matrix_sha256`, and `stack_realization_notes_sha256` on
the ledger. Missing either SHA on a draft that reaches
`ready_for_selection` / `accepted` fails closed
`prototype_revision_stack_gates_incomplete`.

### Post-draft review

1. Run applicable HTML reviewers (`final_design_review`, `visual_quality_audit`,
   gstack design/CEO/requirement reviewers when conditions apply) under
   review-only mutation policy.
2. Run deterministic lints (baseline fit, user copy, contract↔prototype
   semantics, link ledger entries, etc.).
3. Classify findings:
   - **blocking** — wrong/missing capability, contract mismatch, craft fail,
     Baseline/Shell break, unmarked interactive controls, product-truth
     violation, effect-matrix / stack-realization gaps, stack-undeliverable
     showcase without notes disposition;
   - **advisory** — taste nits, optional polish.
4. If `blocking_out > 0` and `ordinal < 5`, author the next draft addressing
   only those blocking items (plus any Content Contract updates required by
   writeback).
5. If `blocking_out == 0`, stop immediately (`stop_reason: zero_blocking`).
   Do **not** pad drafts to five.

### Caps (hard)

| Rule                       | Value                                                      |
| -------------------------- | ---------------------------------------------------------- |
| Max drafts                 | **5**                                                      |
| Early stop                 | First round with **0 blocking**                            |
| Drafts 4–5                 | Allowed **only** when previous draft `blocking_out > 0`    |
| Advisory-only              | Must **not** open draft 4 or 5                             |
| Cap with residual blocking | `stop_reason: max_drafts` and **refuse** `visualConfirmed` |

Fail closed:

- `prototype_serial_revision_unread`
- `prototype_revision_ledger_required`
- `prototype_revision_max_drafts`
- `prototype_revision_late_draft_without_blocking`
- `prototype_revision_blocking_residual`
- `prototype_revision_selection_invalid`
- `prototype_revision_stack_gates_incomplete`
- `prototype_revision_lint_failed`

## Selection Surface

### Interactive

- Present the **last** `min(n, 3)` drafts as clickable absolute `file://` links
  (and a history gallery when `n ≥ 2`). Older drafts stay on the ledger for
  audit but are not on the default pick surface.
- Mark **recommended** = last draft with `blocking_out == 0`, or the latest
  draft when stopping at max with zero blocking. Never recommend a draft that
  still has blocking findings.
- When `n == 1`:
  - `selection_mode: confirm_or_revise`
  - Do **not** force a multi-option pick
  - User may confirm the single draft, or give detail revision notes (those
    notes open draft 2+ inside the same 5-cap)
- When `n ≥ 2`:
  - `selection_mode: pick_among` over the last ≤3 ordinals
  - Still allow “revise recommended” detail notes (counts as a new draft if
    under cap)

### Unattended (explicit only)

- No pick surface (`selection_mode: auto_adopt`).
- Adopt the last draft with `blocking_out == 0`.
- If the run hits max drafts with residual blocking → fail closed
  `prototype_revision_blocking_residual` (never silent `visualConfirmed`).

## Ledger Schema

Persist on Task Work (or an attachment referenced by exact SHA):

```yaml
prototype_revision_ledger:
  schema: granoflow_prototype_revision_ledger_v1
  contract_loaded: true
  mode: interactive # interactive | unattended
  status: in_progress | ready_for_selection | accepted | blocked
  drafts:
    - ordinal: 1
      html_paths: [] # absolute or package-relative paths
      package_sha256: null # 64 hex when packaged
      component_effect_matrix_sha256: null # 64 hex; required at ready_for_selection|accepted
      stack_realization_notes_sha256: null # 64 hex; required at ready_for_selection|accepted
      pre_review:
        blocking_count: 0
        advisory_count: 0
        evidence_refs: []
      post_review:
        blocking_count: 0
        advisory_count: 0
        evidence_refs: []
      blocking_in: 0 # blocking findings that justified authoring this draft (0 for draft 1)
      blocking_out: 0 # blocking remaining after post-review
  stop_reason: null # zero_blocking | max_drafts | null while in_progress
  selection_surface:
    draft_ordinals: [1] # last min(n, 3)
    selection_mode: confirm_or_revise # confirm_or_revise | pick_among | auto_adopt
    recommended_ordinal: 1
  accepted_ordinal: null
  accepted_package_sha256: null
```

## Lint

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_revision_ledger.py \
  path/to/task-work.yaml
```

Require `ok: true` before `visualConfirmed=true` on UI-changing tasks.
Also keep `lint_prototype_link_ledger.py --require-complete` and Plan-entry
prototype acceptance gates.

## Admission Test (host self-check)

1. Loaded this reference via MCP before first task HTML draft?
2. Temp brief decisions written into Logic Draft / Content Contract?
3. Pre/post reviews review-only (no mutating gstack design-review commits)?
4. Unattended grill is self-QA only?
5. Drafts ≤5; drafts 4–5 only after prior blocking; early stop on zero blocking?
6. Interactive surface = last ≤3; single draft uses confirm_or_revise?
7. Unattended adopts final green only; residual blocking blocks confirm?
8. `lint_prototype_revision_ledger.py` green before visual confirm?
