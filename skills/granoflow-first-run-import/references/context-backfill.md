# Context Backfill

Read this reference after confirmed import batches have been written and read
back from Granoflow.

Project and milestone descriptions are context maps for future agents. They
should be filled from imported evidence, not from the agent's hopes about what
the import meant.

## Timing

Backfill context only after:

1. project and milestone creates/reuses are known;
2. task imports have been read back;
3. review-card imports or candidates have been recorded;
4. failed and skipped batches are listed;
5. the user confirmed that description updates should proceed.

Do not write descriptions before import readback.

## Evidence Sources

Use only:

- imported tasks;
- task reviews;
- review cards or confirmed card candidates;
- source ledger summaries;
- decisions and rejected alternatives;
- risks and blockers;
- verification evidence;
- readback state from Granoflow.

Do not use raw private thread dumps, hidden chat memory, secrets, tokens,
private auth URLs, or long copied conversation text.

## Project Description Shape

A project description should stay compact and useful for future agents:

```text
Purpose:
Imported history:
Important decisions:
Durable lessons:
Active risks or blockers:
Current phase:
Next expected work:
Last import:
```

Include only sections that have evidence. Do not pad empty sections.

## Milestone Description Shape

A monthly milestone description should summarize that month:

```text
Month:
Imported work:
Outcomes:
Decisions and lessons:
Unresolved tasks or blockers:
Relation to project context:
```

Do not update archived milestone descriptions through ordinary workflow unless
the running app exposes a safe archive/context closure path.

## Tool Preference

Prefer context-steward tools when available:

- `granoflow_context_steward_status`
- `granoflow_project_context_update`
- `granoflow_milestone_context_update`
- `granoflow_milestone_context_archive`

If context-steward tools are unavailable, use structured project or milestone
updates only when the Local HTTP API clearly supports the needed description
field. Otherwise report context backfill as skipped.

## Final Report Fields

Report context backfill with:

- project descriptions updated;
- milestone descriptions updated;
- descriptions skipped and why;
- evidence sources used;
- readback or sync status;
- remaining context decisions for the user.
