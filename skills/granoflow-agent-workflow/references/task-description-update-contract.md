# Task Description Update Contract

## When To Read

Read this reference before an AI or MCP client changes any field on an existing
task. Task creation remains owned by `task-authoring-quality-contract`.
Ordinary App UI edits are outside this MCP-only contract.

## Principle

Every attempted task mutation triggers a Description Impact Check. A check is
not an automatic rewrite:

- operational changes usually preserve the description;
- semantic changes update the description in the same reviewed write;
- completed task prose is frozen except through a post-completion revision;
- Completion Summary updates may replace only their managed block.

The description remains the current 30-second recall summary. Task Work,
Delivery, revisions, and change-impact ledgers preserve detailed history.

## Transient Review

Supply `descriptionImpactReview` to every update path:

```yaml
reviewedTaskUpdatedAt: ""
reviewedDescriptionSha256: ""
decision: unchanged | rewrite
reasonCode: operational_only | review_only | completion_only | completion_summary_only | historical_time_only | node_completion_only | placement_reviewed_no_semantic_change | title_clarification_no_semantic_change | semantic_change | description_correction | post_completion_revision
rationale: ""
fiveDimensionsReviewed: false
authoringEvidence: null
writebackRefs: []
```

The MCP reads the current task, checks the revision and SHA, computes actual
changed fields, validates the decision, removes this transient object, writes,
and reads back. It never persists review metadata in the App task schema.

## Decisions

Use `unchanged` only when the task meaning remains true:

| Change                                      | Reason                                   |
| ------------------------------------------- | ---------------------------------------- |
| due, reminder, status, or tags              | `operational_only`                       |
| Task Review body                            | `review_only`                            |
| ordinary completion and timing              | `completion_only`                        |
| Completion Summary managed block            | `completion_summary_only`                |
| historical timestamps or soft delete        | `historical_time_only`                   |
| node completion side effect                 | `node_completion_only`                   |
| project/milestone move with unchanged scope | `placement_reviewed_no_semantic_change`  |
| wording-only title clarification            | `title_clarification_no_semantic_change` |

Title clarification still requires current authoring evidence and
`fiveDimensionsReviewed: true`, proving the existing description remains
compatible with the new title. Unknown generic fields cannot use an unchanged
escape hatch.

Use `rewrite` for:

- product outcome, scope, acceptance, requirement, permission, behavior, or
  other semantic change;
- direct description correction;
- an evidence-backed post-completion revision.

A rewrite supplies the complete next description, current authoring evidence,
and `fiveDimensionsReviewed: true`. `semantic_change` and
`post_completion_revision` also require durable `writebackRefs`.

## Mutation Paths

The shared guard applies to generic and structured task updates, Task Review,
Completion Summary, historical update/soft-delete, node-less completion,
`granoflow_task_finish`, and final-node completion checks. Task creation keeps
its existing creation quality gate.

Node and completion paths do not convert the original description into an
activity log. Actual results belong in Delivery and Completion Summary.

## Completion Summary Safety

The caller supplies the complete description containing one valid managed
block. The MCP removes the managed block from both the current and proposed
text and requires the remaining text to be byte-for-byte identical. This
allows append or replacement of the managed block without rewriting user text.

## Failure And Recovery

- Missing review: re-read the task and prepare the review.
- Revision/SHA mismatch: discard the stale preview and recompute.
- Rewrite required: update contracts and Task Work first when semantic truth
  changed, then submit fields and description together.
- Quality failure: revise the complete description; do not patch around the
  five-dimension, analogy, example, or plain-language checks.
- Readback mismatch: report failure and re-read; never claim the update landed.

Fail closed with:

- `task_description_impact_review_required`
- `task_description_review_digest_mismatch`
- `task_description_rewrite_required`
- `task_description_quality_failed`
- `task_description_readback_mismatch`
- `task_description_post_completion_overwrite_forbidden`
