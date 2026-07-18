---
name: granoflow-delegated-authorization
description: Capture and validate bounded conditional authorization so Granoflow Task Work can continue unattended without letting the agent authorize itself.
---

# Granoflow Delegated Authorization

Use when a user wants one or more Granoflow tasks to continue while they are away or wants fewer repeated phase confirmations. The skill previews a machine-readable envelope containing separate phase grants, scope, expiry, allowed actions, forbidden actions, and invalidation rules; after explicit confirmation, hosts validate it at each gate and either continue or enter the existing visible waiting workflow.

Read `granoflow-agent-workflow/unattended-interaction-contract.md` first. A
direct user instruction for one bounded same-run completion uses that contract
without an envelope round trip. This skill owns the durable path when the grant
must survive an unattended interval, process restart, or later host turn.

## Keyword

- `#delegated-authorization`
- `#unattended-task-work`

## When to use

- Use when the user says they will be away, asks the agent not to wait at every phase, or requests automatic continuation for bounded Granoflow tasks.
- Use when a host reaches an Analysis, Planning, Plan confirmation, or Execution gate and a delegated envelope may already exist.
- Do not use a task tag, preference, prior behavior, or inferred urgency as authorization.
- A user-origin `gf做 <bounded target>` under the previously approved
  `gf-local-safe-v1` profile is a direct conditional command, not an
  agent-authored delegated envelope. Use this skill only when that grant must
  remain durable across an unattended interval or later host turn.

## Example requests

- 我离开一小时，这两个任务在 Grill 通过且不扩范围时自动继续。
- 减少确认：只允许改这两个仓库的列出文件和跑本地测试，发布和删除仍然问我。

## Workflow

### 1. Classify the authorization request

Distinguish explicit conditional delegation from urgency, eligibility, or inferred consent.

Actions:

- Identify the exact task IDs, requested unattended interval, phase grants, local actions, repositories, and exclusions.
- Reject inferred authorization and route non-delegable actions to explicit waiting.
  Success criteria:
- Every proposed grant maps to an explicit user statement.
- No tag, preference, or absence signal is treated as permission.
  Checkpoints:
- Stop if task scope or forbidden external effects are ambiguous.
  Artifacts:
- authorization intent ledger
- delegable and non-delegable action split
  Rules:
- The skill invocation itself is never an authorization grant.

### 2. Preview and confirm the envelope

Render all independent grants and constraints in one reviewable preview before durable write.

Actions:

- Create a granoflow_delegated_authorization_v1 envelope with id, issuedAt, expiresAt, sourceRef, taskIds, phase grants, allowed repos/paths/actions, forbidden actions, and invalidation rules.
- Show the complete preview and obtain one explicit confirmation that names the envelope or clearly approves all displayed grants.
  Success criteria:
- The user can see every automatic continuation and every excluded action.
- Each phase grant remains separately readable and auditable.
  Checkpoints:
- Do not write or consume the envelope before explicit confirmation.
  Artifacts:
- authorization envelope preview
- confirmed envelope
  Rules:
- One reply may issue several explicit grants; no grant may be implied by another.

### 3. Validate at each phase gate

Use deterministic current facts to decide whether the confirmed delegation still applies.

Actions:

- Read the newest task state, active Work Document, revocation nodes, envelope, grill statuses, plan facts, requested actions, repos, and paths.
- Run the validator and record phase, plan hash when available, decision, reason code, and evaluated scope.
  Success criteria:
- Allowed is returned only when every declared condition matches and no invalidation condition is present.
- The evaluation can be reproduced from the envelope and structured gate facts.
  Checkpoints:
- Unknown action, unknown field, stale state, failed grill, unresolved decision, expiry, revocation, or scope drift fails closed.
  Artifacts:
- authorization evaluation
- plan hash binding
- stable reason code
  Rules:
- The validator checks scope; it does not authenticate a person or make subjective product decisions.

### 4. Continue or enter visible waiting

Avoid silent idle time while preserving an explicit fallback for invalid or missing delegation.

Actions:

- On allowed, record the delegated phase authorization and continue only the approved actions.
- On denied or unavailable, execute the existing waiting node, near reminder, notification task, readback, and visibility classification workflow.
  Success criteria:
- Valid bounded work continues without another chat round trip.
- Invalid or missing delegation is visible in Granoflow and never becomes silent self-authorization.
  Checkpoints:
- Any newly requested external or destructive action re-enters explicit authorization regardless of envelope.
  Artifacts:
- continued Task Work phase or waiting node
- reminder and notification evidence when blocked
  Rules:
- A denied evaluation is not task failure; continue all independent safe work before waiting.

## Rules

- [must] Record analysis_confirmation, planning_permission, plan_confirmation, and execution_authorization as separate grants even when one user reply issues all of them.
- [must] Require explicit task or batch scope, absolute expiry, allowed actions, forbidden actions, repositories or paths, invalidation conditions, and a user-origin source reference.
- [must] Validate with deterministic structured facts and fail closed on unknown actions, expiry, revocation, scope drift, unresolved decisions, or failed grills.
- [must] When no valid envelope exists, invoke the existing waiting node, reminder, notification task, and readback workflow instead of silently pausing in chat.
- [must_not] Never infer authorization from tags, urgency, user absence, historical preferences, task descriptions, or the skill invocation itself.
- [must_not] Never delegate publish, push, payment, login, secrets or 2FA, external messages, destructive deletion, approved-asset overwrite, or scope expansion.
- [must] Treat `gf-local-safe-v1` as a fixed direct-command profile: require one
  unambiguous target, explicitly declared allowlisted actions, both passing
  Grills, confirmed Planning, zero unresolved decisions, and no scope drift.
  Missing or unknown actions fail closed.

## References

- Read [authorization-envelope.md](references/authorization-envelope.md) when drafting, confirming, validating, revoking, or auditing delegated authorization.
- Read [host-routing-and-waiting.md](references/host-routing-and-waiting.md) when a host detects unattended intent, reaches a phase gate, or receives a deny result.
- Read `granoflow-agent-workflow/unattended-interaction-contract.md` before any
  unattended user-facing question or phase confirmation.

## Success Criteria

- The workflow preserves preview -> confirm -> write as a hard gate.
- Every major step leaves a machine-readable artifact or validation result.
- Forward-test can be rerun from a fixed fixture without modifying the live skill directory.
