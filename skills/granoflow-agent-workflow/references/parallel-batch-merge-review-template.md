# Parallel Batch Merge Review Template

Copy to `temp/parallel-batch-<batch_id>-review-v<n>.md`. Delete guidance
comments. See `parallel-batch-merge-review.md`.

```yaml
---
doc_type: parallel_batch_merge_review
schema: granoflow_parallel_batch_merge_review_v1
batch_id: batch-1
milestone_id: ""
project_id: ""
version: 1
status: draft # draft | pending_acceptance | accepted | rejected | superseded
interaction_mode: interactive # interactive | unattended
host_isolation: same_tree_disjoint # same_tree_disjoint | worktree | serialized
workers:
  - task_id: ""
    write_surfaces: []
    delivery_ref: ""
    exit_ok: false
    diff_ref: null
pairwise_recheck: pending # pending | parallel_safe | conflict
post_merge_gates: [] # [{ id, command_or_gate, status: pending|passed|failed|skipped }]
decision_authority: null # null | user_explicit | unattended_grant
accepted_at: ""
html_render:
  status: skipped_markdown_only # ready | tools_missing | error | skipped_markdown_only
  html_path: null
  html_file_url: null
  markdown_path: ""
  markdown_file_url: ""
  link_emitted: false
  tool_probe:
    pandoc: false
    mmdc: false
    diagram_lua: false
    plantuml: false
  note: ""
---
```

# Parallel Batch Review — `<batch_id>`

## Summary

- Milestone / project:
- Host isolation:
- Pairwise recheck:

## Workers

| task_id | write_surfaces | delivery_ref | exit_ok | notes |
| ------- | -------------- | ------------ | ------- | ----- |
|         |                |              |         |       |

## Pairwise recheck

- Result: `pending` | `parallel_safe` | `conflict`
- Evidence:

## Post-merge gates

| id  | gate | status |
| --- | ---- | ------ |
|     |      |        |

## Decision

- Interactive accept / revise / reject, or unattended auto-adopt basis:
