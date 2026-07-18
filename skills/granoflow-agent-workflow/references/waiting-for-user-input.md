# Waiting For User Input

Read this reference when part of a Granoflow task depends on a user-only action:
permission, a decision, login, 2FA, opening Granoflow, missing material, or
private context the agent cannot infer.

The waiting state should usually be local to the node that needs the user. Do
not block the whole task while safe work remains.

Public README, npm, registry, and MCP-directory copy must stay English-only.
Localized trigger examples belong in skill/runtime documentation and tests, not
canonical public listing copy. Runtime behavior is multilingual: write waiting
nodes, notification tasks, reminders, confirmation prompts, and final reports in
the user's language by default.

## Required Writes

Use the Granoflow Local HTTP API or documented Granoflow tools.

When this branch follows delegated-authorization evaluation, preserve the stable
deny reason from `decision=denied` in the waiting node. Missing envelope,
unreadable owner attachment, `attachmentSha256` mismatch, or
`receiptVerified=false` is `stale_state`, not permission to continue. A GFMCP tag
is eligibility only and is never authorization.

1. Complete any already-finished task nodes when a node-aware API path is
   available.
2. Move safe, non-authorized nodes before the authorization node when they can be
   completed without user-only context, external side effects, privacy exposure,
   account changes, irreversible changes, or other explicit authorization.
3. Add a current node on the original task with a direct description of the
   requested authorization, the blocked action, and what user responses count as
   approval, rejection, or a changed instruction.
4. Read the original task back and verify the waiting node exists, belongs to
   the intended original task, describes the intended blocker, and contains no
   secret value. If local readback fails, stop and report
   `waiting_node_local_write_failed`.
5. Set the original task `remindAt` to local current time plus 3 minutes.
6. Create a separate notification task with `remindAt` set to local current
   time plus 10 minutes. The task must describe the real authorization problem,
   not only say that the agent is waiting.
7. Read back the original task reminder and notification task.
8. Attempt cloud sync through the Local HTTP API when sync is available, then
   classify visibility as `synced_to_server`, `local_only`, or
   `unknown_remote_visibility`.
9. Continue the safe nodes first. Switch to other tasks only after no safe node
   remains before the authorization decision.

The notification task title and description should stand on their own. Include:

- the requested user action or decision;
- the original task title or id;
- the concrete target or object affected by the decision;
- the external effect, irreversible effect, privacy effect, account effect, or
  other reason this needs user authorization;
- the acceptable response options: approve, reject, revise the action, provide
  missing input, or reschedule;
- that the user should respond by adding a new node with explicit text under
  the original task;
- that the notification task is a temporary pointer back to the original task,
  not the main conversation thread;
- any safe context needed to decide, without copying secrets or tokens.

Generic response examples:

- `Response: approve`
- `Response: reject`
- `Response: revise to ...`
- `Response: reschedule to tomorrow 09:00`

## User Response Contract

Tell the user to add a new node under the original task. The node title must
use explicit text such as:

- approve: `同意`, `批准`, `可以执行`, `继续`, `yes`, `approve`;
- reject: `不同意`, `不要`, `取消`, `不执行`, `no`, `reject`;
- revise: `改成...`, `改为...`, `只做...`, `不要...`;
- reschedule: `一小时以后`, `明天上午 9 点提醒我`, `10 分钟后再问我`;
- provide input: attach or paste the missing file, answer the question, or give
  the requested credential-free context.

If the user reschedules, update the reminder rather than treating the original
action as approved. If the user revises the action, confirm or execute only the
revised action that is safe and sufficiently specific.

## Where The User Should Reply

Use this response-location rule in the waiting node and notification task
description:

- The user should add a new node under the original task to express the
  decision. This makes the answer visible as synced Granoflow task data.
- The response node must be specific enough to act on, for example
  `Response: approve`, `Response: reject`, or
  `Response: reschedule to tomorrow 09:00`.
- If multiple response nodes conflict, treat the newest explicit user response
  as authoritative when timestamps are available. If the conflict is unclear,
  ask before taking the external action.

Only data written into Granoflow task fields or nodes will exist as synced
Granoflow data. For this workflow, the durable user response should be a new
node under the original task, not a hidden chat-only instruction and not a reply
stored only on the notification task.

## Tooling Notes

- Prefer structured task tools when they expose the required fields.
- If a structured tool does not expose a needed field, use the lower-level JSON
  task tools or `granoflow_api_request`.
- Use `/v1/sync/push` through `granoflow_api_request` only when a sync attempt is
  appropriate for the user's current setup.
- Do not add execution dependencies on external Granoflow command-line wrappers.

## Sync Status Contract

Do not claim that the server, another device, or a phone notification received
the waiting node unless the app or API returns explicit evidence.

Report one of:

- `synced_to_server`: only when the app/API explicitly returns evidence that the
  write was pushed or remote state is current.
- `local_only`: local write/readback succeeded, but sync is unavailable,
  disabled, failed, or unverified.
- `unknown_remote_visibility`: sync was attempted, but the response does not
  prove server visibility.

Never write a generic "pushed" or "notified" success report without one of these
statuses.

## Reminder Safety

- Do not write reminders in the past.
- If the calculated reminder time has already passed by the time the write
  happens, recalculate it from the current local time.
- If sync fails or is unavailable, report that local writes were made but remote
  devices may not see them until a later sync.
- Do not claim that a phone notification was delivered unless the app or API
  returns evidence of delivery.

## Notification Task Cleanup

After the original task is completed or the blocker is resolved, recommend
deleting the temporary notification task. If deletion is unavailable or
inappropriate for the app's task-management semantics, complete, archive, or
otherwise clean it up only after verifying that it is the notification task for
the resolved original task.

## Checkpoints

- The blocked action is understandable without reading the chat.
- Safe nodes that do not need authorization are moved before the waiting node and
  attempted first.
- Local readback proves the waiting node exists on the original task before sync
  is attempted.
- The original task has a near reminder 3 minutes out.
- The notification task has a second reminder 10 minutes out.
- The notification task names the specific authorization issue and the target
  affected by it.
- The notification task includes clear approve/reject/revise/reschedule options.
- The waiting node and notification task explain that synced user replies are
  added to the original task as new nodes with explicit decision text.
- The original task and notification task have different reminder times.
- The notification task is not marked done or hidden before the blocker is
  resolved.
- Cleanup recommends deleting the temporary notification task after the original
  task completes or the blocker is resolved.
- No secrets, tokens, or private credentials are copied into task titles,
  descriptions, nodes, or tool results.
