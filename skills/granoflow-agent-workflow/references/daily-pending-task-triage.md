# Due Task Processing And Execution

Runtime triggers include `Process today's tasks`, `处理今日任务`, and equivalent
requests in the user's language.

Read this reference for today's tasks, a date/range, overdue work, more tasks,
or all unfinished Granoflow tasks. This is host-side batch orchestration. MCP
remains a thin Local HTTP API bridge and never owns the traversal or execution
loop.

Use localized runtime prompts and reports. Keep public README, npm, registry,
and directory copy English-only.

## Connect And Resolve Scope

1. Verify the running Granoflow Local HTTP API and current app/task surface.
2. Resolve the user request to concrete local dates and unfinished task states.
3. `Process today's tasks` means unfinished tasks due today unless the user
   explicitly asks for another date, range, overdue, more, or all tasks.
4. Include in-progress tasks when they match. Exclude done, archived, trashed,
   deleted, and undated tasks from date scopes unless explicitly included.
5. If API evidence cannot establish the requested scope, report the tool gap
   instead of guessing from titles, chat, or memory.

Record requested scope, resolved dates, snapshot time, task ids/titles/status,
project/milestone, due/reminder evidence, and included/excluded reasons in a
compact batch ledger. The ledger organizes traversal; it never replaces each
task's Work Document.

## Classify Each Task Once

Primary classifications:

- `ai_can_do_now`: current permissions and evidence support safe work;
- `needs_user_authorization_or_input`: approval, login, file, missing fact, or
  external-account action is required;
- `user_must_do`: the user must personally act or make a subjective decision.

Optional flags:

- `needs_secret_or_key`
- `needs_login_or_2fa`
- `needs_missing_file`
- `needs_external_account_action`
- `likely_done_verify_only`
- `stale_or_not_worth_doing`
- `conflicts_with_current_requirement`
- `blocked_by_tool_gap`

Name the needed secret, account, or file without recording its value. Never put
tokens, OTPs, recovery codes, auth URLs, or raw private material into task data.

The ledger contains at least:

```text
Task | Due/scope evidence | Primary class | Flags | Existing evidence |
User/auth/input needed | Recommended next action | Verification
```

Show every scoped task exactly once, plus included/excluded counts and reasons.
Ask only questions that can change classification, order, authorization, or
whether a task should proceed.

## Per-Task Work Document

For every task that needs analysis or execution, read
`task-work-document-workflow.md` and create one adaptive Task Work Document.
Do not create separate new Analysis and Plan documents.

- Light tasks may reach `analysis_status=confirmed` and
  `planning_status=not_required` with only the five core sections.
- Tasks with risk, uncertainty, dependencies, multiple specialist methods, or
  separately authorized effects enter Planning in the same document family.
- The batch ledger or batch confirmation never replaces per-task Analysis,
  Planning permission/confirmation, immutable vNN identity, content/hash
  readback, or separate execution instruction.
- A blocked task stops that task and dependency-linked downstream work; safe,
  independent tasks may continue unless the user's ordering contract says the
  whole batch must stop.

The host may process tasks in order, but each active Work Document remains
self-contained and belongs to exactly one task.

## Confirmation And Execution

Present a bounded batch summary:

- tasks proposed for Analysis or safe execution;
- tasks needing authorization, input, login, secret setup, files, or account
  action;
- user-only, verify-only, stale, conflicting, and tool-gap tasks;
- proposed task writes, Work Document attachments, nodes, reminders,
  notification tasks, completion, and sync attempts.

A broad user instruction may pre-authorize clearly bounded, safe, reversible
operations, but it never pre-authorizes later-discovered publish, send, payment,
deletion, login, secrets, account changes, or other irreversible work.

Execute a task only after its unique active Work Document is Analysis-confirmed,
has valid Planning state (`not_required` or `confirmed`), passed App-owned
content/SHA-256 readback, and the user separately instructed the host to
implement it. Re-read current task/node state before every write.

## Waiting For User Input

When a task needs user action, use `waiting-for-user-input.md` instead of
leaving a chat-only question. Its owner defines the original-task node,
readback, reminders, notification task, response instructions, sync visibility,
and cleanup contract. Do not duplicate or weaken that workflow here.

## Delivery And Completion

After execution:

1. verify the Work Document Evidence against the real artifact or user surface;
2. create immutable Task Delivery with `source_work_document`, upload it, and
   read App-owned content/hash back;
3. for node-backed work, finish the final required node and let NodeService
   complete the parent;
4. for `planning_status=not_required` or other node-less compatibility work,
   create/readback Delivery first, then call compatibility finish once;
5. read the task back and require persisted completion before reporting done.

Legacy task work may read verified `source_analysis` and `source_plan` instead.
Do not create new legacy Analysis/Plan attachments.

Completion does not automatically start Deferred Task Review or a new Card
Checkpoint. It summarizes the Delivery checkpoint and leaves deep review for a
separately initiated workflow.

## Progressive Loading

Initially load only the main Agent Workflow, this batch reference, and the Work
Document owner/template. Load Profile, external Skill, Card, waiting, Delivery,
Review, or legacy references only when a task-specific trigger fires. Never
preload the full manifest for every task.

## Writeback And Final Report

For every task report:

- active Work Document or verified legacy source;
- attachment/readback status;
- Analysis and Planning state;
- execution and node state from current task data;
- Delivery path/status and verification evidence;
- completed, pending, blocked, user-only, or deferred result;
- skipped checks, residual risk, and next entry point;
- sync visibility as `synced_to_server`, `local_only`, or
  `unknown_remote_visibility` when sync was attempted.

Use plain language. Do not expose internal labels without explanation. Never
claim attachment, sync, notification delivery, completion, or remote visibility
without corresponding API/tool readback.
