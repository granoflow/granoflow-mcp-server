# Task And Card Import

Read this reference before turning retained agent records into Granoflow task
and review-card candidates.

This reference defines import boundaries. For detailed card-writing rules, read
`../../granoflow-agent-workflow/references/review-card-authoring.md` through the
base workflow skill.

## Task Candidate Gate

Create a task candidate only when the source contains at least one of:

- a clear work unit;
- a completed outcome;
- an unresolved next action;
- a blocker or waiting decision;
- a concrete verification or failure result;
- a reusable implementation or operations step tied to a project.

Do not create tasks from:

- greetings or acknowledgements;
- repeated status polling;
- raw model reasoning with no durable work result;
- duplicate summaries of the same work;
- temporary command output with no durable decision or action;
- private material that cannot be safely summarized.

## Task Candidate Fields

Each candidate should include:

- candidate id;
- title;
- project key;
- monthly milestone key;
- status: `completed`, `pending`, `blocked`, or `needs_confirmation`;
- source summary;
- source locator when available;
- started or ended evidence when available;
- task review candidate when the source has durable review value;
- dedupe key;
- completion source: `ai`, `human`, or `unknown`.

Completed work should become completed tasks only when the source clearly
records an outcome. Otherwise keep it as pending, blocked, or
needs-confirmation.

## Completion Source Tags

Before importing completed tasks, call `granoflow_source_tags_ensure`.

When writing imported or newly created completed tasks:

- AI clearly completed the work -> attach the `AI` source tag (`custom_ai`).
- A human clearly completed the work -> attach the `人工` source tag
  (`custom_u4eba5de5`).
- Source is uncertain -> do not attach either source tag.

Use `completionSource` on `granoflow_task_create` /
`granoflow_task_create_structured` for direct task writes. After review-card or
single-task import writes, PATCH the task tags when the import payload cannot
carry tags directly.

Do not invent alternate AI/人工 tag slugs. Do not attach source tags to pending
capture-only tasks unless the source clearly records completed human work.

## Task Review Gate

Write a task review candidate only when the source contains:

- a decision;
- a rejected alternative;
- a failure mode;
- verification evidence;
- reusable process detail;
- important unresolved risk;
- a lesson future agents should know.

Do not write a task review that merely says the task happened.

## Review-Card Candidate Gate

Create review-card candidates only for knowledge likely to change future action.
Valid shapes include:

- durable decisions;
- repeated failure modes;
- project rules;
- engineering conventions;
- security principles;
- user, customer, vendor, or team preferences;
- professional terms or concepts worth spaced practice.

Do not create review cards for:

- plain activity logs;
- one-off facts with no future action;
- secrets, OTPs, tokens, recovery codes, auth URLs, or credentials;
- long copyrighted excerpts;
- temporary logs;
- speculative claims without evidence.

## Card Candidate Fields

Each candidate should include:

- candidate id;
- front;
- back summary;
- card type;
- source summary;
- worthiness reason;
- dedupe key;
- fallback plain front/back shape when enhanced fields are unsupported.

Keep each card to one durable knowledge point. If a point is useful but not
worth spaced practice, keep it in the task review instead.

## Capability Handling

Before sending enhanced card fields:

1. call `granoflow_ai_agent_tools`;
2. inspect review-card draft note-field capability;
3. use enhanced fields only when advertised;
4. otherwise keep pronunciation, translation, and source hints in plain
   front/back content.

If a write returns an unsupported enhanced-field error, rewrite the card
candidate into fallback shape before retrying.

## Write Sequence

1. Dry-run or preview task writes where tools support it.
2. Import or create confirmed task batches.
3. Read back task state.
4. Import review-card candidates only after task/project/milestone context is
   known.
5. Stop on duplicate, unsupported capability, validation, or provenance errors.

Never retry by removing dedupe keys, source summaries, or safety constraints.
