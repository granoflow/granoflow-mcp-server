# Source Discovery

Read this reference before inspecting agent, thread, workspace, repository,
folder, or user-provided history sources for a first-run Granoflow import.

The goal is to build a bounded source ledger. Do not spend the turn debating
what a perfect importer would do.

## Source Scope

Use only sources the current host exposes or the user provides. Common sources:

- current Cursor, Codex, Hermes, or other agent workspace context;
- exported agent threads or session files;
- project folders and repository metadata;
- user-provided notes, reports, or migration files;
- existing Granoflow tasks, reviews, projects, milestones, and cards.

Unavailable examples:

- hidden cloud chat history;
- private browser history;
- another agent's account that the current host cannot read;
- local secrets, recovery codes, OTPs, auth URLs, or tokens;
- raw application databases outside documented Granoflow APIs.

If the user says "all threads", interpret that as all host-exposed and
user-authorized thread records available in the current environment. State
unavailable sources in the preview instead of inventing them.

## Source Ledger

Create a source ledger with one row per source group:

```text
Source | Type | Location | Date range | Project signal | Access status |
Usable records | Excluded records | Citation form | Notes
```

Allowed access statuses:

- `available`
- `provided_by_user`
- `host_exposed`
- `unavailable`
- `needs_user_file`
- `too_broad`
- `excluded_private`

Citation form should be short and stable, such as a thread id, file path, repo
name, date, or short source summary. Do not copy raw private history into the
ledger when a summary is enough.

## Default Import Budgets

Use these defaults unless the user provides tighter limits:

- projects: 20 maximum;
- monthly milestones per project: 24 maximum;
- task candidates: 300 maximum;
- review-card candidates: 120 maximum;
- write batch size: 20 objects maximum.

When a source exceeds a budget, sample deterministically by directness, recency,
project match, and evidence quality. Record skipped counts and reasons.

## Privacy And Secret Handling

Never include these in preview documents, task descriptions, reviews, cards, or
context descriptions:

- API tokens;
- recovery codes;
- OTPs;
- private auth URLs;
- credentials;
- payment identifiers;
- long private conversation dumps;
- temporary logs that are not durable lessons.

If a durable lesson concerns a secret exposure risk, summarize the principle
without copying the secret.

## When Sources Are Missing

If the current host exposes no historical agent records, continue with the
available path:

1. Tell the user which source types are unavailable.
2. Offer to import from a user-provided export file or current workspace
   evidence.
3. Create a preview only from actual accessible records.

Do not block first-run setup merely because a richer source might exist
elsewhere.
