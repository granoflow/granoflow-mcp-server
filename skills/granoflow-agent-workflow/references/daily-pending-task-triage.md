# Due Task Processing And Execution

Read this reference when the user asks the agent to process today's Granoflow
tasks, tasks for a specific day or range, more unfinished tasks, all unfinished
tasks, or the older daily pending-task triage workflow. The workflow resolves
the task scope from Granoflow app data, writes and grills an analysis document,
asks for user confirmation, writes and grills an execution plan, completes what
the agent can safely complete, and leaves user-only decisions as durable
Granoflow task data.

This is an agent workflow. The MCP server remains a thin Local HTTP API bridge:
use MCP tools and documented Granoflow API paths for reads, writes, reminders,
sync, and verification. Do not reimplement Granoflow business logic, inspect
SQLite directly, run app builds, or create a hidden task database.

## Trigger Phrases

Use this workflow for requests such as:

- "Process today's tasks";
- "process tomorrow's tasks";
- "process tasks for 2026-07-10";
- "process overdue tasks";
- "process all tasks";
- "check all unfinished gf tasks";
- "analyze pending Granoflow tasks and tell me what needs authorization";
- "write an analysis document for current tasks, then plan and execute";
- "daily task triage";
- "find tasks that need me, keys, login, or external action";
- "do what AI can do and leave the rest as nodes/reminders";
- `处理今日任务`;
- equivalent instructions in another language.

Do not use this workflow for a single obvious task unless the user asks for a
full pending-task sweep.

Public README, npm, registry, and MCP-directory copy must stay English-only.
Localized trigger examples belong in skill/runtime documentation and tests, not
canonical public listing copy.

Runtime behavior is multilingual. Parse equivalent commands in the user's
language, resolve dates and task scope in that language, and write prompts,
blockers, confirmation requests, task descriptions, analysis summaries, plans,
and final reports in the user's language by default unless the user asks
otherwise. Preserve official product names, API names, command names,
environment variable names, and file paths in their original spelling.

## Phase 0: Connect And Scope

1. Call the setup/status tool or otherwise verify that the Granoflow Local HTTP
   API is reachable.
2. List current tasks from the running app. Treat the running app as the source
   of truth.
3. If the user is comparing against the visible UI, verify that the task set,
   app version, API base URL, or other observable facts match the user-visible
   app before writing.
4. Resolve the requested task scope before analysis:
   - For "Process today's tasks", include unfinished tasks whose due date is
     today in the user's local timezone.
   - If the user names a specific day, such as "process tomorrow's tasks",
     "process tasks for 2026-07-10", or "process last Friday's tasks", use that
     concrete day.
   - If the user names a range, such as this week, next week, this month,
     overdue tasks, or tasks before a date, use that range.
   - If the user asks to complete more tasks, broaden conservatively from today
     to overdue plus near-term unfinished tasks, and show the chosen boundary
     before execution.
   - If the user asks to process all tasks, include all unfinished Granoflow
     tasks unless they explicitly include completed or archived records too.
5. Include active in-progress states when they match the resolved scope. Exclude
   done, archived, trashed, deleted, and undated tasks from date-based scopes
   unless the user explicitly includes them.
6. If a natural-language date is ambiguous, state the resolved concrete date or
   date range before analysis. Ask only when ambiguity changes which tasks would
   be touched.
7. Record the requested scope, resolved concrete dates, task ids, titles,
   status, project, milestone, due/reminder times, and description availability
   in the analysis document.

If the API is unreachable, stop and explain that Granoflow must be open with the
Local HTTP API enabled. If the API cannot expose due dates or cannot support the
requested scope, stop and report the tool gap instead of guessing from titles or
chat history. Do not invent task data from memory.

## Document Names

Use simple, portable file names that do not depend on a private numbering
system:

- Analysis documents: `analysis-YYYY-MM-DD-due-tasks.md` or
  `analysis-YYYY-MM-DD-<short-topic>.md`
- Plan documents: `plan-YYYY-MM-DD-due-tasks.md` or
  `plan-YYYY-MM-DD-<short-topic>.md`

When a project has a documented temporary-docs directory, write there. Otherwise
use a clearly local working directory such as `docs-temp/`, `.local-ai/`, or an
agent-provided workspace path. Do not write private task content into public
docs unless the user explicitly asks for a public artifact.

## Phase 1: Write The Analysis Document

Before execution, write a Markdown analysis document. Use the user's repository
or workspace convention when one is known; otherwise use a temporary local
analysis path that is clearly not a public product document.

Use these classifications:

- `ai_can_do_now`: the agent can complete it with current permissions, local
  evidence, and no external side effect requiring approval.
- `needs_user_authorization_or_input`: the agent can probably complete it after
  the user approves, logs in, provides a required file, supplies missing
  information, or makes an account/payment/publish/delete/send decision.
- `user_must_do`: the user must personally act, decide, pay, sign in, handle a
  private account surface, or make a subjective judgment the agent cannot safely
  make.

Secondary flags may be added when useful:

- `needs_secret_or_key`: token, OTP, recovery code, login, private account, or
  browser/session state is required.
- `needs_login_or_2fa`: login or second-factor action is required.
- `needs_missing_file`: a required local or private file is missing.
- `needs_external_account_action`: external account state blocks safe execution.
- `likely_done_verify_only`: evidence suggests the work is already done; the
  agent should verify and close only if readback supports it.
- `stale_or_not_worth_doing`: cost, risk, stale goal, or conflict outweighs
  value.
- `conflicts_with_current_requirement`: the task points at an older direction
  that appears to contradict current requirements.
- `blocked_by_tool_gap`: Granoflow/MCP lacks a needed node, reminder, sync, or
  API surface; record the tool gap instead of faking completion.

The analysis must explicitly list every approval point and every needed key,
login, OTP, file, account action, or missing fact by name, never by secret
value. For example, write `OPENAI_API_KEY needed in local environment`, not the
key itself. If a secret is needed, tell the user to provide it through an
appropriate local secure channel or existing app/account flow, not paste it into
public docs, task descriptions, test snapshots, or chat transcripts.

Recommended ledger columns:

```text
Task | Project/Milestone | Due evidence | What it really asks |
Primary bucket | Secondary flags | Worth doing? | Existing evidence |
Conflict? | User/auth/input needed | Recommended next action |
AI can do now? | Verification
```

Use this template:

```markdown
# Analysis: <topic>

Date: <YYYY-MM-DD>
Source: <Granoflow API base URL or tool>
Snapshot time: <local time>
Requested scope: <user wording>
Resolved scope: <concrete date, date range, or all-task boundary>

## Summary

- Total scoped unfinished tasks: <count>
- AI can do now: <count>
- Needs user authorization or input: <count>
- User must do: <count>
- Likely done / verify only: <count>
- Stale or not worth doing: <count>
- Conflicting with current requirements: <count>
- Blocked by tool gap: <count>

## Included Tasks

| Task | Due evidence | Why included |
| ---- | ------------ | ------------ |

## Excluded Tasks

| Task | Reason |
| ---- | ------ |

## Task Ledger

| Task | Project/Milestone | Due evidence | What it really asks | Primary bucket | Secondary flags | Worth doing? | Existing evidence | Conflict? | User/auth/input needed | Recommended next action | AI can do now? | Verification |
| ---- | ----------------- | ------------ | ------------------- | -------------- | --------------- | ------------ | ----------------- | --------- | ---------------------- | ----------------------- | -------------- | ------------ |

## Authorization And Input Checklist

| Task | Approval, key, login, file, account action, or missing fact | Value requested? | Safe way to provide | Blocks execution? |
| ---- | ----------------------------------------------------------- | ---------------- | ------------------- | ----------------- |

## Blocking Questions

| Task | Question | Recommended answer | Why it matters | Blocks execution? |
| ---- | -------- | ------------------ | -------------- | ----------------- |

## Execution Batches

1. AI can do now:
2. Verify-only:
3. Needs user authorization or input:
4. User must do:
5. Deferred / stale / not worth doing:

## Proposed Writes

- Task updates:
- Nodes:
- Reminders:
- Notification tasks:
- Document attachments:
- Plain-language task descriptions:
- Task reviews/cards:
- Sync:

## Risks And Assumptions

- <risk or assumption>
```

Use the user's language by default. Preserve official product names, API names,
environment variable names, command names, and file paths in their original
spelling.

## Phase 2: Analysis Grill And Revision

Before showing the analysis as final, run a grill pass and revise the analysis.

The grill pass must ask at least these questions:

- Did the workflow resolve the user's requested task scope correctly?
- If the user did not request another scope, did it stay limited to tasks due
  today?
- Did any task get labeled `ai_can_do_now` while hiding publish, send, payment,
  deletion, account, login, key, or irreversible effects?
- Are all requested keys or secrets named without exposing values?
- Is any `user_must_do` task being disguised as an agent task?
- Is any likely-done or stale task worth verifying instead of executing?
- Would a non-technical user understand what is being asked from them?

Every non-`keep` grill result must be applied back to the analysis document
before the workflow proceeds.

## Phase 3: Confirmation Gate

Show the analysis summary and ask for confirmation before executing, unless the
user's latest instruction explicitly pre-authorizes the same action after seeing
the analysis. Internal confidence is not user confirmation.

The confirmation request should name:

- tasks the agent proposes to execute now;
- tasks that need user authorization, secrets, login, files, account actions, or
  missing info;
- tasks the user should do personally;
- tasks proposed as verify-only, obsolete, not worth doing, or conflicting;
- exact approvals and missing inputs requested;
- the phrase the user can use to proceed, localized to the user's language, such
  as `Start execution` for English or `开始执行` for Chinese;
- any task writes the agent will make, such as node additions, reminders,
  notification tasks, document attachments, task description updates, task
  reviews, completions, or sync attempts.

If the user confirms only part of the analysis, execute only that part and keep
the rest in the document as deferred.

## Phase 4: Plan, Grill, And Revise

Use [task-plan-workflow.md](task-plan-workflow.md) as the Plan owner for every
executable task. The batch outline below may organize the ledger, but it must
not replace the owner workflow's immutable Plan attachment, deliverable node,
handoff, manual-acceptance, current-state reconciliation, or NodeService
completion contracts.

For tasks classified as executable, write a plan document before changing code,
docs, public copy, release settings, or other durable artifacts. Use the
project's own planning rules when the task belongs to a repo with stricter
rules.

The plan must include:

- in-scope tasks and out-of-scope tasks;
- files, systems, APIs, projects, accounts, or docs that may be touched;
- forbidden actions;
- database/schema/UI/publish/sync/auth impact when relevant;
- verification commands or user-visible checks;
- rollback or stop conditions;
- how completion will be written back to Granoflow.
- how the final analysis and plan documents will be attached or linked.

Use this template:

```markdown
# Plan: <topic>

Date: <YYYY-MM-DD>
Source analysis: <analysis document path>
Confirmed by user: <yes/no and confirmation text>

## Goal

<What user-visible or task-visible result this plan will produce.>

## In Scope

- <task or change>

## Out Of Scope

- <explicit non-goal>

## Impact Check

| Area                         | Impact                | Notes     |
| ---------------------------- | --------------------- | --------- |
| Data/schema                  | none / possible / yes | <details> |
| UI/user-visible copy         | none / possible / yes | <details> |
| Sync/backup/import           | none / possible / yes | <details> |
| Auth/secrets/payment         | none / possible / yes | <details> |
| External publish/delete/send | none / possible / yes | <details> |

## Steps

1. <implementation or work step>
2. <verification step>
3. <Granoflow writeback step>

## Adversarial Review

| Lens | Question | Recommended answer | Evidence | Second-order risk | Status |
| ---- | -------- | ------------------ | -------- | ----------------- | ------ |

## Revised Plan

<State what changed after the adversarial review.>

## Verification

- <command, API readback, UI check, or external surface>

## Stop Conditions

- <condition that requires user input or blocks execution>

## Completion Writeback

- Document attachments or safe links:
- Plain-language task description updates:
- Task review:
- Review cards:
- Tasks to mark done:
- Tasks to leave pending:
- Sync:
```

Run an adversarial review pass before execution. If a local review/finalizer
workflow is available and the user asked to use it, follow that workflow.
Otherwise do the adversarial review inline in the plan document.

The adversarial review must attack:

- whether the plan implements the user's actual intent or a smaller safer
  approximation;
- whether any task is stale, already done, or not worth doing;
- whether old long-lived docs/specs conflict with the user's newer intent;
- whether external authorization, account state, payment, publish, deletion, or
  secrets are hidden in the plan;
- whether the planned evidence proves the user-visible result;
- whether the task belongs in Granoflow app, MCP server, docs/manual, marketing,
  release, or user-only action;
- whether every execution step traces back to the confirmed analysis;
- whether the plan secretly adds scope the user did not approve;
- what breaks if sync, Local HTTP API, review-card writing, node writing, or
  reminders are unavailable.

Revise the plan after the adversarial review. Do not execute a plan that still
has blocking questions.

Every non-`keep` grill result must be applied back to the plan document. If the
grill finds a blocker, execution stops and the blocker is written back to the
task.

## Phase 5: Attach Documents And Write Plain-Language Descriptions

After both documents are finalized, attach the final analysis and plan
documents to the relevant Granoflow task or tasks when the running app and MCP
tools expose a documented attachment surface.

If first-class attachment support is unavailable, write stable local paths or
safe document links into the task description and record
`blocked_by_tool_gap: attachment_api_unavailable` in the analysis or final
report. Do not silently pretend that attachment happened.

Update relevant task descriptions with a simple explanation based on the final
analysis and plan.

Plain-language description rules:

- explain the task like a normal person would explain a household errand or
  office handoff;
- use short sentences;
- use examples or analogies when they reduce confusion;
- avoid invented agent/process jargon;
- avoid unexplained internal labels such as `ai_can_do_now`, `context pack`,
  `tool gap`, or `writeback` in user-facing prose;
- when a professional term is unavoidable, write the English term first and, if
  the user's language is not English, add the common local translation in
  parentheses;
- never include secret values, OTPs, private auth URLs, or raw sensitive account
  data.

For example, in Chinese:

```text
今天这件事像整理办公桌：我会先把能自己处理的文件放好，把需要你签字或提供钥匙的文件单独放一摞，把必须你本人处理的文件留下来。你确认后，我只处理你同意的部分，并把检查结果写回这里。
```

For an English-speaking user:

```text
This step needs an OAuth token. Do not paste the token into the task; configure
it in the safe local place first, then I can continue.
```

## Phase 6: Execute Safe Work

Execute only work classified as safe and confirmed. Keep diffs small and local
to the task. Follow the owning project's rules, tests, and release gates.

During execution:

- keep the analysis/plan document updated with material discoveries;
- do not mark tasks complete until verification passes or the user accepts a
  documented limitation;
- when a task turns out already done, record the evidence and close it only if
  the user allowed closure or the task's own contract allows verify-only
  completion;
- when a task becomes blocked, switch to the waiting workflow below instead of
  leaving a chat-only question.

## Phase 7: Blocking User Input

When a task needs user authorization, login, OTP, secret material, external
account action, missing files, private context, or an explicit decision, use the
waiting-for-user-input workflow.

Required writes:

1. Add a current node to the original task when a node-aware API or documented
   tool exists. The node must say:
   - what decision or input is needed;
   - what action is blocked;
   - why the agent cannot safely proceed;
   - acceptable user responses: approve, reject, revise, provide input, or
     reschedule;
   - that the user should respond by adding a new explicit node under the
     original task.
2. Read the original task back and verify that the waiting node exists before
   making any sync or delivery claim.
3. Set the original task reminder to local current time plus 3 minutes.
4. Create a separate notification task with reminder at local current time plus
   10 minutes. The notification task must stand alone, name the original task,
   describe the same blocker, and tell the user to add a new node under the
   original task.
5. If the app or MCP does not expose node writes, write the same content into
   the task description or another documented field and classify the result as
   `blocked_by_tool_gap`.
6. Attempt sync through the documented Granoflow API/tool when sync is
   available.
7. Report sync visibility as `synced_to_server`, `local_only`, or
   `unknown_remote_visibility`. Do not claim remote delivery or phone
   notification delivery without app/API evidence.
8. After the original task completes or the blocker is resolved, recommend
   deleting the temporary notification task. If deletion is unavailable or
   inappropriate, complete, archive, or otherwise clean it up only after
   verifying it is the notification task for the resolved original task.

Notification task description template:

```text
This task is waiting for your explicit response on the original task.

Original task: <title or id>
Blocked action: <action>
Target: <object/account/repo/task>
Why user input is required: <authorization/login/secret/payment/external effect>

Please add a new node under the original task with one of:
- Response: approve
- Response: reject
- Response: revise to ...
- Response: provide <missing input>
- Response: reschedule to tomorrow 09:00

The agent must not proceed with the blocked action until that node exists.
After the original task is completed or the blocker is resolved, this temporary
notification task should be deleted or cleaned up.
```

## Phase 8: Completion And Writeback

For work that entered Plan/Execution, write and content/hash-readback the
versioned Task Delivery before completion. Node-backed tasks complete only via
NodeService; node-less compatibility tasks may use `granoflow_task_finish` once.
Default completion leaves deep Task Review and Review Cards for a separately
initiated Deferred Task Review.

Task completion writeback should include:

- what was completed;
- evidence and commands or checks;
- changed files or external surfaces when relevant;
- skipped checks and why;
- residual risk;
- attachment or fallback-link status for final analysis and plan documents;
- plain-language task description updates;
- Review status pending or explicitly completed;
- links or paths to analysis and plan documents when safe.

After completion, read back the task list or exported task and verify completed
tasks are really done. If verification fails, report the mismatch and do not
claim closure.

## Phase 9: Sync And Final Report

After task, node, reminder, notification task, review, or card writes, attempt
sync when the running app advertises or exposes a documented sync path and the
user's setup makes sync appropriate.

The final report must include:

- analysis document path;
- plan document path when one was created;
- attachment or fallback-link status;
- tasks completed;
- tasks left pending and why;
- blockers written as nodes/reminders/notification tasks;
- task descriptions updated;
- review cards created;
- sync visibility result;
- verification results;
- skipped checks and residual risks.

## Stop Conditions

Stop and ask the user or leave durable waiting nodes when:

- the same blocker repeats three times;
- the Local HTTP API becomes unreachable;
- the current app data no longer matches the visible user surface;
- a task requires a secret, OTP, login, payment, publish, deletion, account
  change, or irreversible external action without explicit authorization;
- the analysis finds a product-direction conflict below 90% intent confidence;
- the plan's adversarial review finds a blocking question;
- verification evidence is unavailable and the task is not safe to mark done;
- required node/reminder/sync tools are missing and the workaround would hide
  the blocker from Granoflow.

## Tool Gap Notes

This workflow benefits from dedicated node, reminder, and sync tools. Until the
running Granoflow app and MCP server expose stable first-class tools for those
actions, use documented lower-level JSON task/API tools only when the field or
endpoint is clearly supported. If support is missing, record the tool gap in
the analysis instead of silently weakening the workflow.
