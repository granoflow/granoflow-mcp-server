# Parallel Batch Merge Review

Single owner for the **concurrent-batch delivery review artifact**: one Markdown
file that lists every worker’s write surfaces, Delivery pointers, and
pairwise recheck before a single-writer merge into the main working tree.

Per-task Delivery remains in each Task Work. This pack never replaces task
completion owners; it is the supervisor surface for batch merge acceptance.

Also load `parallel-task-execution` (Host Concurrency Policy) and
`markdown-html-acceptance-render` before closeout.

## Mandatory Load

Load via MCP before claiming any concurrent batch done, before multi-writer
merge into the main tree, and when refreshing a living batch review:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "parallel-batch-merge-review"
)
```

Use `references/parallel-batch-merge-review-template.md` when creating the file.
Skipping the load fails closed as `parallel_batch_merge_review_unread`.

## When It Applies

| Case                                                        | Rule                                                                       |
| ----------------------------------------------------------- | -------------------------------------------------------------------------- |
| A `parallel_safe` / `disjoint_write_batch` finishes workers | Create or refresh pack; lint; mode-branch accept before merge              |
| `read_only_fanout` only (no material writes)                | Pack optional; if omitted, record `not_applicable` basis in Milestone Work |
| Serialized single-worker execution                          | Pack not required                                                          |
| Unplanned overlap discovered mid-batch                      | Stop conflicting writes; pack `status: rejected` or supersede; replan      |

Missing pack before batch-done / merge → `parallel_batch_merge_review_required`.
Merge or batch-done while not `accepted` →
`parallel_batch_merge_review_unaccepted`.

## Pack File

### Location And Naming

```text
temp/parallel-batch-<batch_id>-review-v<n>.md
```

Examples: `temp/parallel-batch-batch-1-review-v1.md`. Bump `v<n>` on material
changes after a prior `accepted` pack (or when superseding a closed draft).

### Lifecycle

| `status`             | When                                                          |
| -------------------- | ------------------------------------------------------------- |
| `draft`              | Workers still running or supervisor assembling evidence       |
| `pending_acceptance` | All workers stopped; pairwise recheck done; ready for Preview |
| `accepted`           | Interactive accept or valid unattended grant                  |
| `rejected`           | User or supervisor rejected one/more workers or the batch     |
| `superseded`         | Replaced by `v<n+1>`                                          |

### Frontmatter (required)

```yaml
doc_type: parallel_batch_merge_review
schema: granoflow_parallel_batch_merge_review_v1
batch_id: batch-1
milestone_id: "" # UUID or key when known
project_id: ""
version: 1
status: draft # draft | pending_acceptance | accepted | rejected | superseded
interaction_mode: interactive # interactive | unattended
host_isolation: same_tree_disjoint # same_tree_disjoint | worktree | serialized
workers:
  - task_id: ""
    write_surfaces: [] # bounded paths / surfaces
    delivery_ref: "" # Task Delivery path or attachment id
    exit_ok: false # process exit alone is never completion
    diff_ref: null # optional patch / worktree pointer
pairwise_recheck: pending # pending | parallel_safe | conflict
post_merge_gates: [] # [{ id, command_or_gate, status }]
decision_authority: null # null | user_explicit | unattended_grant
accepted_at: ""
html_render:
  status: skipped_markdown_only
  html_path: null
  html_file_url: null
  markdown_path: ""
  markdown_file_url: ""
  link_emitted: false
```

Rules:

1. `workers` Must be a non-empty list for any pack that is not documenting a
   cancelled empty batch with explicit basis in the body.
2. `pairwise_recheck: conflict` blocks `accepted`.
3. `exit_ok: true` is evidence of process finish only; task completion still
   requires Delivery / node / timestamp readback per `parallel-task-execution`.
4. `host_isolation: serialized` packs are only valid when the run was forced
   serial after `host_isolation_unavailable` or an explicit serialize decision—
   do not use them to launder a same-tree `shared_write` parallel launch.

### Lint

```text
python3 skills/granoflow-agent-workflow/scripts/lint_parallel_batch_merge_review.py \
  path/to/pack.md --require-links
```

## Acceptance Interaction

Load `markdown-html-acceptance-render` and apply clickable-link rules.

| Mode          | Behavior                                                                                                                                                                                                                                                                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interactive` | Write Markdown → render HTML when tools allow → emit **Parallel Batch Review Link** with `file://` HTML (when ready) + Markdown → prefer host open → **wait** for accept / revise / reject.                                                                                                                                                       |
| `unattended`  | Same convert + links as non-blocking notice. Auto-adopt only when lint ok, `pairwise_recheck: parallel_safe`, every worker has Delivery readback evidence, and Host Concurrency Policy was obeyed. Record `decision_authority: unattended_grant`. On failure: park batch/workers in Residual / deferred list; continue other independent batches. |

Missing clickable Markdown `file://` when links required →
`parallel_batch_review_link_required`. HTML `status: ready` without HTML
`file://` → same code.

Never present unattended adoption as user acceptance.

## Merge And Post-Gates

Only after `status: accepted`:

1. **Single-writer merge** into the main working tree (supervisor only).
2. Run `post_merge_gates` serially on the main tree.
3. Update Milestone Work `parallel_execution.batches[].review_ref` and, when a
   Project E2E SoT is active, the coarse `parallel_batches[]` pointer.
4. Then—and only then—claim the batch complete.

## Hard-fail codes

| Code                                     | When                                              |
| ---------------------------------------- | ------------------------------------------------- |
| `parallel_batch_merge_review_unread`     | Reference not loaded                              |
| `parallel_batch_merge_review_required`   | Batch done / merge without pack                   |
| `parallel_batch_merge_review_unaccepted` | Merge / batch-done while not accepted             |
| `parallel_batch_merge_review_incomplete` | Lint: schema / workers / status / recheck invalid |
| `parallel_batch_review_link_required`    | Links required but not emitted / not file://      |

## Checklist

1. Load this reference + `parallel-task-execution`?
2. Host class is `read_only_fanout` or `disjoint_write_batch` (or worktree)?
3. Pack path `temp/parallel-batch-<batch_id>-review-v<n>.md` written?
4. `pairwise_recheck` re-run after workers stopped?
5. Lint (+ `--require-links` at closeout) ok?
6. Interactive wait / unattended auto-adopt recorded?
7. Single-writer merge + post-merge gates before batch-done claim?
