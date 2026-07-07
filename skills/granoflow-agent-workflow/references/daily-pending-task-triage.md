# Daily Pending Task Triage And Execution

Read this reference when the user asks the agent to inspect all current
unfinished Granoflow tasks, decide what they really require, write an analysis
document, plan and adversarially review the executable work, complete what the agent can safely
complete, and leave user-only decisions as durable Granoflow task data.

This is an agent workflow. The MCP server remains a thin Local HTTP API bridge:
use MCP tools and documented Granoflow API paths for reads, writes, reminders,
sync, and verification. Do not reimplement Granoflow business logic, inspect
SQLite directly, run app builds, or create a hidden task database.

## Trigger Phrases

Use this workflow for requests such as:

- "check all unfinished gf tasks";
- "analyze pending Granoflow tasks and tell me what needs authorization";
- "write an analysis document for current tasks, then plan and execute";
- "daily task triage";
- "find tasks that need me, keys, login, or external action";
- "do what AI can do and leave the rest as nodes/reminders";
- equivalent instructions in another language.

Do not use this workflow for a single obvious task unless the user asks for a
full pending-task sweep.

## Phase 0: Connect And Scope

1. Call the setup/status tool or otherwise verify that the Granoflow Local HTTP
   API is reachable.
2. List current tasks from the running app. Treat the running app as the source
   of truth.
3. If the user is comparing against the visible UI, verify that the task set,
   app version, API base URL, or other observable facts match the user-visible
   app before writing.
4. Include only unfinished tasks by default. If the API returns multiple
   unfinished-like states, include `pending` and active in-progress states, and
   exclude done, archived, trashed, and deleted tasks unless the user says
   otherwise.
5. Record the task ids, titles, status, project, milestone, due/reminder times,
   and description availability in the analysis document.

If the API is unreachable, stop and explain that Granoflow must be open with the
Local HTTP API enabled. Do not invent task data from memory.

## Document Names

Use simple, portable file names that do not depend on a private numbering
system:

- Analysis documents: `analysis-YYYY-MM-DD-<short-topic>.md`
- Plan documents: `plan-YYYY-MM-DD-<short-topic>.md`

When a project has a documented temporary-docs directory, write there. Otherwise
use a clearly local working directory such as `docs-temp/`, `.local-ai/`, or an
agent-provided workspace path. Do not write private task content into public
docs unless the user explicitly asks for a public artifact.

## Phase 1: Write The Analysis Document

Before execution, write a Markdown analysis document. Use the user's repository
or workspace convention when one is known; otherwise use a temporary local
analysis path that is clearly not a public product document.

Use these classifications:

- `ai_safe_now`: the agent can do it with current permissions and local
  evidence.
- `needs_user_authorization`: external effect, publish, delete, payment,
  account, sending, irreversible change, or user approval is required.
- `needs_secret_or_login`: token, OTP, recovery code, login, private account, or
  browser/session state is required.
- `needs_more_information`: the task goal is under-specified and local evidence
  cannot resolve it.
- `user_only`: the user must personally do the action, decide the subjective
  preference, provide legal/payment/account context, or operate an external
  surface the agent cannot safely control.
- `likely_done_verify_only`: evidence suggests the work is already done; the
  agent should verify and close only if readback supports it.
- `not_worth_doing`: cost, risk, stale goal, or conflict outweighs value.
- `conflicts_with_current_requirement`: the task points at an older direction
  that appears to contradict current requirements.
- `blocked_by_tool_gap`: Granoflow/MCP lacks a needed node, reminder, sync, or
  API surface; record the tool gap instead of faking completion.

Recommended ledger columns:

```text
Task | Project/Milestone | What it really asks | Classification |
Worth doing? | Existing evidence | Conflict? | User/auth needed |
Recommended next action | AI can do now? | Verification
```

Use this template:

```markdown
# Analysis: <topic>

Date: <YYYY-MM-DD>
Source: <Granoflow API base URL or tool>
Snapshot time: <local time>
Scope: <which projects/milestones/tasks are included>

## Summary

- Total unfinished tasks: <count>
- Safe for AI now: <count>
- Needs user authorization: <count>
- Needs secret/login: <count>
- Needs more information: <count>
- User-only: <count>
- Likely done / verify only: <count>
- Not worth doing or stale: <count>
- Conflicting with current requirements: <count>
- Blocked by tool gap: <count>

## Task Ledger

| Task | Project/Milestone | What it really asks | Classification | Worth doing? | Existing evidence | Conflict? | User/auth needed | Recommended next action | AI can do now? | Verification |
| ---- | ----------------- | ------------------- | -------------- | ------------ | ----------------- | --------- | ---------------- | ----------------------- | -------------- | ------------ |

## Blocking Questions

| Task | Question | Recommended answer | Why it matters | Blocks execution? |
| ---- | -------- | ------------------ | -------------- | ----------------- |

## Execution Batches

1. Safe now:
2. Verify-only:
3. Needs user response:
4. Deferred / not worth doing:

## Proposed Writes

- Task updates:
- Nodes:
- Reminders:
- Follow-up tasks:
- Task reviews/cards:
- Sync:

## Risks And Assumptions

- <risk or assumption>
```

## Phase 2: Confirmation Gate

Show the analysis summary and ask for confirmation before executing, unless the
user's latest instruction explicitly pre-authorizes the same action after seeing
the analysis. Internal confidence is not user confirmation.

The confirmation request should name:

- tasks the agent proposes to execute now;
- tasks that need user authorization, secrets, login, or missing info;
- tasks proposed as verify-only, obsolete, not worth doing, or conflicting;
- any task writes the agent will make, such as node additions, reminders,
  follow-up tasks, task reviews, completions, or sync attempts.

If the user confirms only part of the analysis, execute only that part and keep
the rest in the document as deferred.

## Phase 3: Plan, Review, And Revise

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
- what breaks if sync, Local HTTP API, review-card writing, node writing, or
  reminders are unavailable.

Revise the plan after the adversarial review. Do not execute a plan that still
has blocking questions.

## Phase 4: Execute Safe Work

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

## Phase 5: Blocking User Input

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
2. Set the original task reminder to local current time plus 5 minutes.
3. Create a separate follow-up task with reminder at local current time plus 10
   minutes. The follow-up task must stand alone and describe the same blocker.
4. If the app or MCP does not expose node writes, write the same content into
   the task description or another documented field and classify the result as
   `blocked_by_tool_gap`.
5. Attempt sync through the documented Granoflow API/tool when sync is available.
6. Report any sync failure as local-only visibility risk. Do not claim remote
   delivery or phone notification delivery without app/API evidence.

Follow-up task description template:

```text
This task is waiting for your explicit response on the original task.

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
```

## Phase 6: Completion And Writeback

For completed tasks, prefer `granoflow_task_finish` when available. Write a
meaningful task review only when the task produced decisions, evidence, durable
lessons, unresolved risk, or reusable process detail. Create review cards only
for durable points that change future action.

Task completion writeback should include:

- what was completed;
- evidence and commands or checks;
- changed files or external surfaces when relevant;
- skipped checks and why;
- residual risk;
- cards created or deliberately omitted;
- links or paths to analysis and plan documents when safe.

After completion, read back the task list or exported task and verify completed
tasks are really done. If verification fails, report the mismatch and do not
claim closure.

## Phase 7: Sync And Final Report

After task, node, reminder, follow-up, review, or card writes, attempt sync when
the running app advertises or exposes a documented sync path and the user's
setup makes sync appropriate.

The final report must include:

- analysis document path;
- plan document path when one was created;
- tasks completed;
- tasks left pending and why;
- blockers written as nodes/reminders/follow-up tasks;
- review cards created;
- sync attempt result;
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
