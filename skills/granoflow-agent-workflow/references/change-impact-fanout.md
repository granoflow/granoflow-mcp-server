# Change Impact Fan-out

Apply whenever the user **accepts, confirms, or locks** a material adjustment
during discussion — the same trigger set as `discussion-writeback-contract`.
Writeback alone is not enough: one decision may stale sibling tasks,
milestones, project docs, notes, or cards. This contract forces an explicit
**Change Impact Ledger** before the decision batch may close.

**Owner:** process completeness of cross-entity updates (not semantic
omniscience). Mechanical scan + mandatory disposition of every hit; fail closed
when the ledger is open or falsely empty.

MCP stays thin: scan with App list/read tools + repo docs; write through
existing App tools. Do not invent a second store. A future App-owned
`change_impact_preview` tool may replace host-side scanning; the ledger and
fail codes stay the gate.

## Mandatory Load (fail closed if skipped)

Before writing App slots for a material discussion decision, the host **Must**
load this reference via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "change-impact-fanout"
)
```

Skipping fails closed as `change_impact_unread`.
Seeing `discussion-writeback-contract` or SKILL prose alone does **not** count.

Also load `discussion-writeback-contract` for authoritative slot writeback.
When any prototype is updated in the batch, also load
`prototype-product-truth-writeback`.

## Hard Rule

For each material discussion decision:

1. **Load** this reference (and writeback).
2. **Scan** required scopes with decision summary + search terms (user
   wording + domain keywords). Record non-empty `scan_terms` unless the
   decision is explicitly local and `none` is proven after a documented empty
   scan.
3. **Disposition every candidate** (including zero hits):
   - `updated` — App/repo artifact changed + SHA/id readback where App-owned;
   - `not_applicable` — hit is unrelated; one auditable reason required;
   - `deferred` — only with **explicit user consent**, `owner`, and a blocking
     residual code.
4. **Close the ledger** (`status: closed`) only when every candidate has a
   disposition and every `updated` row has evidence.
5. **Then** complete writeback + readback and close the discussion batch.

Declaring `none` while the scan returned hits that were not dispositioned
fails closed as `change_impact_false_none`.

Leaving any candidate undispositioned fails closed as
`change_impact_open_targets`.

Omitting required scopes from `scopes_checked` fails closed as
`change_impact_ledger_incomplete`.

`deferred` without user consent / owner fails closed as
`change_impact_deferred_unapproved`.

`updated` without SHA/id (when App-owned) or path evidence fails closed as
`change_impact_updated_missing_evidence`.

## Required Scan Scopes

Every ledger Must list these in `scopes_checked` (may record empty hits):

| Scope                  | What to search                                                                                                                         |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `product_docs`         | Authoritative product / user-story docs in the repo (when present)                                                                     |
| `project_work`         | Project Work + project context attachments                                                                                             |
| `milestone_work`       | Active and related Milestone Work                                                                                                      |
| `tasks`                | Task titles, descriptions, and Task Work across the **project** (prefer current milestone first; do not default-skip other milestones) |
| `prototypes`           | Current / draft UI prototypes tied to hit tasks                                                                                        |
| `notes_cards`          | Notes / review cards that mention the changed surface (use review-card similarity / shared-note impact when available)                 |
| `experience_knowledge` | Experience / knowledge usages linked to hit tasks when present                                                                         |

Honest empty results are allowed; skipping a scope is not.

## Change Impact Ledger (minimum evidence)

Record in Task Work / Project Work / Milestone Work (as applicable):

```yaml
change_impact:
  - at: null # ISO time
    decision_summary: null
    decision_class: null # product_truth_changing | craft_only; required when any prototype updated
    product_truth_writeback_loaded: false # must be true when prototypes updated
    contract_loaded: false # must be true
    scan_terms: [] # non-empty unless empty-scan none is documented
    scopes_checked: [] # must include all required scopes above
    candidates:
      - entity_type: product_doc | user_story | project_work | milestone_work | task | task_work | prototype | note | card | experience | other
        entity_id: null # App id when applicable
        path_or_title: null
        hit_summary: null
        disposition: updated | not_applicable | deferred
        reason: null # required for not_applicable / deferred
        evidence:
          content_sha256: null
          package_sha256: null
          prototype_id: null
          version_id: null
          owner: null # required when deferred
        status: pending | done
    status: open | closed | failed
```

`status: open` or `failed` blocks Plan confirm, Readiness `passed`, and
Execution — same moments as writeback. Omit the ledger only when **no**
material discussion change occurred.

Run
`skills/granoflow-agent-workflow/scripts/lint_change_impact_fanout.py`
on the ledger YAML (or a Work Document excerpt). Require `ok: true` before
closing the batch.

## Timing

| Moment                                                 | Requirement                                              |
| ------------------------------------------------------ | -------------------------------------------------------- |
| User accepts a material change                         | Fan-out ledger closed **in the same batch** as writeback |
| Before Analysis / Plan confirm / Readiness / Execution | Ledger `closed` + writeback `written_and_read_back`      |
| Unattended (explicit only)                             | Same; `interaction_budget: 0` never skips fan-out        |

## Relationship To Existing Gates

- **Requires** `discussion-writeback-contract`: fan-out finds _what else_;
  writeback updates authoritative slots for each `updated` target.
- **Requires** `prototype-product-truth-writeback` when any `prototype`
  candidate is `updated`: set `decision_class` (default
  `product_truth_changing` when unsure) and satisfy product-doc / Task Work /
  user-story disposition rules. Lint encodes those fails.
- Complements review-card **shared-note impact** and experience
  **delete/unlink impact**: reuse those previews when the change touches
  notes/cards/experience; still record dispositions in this ledger.
- A platform version, support status, layout-family, orientation, or desktop
  window-constraint change must fan out to the Design Baseline, Milestone
  review, affected Task Prototype Bundles, Widget Promotion inputs, rendered
  fidelity evidence, and Acceptance Packs. Their prior digests are stale until
  regenerated and read back.
- A presentation-only color, spacing, typography, or layout adjustment reopens
  the Prototype Bundle and visual evidence, but not product behavior.
- A field, action, state, navigation, permission, or data-source change reopens
  the Screen Content Contract, requirement traceability, Contract Grill,
  Bundle, semantic review, Analysis Technical Package, Planning, and dependent
  acceptance artifacts.
- A domain relationship, core workflow, or data-disposition change also
  reopens the Analysis Logic Draft. Accepted prototype feedback must update the
  earliest affected contract before HTML regeneration.
- A presentation-only HTML change keeps the Content Contract but invalidates
  prior semantic DOM/screenshot evidence and must be recaptured.
- Does **not** claim semantic completeness. It claims: no silent skip of
  scanned hits; no phase advance on an open ledger.
- Fail codes here are in addition to `discussion_writeback_pending`,
  `temp_only_artifact_forbidden`, and `stale_reference_after_discussion`.

## Fail-closed codes

| Code                                        | When                                                                 |
| ------------------------------------------- | -------------------------------------------------------------------- |
| `change_impact_unread`                      | Reference not loaded via MCP                                         |
| `change_impact_ledger_incomplete`           | Missing fields, empty `scopes_checked`, or missing required scopes   |
| `change_impact_open_targets`                | Any candidate still `pending` / undispositioned, or ledger `open`    |
| `change_impact_false_none`                  | Claimed no impact while undispositioned scan hits remain             |
| `change_impact_deferred_unapproved`         | `deferred` without explicit user consent + owner                     |
| `change_impact_updated_missing_evidence`    | `updated` without path/SHA/id evidence                               |
| `prototype_product_truth_class_required`    | Prototype `updated` but `decision_class` missing                     |
| `prototype_product_truth_writeback_unread`  | Prototypes updated / product-truth class without contract load flag  |
| `prototype_product_doc_writeback_required`  | `product_truth_changing` without `product_doc` + `task_work` updated |
| `prototype_user_story_disposition_required` | `product_truth_changing` without a dispositioned `user_story`        |
| `change_impact_lint_failed`                 | `lint_change_impact_fanout.py` ≠ ok                                  |

## Agent Checklist (same batch as writeback)

1. Load `change-impact-fanout` via MCP?
2. If prototypes changed: load `prototype-product-truth-writeback` and set
   `decision_class`?
3. Required scopes scanned with recorded `scan_terms`?
4. Every candidate dispositioned (`updated` / `not_applicable` / `deferred`)?
5. Every `updated` has writeback + readback evidence?
6. Lint script `ok: true` and ledger `status: closed`?
7. If any check fails → do not close the discussion batch / phase gate.
