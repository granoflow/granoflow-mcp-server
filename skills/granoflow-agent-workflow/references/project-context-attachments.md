# Project Context Attachments

Use this reference whenever a workflow reads, writes, creates, updates, imports,
archives, or closes project-level context.

Granoflow exposes two canonical project document attachments:

- `project_snapshot.yaml`
- `project_rules.yaml`

`project_rules.yaml` may contain the project-only `interaction_style` section.
Resolve it with `granoflow_project_interaction_style`; if it is absent, use the
newcomer-friendly default. This is a presentation preference, not a second
source of project facts.

These files are project consistency guards, not a second automatic source of
truth. Prefer app-owned project-context-attachment tools when
`granoflow_ai_agent_tools` advertises `granoflow_project_context_attachments_v1`.

## Read Contract

1. Ensure the canonical attachments exist when the workflow will use project
   context.
2. Read freshness metadata and source watermarks before reading content.
3. Default to header, summary, and the smallest matching section by project id,
   task id, tag, scope, date, keyword, or section name.
4. Do not load the whole YAML into model context unless the user explicitly asks
   for a full audit, export, migration, rewrite, full read, or equivalent.
5. Treat `stale`, `partial`, `source_gap`, and `reconcile_failed` results as
   historical hints, not complete facts.

## Write Contract

1. `project_snapshot.yaml` may receive low-risk factual updates such as current
   state, next step, blocker, recent verification, and context gaps.
2. `project_rules.yaml` stores active rules, long-term preferences, boundaries,
   public-copy constraints, and short decision notes that still affect current
   execution.
3. Rules, wording, positioning, preference, and long-lived decision changes must
   return a proposal or conflict report unless the user has explicitly confirmed
   the exact change.
4. If a workflow writes project state but the snapshot or rules do not actually
   change, record `project_context_attachments_unchanged` with the reason.
5. After a write, read back through the app-owned project-context-attachment
   tool and verify the attachment and section status.

## Conflict Safety

When YAML disagrees with project facts, task records, project descriptions,
long-term rules, or public copy:

- factual snapshot deltas can be reconciled automatically when low risk;
- rules, wording, positioning, and decision conflicts must be shown as a
  proposal or conflict report;
- secrets, tokens, OTPs, recovery codes, private auth URLs, credentials, and
  private identifiers must fail closed and must not be written.

The report should say what differs, where each side came from, the recommended
action, whether user confirmation is required, and how ignoring the conflict
could mislead future agents.

## Workflow Call Sites

Call this reference after these workflows change durable project context:

- first-run import;
- requirement capture;
- due-task processing;
- task analysis and execution;
- task completion when it changes project state, next step, blocker, or rules;
- milestone archive or closeout;
- project or milestone context stewardship.

If the project-context-attachment tool is unavailable, continue safe user work
when possible, but report that project context attachment upkeep was skipped or
blocked.
