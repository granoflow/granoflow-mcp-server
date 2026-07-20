# Project Context Attachments

Use this reference whenever a workflow reads, writes, creates, updates, imports,
archives, or closes project-level context—and **before any software edit** that
could conflict with recorded code status or boundaries.

Granoflow exposes two canonical project document attachments:

- `project_snapshot.yaml` — **code / project status quo** (current modules,
  ownership, verified state, next step, blockers, recent verification, gaps)
- `project_rules.yaml` — **boundaries and durable rules** (constraints,
  preferences, public-copy limits, architectural/decision notes that still
  bind execution)

`project_rules.yaml` may contain the project-only `interaction_style` section.
Resolve it with `granoflow_project_interaction_style`; if it is absent, use the
newcomer-friendly default. This is a presentation preference, not a second
source of project facts.

These files are project consistency guards, not a second automatic source of
truth for task Outcome. Prefer app-owned project-context-attachment tools when
`granoflow_ai_agent_tools` advertises `granoflow_project_context_attachments_v1`.

## Hard Gate: Pre-Change Conflict Check (fail closed)

Any task that will edit code, tests, build files, engineering contracts, or
these YAML attachments **must** complete this gate. Soft “should read context”
reminders are not enough.

| Phase | Required | Fail closed |
| ----- | -------- | ----------- |
| Before first implementation edit (and before writing snapshot/rules) | Ensure both attachments exist (or record capability gap); read bounded relevant sections; compare planned change to snapshot status quo and rules boundaries | `project_context_check_missing` |
| When a conflict is detected (interactive) | Show conflict report; wait for explicit user confirmation of the chosen side | `project_context_conflict_unconfirmed` |
| When a conflict is detected (unattended) | AI decides `revise_code` or `revise_context_yaml`, **explicitly emit** that decision as a user-visible notice (not a question), then proceed only on that path | `project_context_decision_not_emitted` |
| Delivery / completion | Record check result, conflicts (if any), and the confirmed or emitted decision | `project_context_check_unreconciled` |

### Machine fields (Task Work)

```yaml
project_context_check_status: not_applicable | missing | checked_no_conflict | conflict_pending | conflict_resolved
project_context_conflict: none | present
# revise_code | revise_context_yaml | user_confirmed_<side> | not_applicable
project_context_resolution: not_applicable | revise_code | revise_context_yaml | user_confirmed_revise_code | user_confirmed_revise_context_yaml
project_context_decision_emitted: false | true
```

Rules:

1. Do **not** open or patch repository files for implementation while status is
   `missing` or `conflict_pending`.
2. **Interactive:** on conflict, do not auto-pick. Present what differs
   (snapshot vs planned code, and/or rules vs planned code), recommend one
   side, and require user confirmation. Ignoring the conflict fails closed as
   `project_context_conflict_unconfirmed`.
3. **Unattended:** on conflict, choose `revise_code` (change implementation to
   honor YAML) or `revise_context_yaml` (update snapshot and/or rules to match
   the authorized Outcome). Immediately output an explicit notice naming the
   decision, rationale, and which attachment sections will change. That notice
   does **not** consume `interaction_budget` (it is not a question). Skipping
   the notice fails closed as `project_context_decision_not_emitted`.
4. After resolving, set `conflict_resolved` and the matching
   `project_context_resolution`. If YAML is updated, use App write + readback;
   `project_rules.yaml` still follows Write Contract confirmation rules unless
   the unattended grant explicitly covers that rules update.
5. Copy-only tasks still read boundaries that affect public copy; they use
   visual/copy review and must not invent automated tests. They set
   `project_context_check_status` when copy rules in `project_rules.yaml` apply.
6. If context-attachment tools are unavailable, report the gap; do not pretend
   the check passed. Hard-stop software edits with
   `project_context_check_missing` unless the user explicitly waives in
   interactive mode for that task.

## Read Contract

1. Ensure the canonical attachments exist when the workflow will use project
   context or perform the Hard Gate.
2. Read freshness metadata and source watermarks before reading content.
3. Default to header, summary, and the smallest matching section by project id,
   task id, tag, scope, date, keyword, or section name.
4. Do not load the whole YAML into model context unless the user explicitly asks
   for a full audit, export, migration, rewrite, full read, or equivalent.
5. Treat `stale`, `partial`, `source_gap`, and `reconcile_failed` results as
   historical hints, not complete facts—still run the Hard Gate against the
   best available sections and record staleness in the conflict report.

## Write Contract

1. `project_snapshot.yaml` may receive low-risk factual updates such as current
   state, next step, blocker, recent verification, and context gaps.
2. `project_rules.yaml` stores active rules, long-term preferences, boundaries,
   public-copy constraints, and short decision notes that still affect current
   execution.
3. Rules, wording, positioning, preference, and long-lived decision changes must
   return a proposal or conflict report unless the user has explicitly confirmed
   the exact change (interactive) or an unattended grant plus an emitted
   `revise_context_yaml` decision covers that exact update.
4. If a workflow writes project state but the snapshot or rules do not actually
   change, record `project_context_attachments_unchanged` with the reason.
5. After a write, read back through the app-owned project-context-attachment
   tool and verify the attachment and section status.

## Conflict Safety

When YAML disagrees with intended code change, project facts, task records,
project descriptions, long-term rules, or public copy:

- run the Hard Gate above (interactive confirm vs unattended explicit decision);
- secrets, tokens, OTPs, recovery codes, private auth URLs, credentials, and
  private identifiers must fail closed and must not be written.

The conflict report should say what differs, where each side came from, the
recommended action, whether user confirmation is required (interactive) or which
decision was emitted (unattended), and how ignoring the conflict could mislead
future agents.

## Workflow Call Sites

Call this reference:

- **before the first edit** of every software (and copy-boundary) task;
- after first-run import;
- after requirement capture;
- during task analysis, planning, and execution;
- at task completion when project state, next step, blocker, or rules change;
- at milestone archive or closeout;
- during project or milestone context stewardship.

If the project-context-attachment tool is unavailable, continue non-edit user
work when possible, but report that project context attachment upkeep was
skipped or blocked—and do not claim Hard Gate success.
