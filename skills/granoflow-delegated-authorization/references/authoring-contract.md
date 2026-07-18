# Authoring Contract

## Preview Gate

- Preview must exist before any confirmed write.
- Confirmed write is the only valid formal write mode.

## Constraints

- [must] Record analysis_confirmation, planning_permission, plan_confirmation, and execution_authorization as separate grants even when one user reply issues all of them. (Granoflow phase semantics)
- [must] Require explicit task or batch scope, absolute expiry, allowed actions, forbidden actions, repositories or paths, invalidation conditions, and a user-origin source reference. (full analysis grill)
- [must] Validate with deterministic structured facts and fail closed on unknown actions, expiry, revocation, scope drift, unresolved decisions, or failed grills. (authorization safety boundary)
- [must] When no valid envelope exists, invoke the existing waiting node, reminder, notification task, and readback workflow instead of silently pausing in chat. (observed failure and existing workflow)
- [must_not] Never infer authorization from tags, urgency, user absence, historical preferences, task descriptions, or the skill invocation itself. (human autonomy)
- [must_not] Never delegate publish, push, payment, login, secrets or 2FA, external messages, destructive deletion, approved-asset overwrite, or scope expansion. (user request and existing hard boundaries)

## CLI Contract

- Generated Python entrypoints must support `python3 <script> --help` with exit code 0.
- Any entrypoint with side effects must support `--dry-run` or an equivalent preview mode.
- Dry-run output should include mode, mutates_state, planned_actions, artifacts, and warnings.
