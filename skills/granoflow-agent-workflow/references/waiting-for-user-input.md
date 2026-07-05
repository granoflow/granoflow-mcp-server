# Waiting For User Input

Read this reference when a Granoflow task is blocked on a user-only action:
permission, a decision, login, 2FA, opening Granoflow, approving a release,
providing a missing file, or supplying private context the agent cannot infer.

## Required Writes

Use the Granoflow Local HTTP API or documented Granoflow tools.

1. Complete any already-finished task nodes when a node-aware API path is
   available.
2. Add a current node on the original task with a direct description of what is
   missing.
3. Set the original task `remindAt` to local current time plus 5 minutes.
4. Create a separate follow-up task with `remindAt` set to local current time
   plus 10 minutes.
5. Attempt cloud sync through the Local HTTP API when sync is available.

The follow-up task title should stand on its own, for example:

- `Waiting for user approval: publish package`
- `Waiting for source file: Q2 revenue sheet`
- `Waiting for 2FA: npm publish`

## Tooling Notes

- Prefer structured task tools when they expose the required fields.
- If a structured tool does not expose a needed field, use the lower-level JSON
  task tools or `granoflow_api_request`.
- Use `/v1/sync/push` through `granoflow_api_request` only when a sync attempt is
  appropriate for the user's current setup.
- Do not add execution dependencies on external Granoflow command-line wrappers.

## Reminder Safety

- Do not write reminders in the past.
- If the calculated reminder time has already passed by the time the write
  happens, recalculate it from the current local time.
- If sync fails or is unavailable, report that local writes were made but remote
  devices may not see them until a later sync.
- Do not claim that a phone notification was delivered unless the app or API
  returns evidence of delivery.

## Checkpoints

- The blocked action is understandable without reading the chat.
- The original task and follow-up task have different reminder times.
- The follow-up task is not marked done or hidden.
- No secrets, tokens, or private credentials are copied into task titles,
  descriptions, nodes, or tool results.
