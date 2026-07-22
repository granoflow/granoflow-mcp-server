# Discussion Writeback Contract

Apply whenever the user **accepts, confirms, or locks** a material adjustment
during discussion — including but not limited to UI prototypes, page splits,
copy, Outcome/Scope, acceptance mapping, screen/journey coverage, or Plan
steps. Chat text and local `temp/` previews are **not** authoritative for later
Plan or Execution.

**Owner:** keep App-owned artifacts current so Plan / Readiness / Execution
always resolve the same truth the user just approved.

MCP stays thin: write through existing App tools (`logical_attachment_replace`,
`task_prototype_import`, `task_attachment_*`, Project Work confirm, etc.). Do
not invent a second store.

## Hard Rule

After a material discussion decision is accepted:

1. **Load and close Change Impact Fan-out** (`change-impact-fanout`): scan
   required scopes, disposition every hit, lint the ledger to `closed`. Skip
   fails closed as `change_impact_unread` / `change_impact_open_targets` (and
   related codes in that reference).
2. **Identify the authoritative slot** (table below) for each `updated` target.
3. **Write the new bytes** into that slot (new package / replace content).
4. **Update every durable reference** that points at the old truth (Task Work
   `ui_prototype_confirmed`, Project Work `screen_ids`, Plan steps, etc.).
5. **Read back** App SHA / prototype ids; record them in the Work Document and
   in the fan-out ledger evidence fields.
6. **Only then** close the discussion batch, mark Analysis/Plan confirmed, pass
   Readiness, or start Execution.

Leaving the change only in chat, a gallery HTML under `temp/`, or an unlinked
preview fails closed as `discussion_writeback_pending`.

Treating a local-only preview as admission evidence fails closed as
`temp_only_artifact_forbidden`.

If Plan/Readiness/Execution refs still name a superseded package or hash while
a newer App `current` exists, fail closed as
`stale_reference_after_discussion`.

Updating one task/slot while leaving scanned sibling tasks, milestones, project
docs, notes, or cards undispositioned fails closed under
`change-impact-fanout` (not as a soft reminder).

## Authoritative Slot Map

| Adjustment kind                                                                   | Write back to                                                                                                                                | Must also update                                                                                                              |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Task UI prototype (option pick, page split, craft fix, copy-in-frame)             | Task `ui_prototype` (+ `granoflow_task_prototype_import` when packaged) with `visualConfirmed=true` when the user confirmed visuals          | Task Work `ui_prototype_confirmed` (prototypeId, versionId, packageSha256, pages/option_id); supersede old ids explicitly     |
| Prototype **product-truth** correction (chrome, toggles, labels, flows, behavior) | Same `ui_prototype` **plus** authoritative repo `product_doc` + Task Work `locked_product_contracts` per `prototype-product-truth-writeback` | Disposition `user_story` every time; update US when journeys/entries change; fan-out `decision_class: product_truth_changing` |
| Prototype **craft-only** rematch (same product truth)                             | Task `ui_prototype` + Task Work prototype refs                                                                                               | `product_doc`/`user_story` may be `not_applicable` only with section-cite reason (`decision_class: craft_only`)               |
| Project Design Baseline / Spec / Shell                                            | Project design-baseline / Spec / Shell App packages + registry                                                                               | Project Work design fields + SHA readback                                                                                     |
| Product journeys / screens / decomposition / stress paths                         | Project Work `product_spec_coverage` (and related product fields)                                                                            | Attachment replace + confirm when automation requires ready status                                                            |
| Analysis / Plan / Readiness fields                                                | Task Work `task_work_execution` (replace active slot)                                                                                        | Hash readback; bump `work_version` when material                                                                              |
| Milestone portfolio / handoffs                                                    | Milestone Work                                                                                                                               | Hash readback                                                                                                                 |
| Delivery / completion evidence                                                    | Task Delivery slot                                                                                                                           | Hash readback                                                                                                                 |
| Data contracts / constants / widgets                                              | Named project attachments                                                                                                                    | Registry SHA; else later `data_artifact_stale` / `widget_catalog_stale`                                                       |

When multiple slots are affected by one decision, write **all** of them in the
same batch before claiming the decision is done. Discover those slots via
`change-impact-fanout` first; do not invent a private subset.

## Timing

| Moment                                        | Requirement                                                                        |
| --------------------------------------------- | ---------------------------------------------------------------------------------- |
| User accepts a material change mid-discussion | Writeback before the next phase gate or before ending the turn’s decision batch    |
| Before Analysis confirmation                  | Confirmed prototypes/product truths already on App if UI/product changed           |
| Before Plan confirmation / Readiness `passed` | Task Work + `ui_prototype` (if UI) match App readback                              |
| Before Execution (non-dry-run)                | Same; export/`executionAdmission` must not see stale refs                          |
| Unattended (explicit only)                    | Same writebacks with notices; never skip App write because interaction_budget is 0 |

Interactive: user confirmation of the **content** authorizes the writeback of
that content. Do not wait for a second “may I upload?” when the user already
accepted the artifact. Unattended: adopt + writeback under the declaration.

This does **not** authorize code execution, commit, push, publish, or deploy.

## Minimum Evidence In Task / Project Work

Record after each writeback (as applicable):

```yaml
discussion_writeback:
  - at: null # ISO time
    decision_summary: null
    slots_updated: [] # e.g. [ui_prototype, task_work_execution]
    prototype_id: null
    version_id: null
    package_sha256: null
    content_sha256: null
    superseded: [] # prior ids/hashes explicitly retired
    change_impact_status: closed | open | failed # must match change_impact ledger
    status: written_and_read_back | pending | failed

change_impact: [] # see change-impact-fanout.md; required whenever writeback runs
```

`discussion_writeback.status: pending` or `failed`, or
`change_impact.status: open` / `failed`, blocks Plan confirm, Readiness
`passed`, and Execution. Omit both ledgers only when no material discussion
change occurred.

## Relationship To Existing Gates

- Strengthens **UI Change Prototype Mandate**: a later discussion change to a
  once-confirmed prototype Must import a **new** current package and rewrite
  Task Work refs — not leave chat/temp ahead of App.
- **Requires** `change-impact-fanout` in the same batch: writeback is the slot
  write; fan-out is the cross-entity completeness gate.
- **Requires** `prototype-product-truth-writeback` whenever any `ui_prototype`
  is updated in the batch: product-truth corrections Must update product docs
  - Task Work locked contracts (fail closed
    `prototype_product_doc_writeback_required`); craft-only Must be explicit.
- Complements Grill clean-rewrite: local rewrite is not enough until App
  replace + readback succeed.
- Complements `product_spec_coverage` / flow-decomposition: journey/page-count
  conclusions accepted in chat Must land in Project Work before Done /
  automation.
- Fail codes here are in addition to `ui_prototype_required`,
  `attachment_readback_pending`, `post_grill_rewrite_required`, and
  `change_impact_*`.

## Agent Checklist (before Plan / Readiness / Execution)

1. List material discussion decisions since the last App writeback.
2. For each: `change-impact-fanout` loaded, ledger linted `closed`?
3. For each: authoritative slot updated? SHA/ids read back?
4. Task Work / Project Work refs == App current (no superseded “still pointed”)?
5. No `temp/`-only artifact cited as the execution prototype?
6. If any check fails → `discussion_writeback_pending`,
   `stale_reference_after_discussion`, or `change_impact_*`; do not proceed.
