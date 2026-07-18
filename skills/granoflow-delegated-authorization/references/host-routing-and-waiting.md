# Host Routing And Waiting

Read this file when a host detects unattended intent, reaches a phase gate, or
receives a deny result.

Apply `granoflow-agent-workflow/unattended-interaction-contract.md` first. If a
direct current instruction covers the same active bounded run, use its
zero-interruption decision without materializing an envelope. Continue with the
durable gate routing below only when authorization must survive an unattended
interval, process restart, or later host turn.

## Gate Routing

1. Re-read the target Task, nodes, active Task Work, and authorization receipt.
2. Re-read the controller attachment by `attachmentId`; compare its App-owned
   SHA-256 with `attachmentSha256`.
3. Extract the confirmed envelope only when the receipt matches and there is no
   newer revocation or narrowed instruction.
4. Build strict current gate facts and run
   `scripts/validate_delegated_authorization.py`.
5. Record the phase, Plan hash, receipt, decision, reason, and evaluated scope in
   Task Work.

On `decision=allowed`, continue only the evaluated actions and paths. Re-evaluate
at the next phase gate. Never carry an allowed result across a changed Plan,
task revision, API outage, expiry, or new action.

On `decision=denied`, missing envelope, unreadable receipt, or unsupported old
host, use the existing `waiting-for-user-input` contract. Complete independent
safe nodes first, then:

- add and read back a waiting node with the stable reason code;
- set the original task reminder to current local time plus 3 minutes;
- read `granoflow-agent-workflow/task-authoring-quality-contract`, then create
  and read back a compliant notification task at plus 10 minutes;
- attempt sync only when the App says it is safe;
- report `synced_to_server`, `local_only`, or `unknown_remote_visibility` from
  evidence, never inference.

## Host Parity

Codex, Cursor, Claude, and OpenCode/OpenClaw pass the same JSON files to the same
validator and must receive the same decision. Package fixtures prove contract
parity; they are not evidence that a real installation smoke ran in every host.

## False Authorization Signals

Never treat any of these as a grant:

- the `GFMCP` tag or any other task tag;
- skill invocation, installation, or registry presence;
- user absence, urgency, due date, historical preference, or past approval;
- an agent-authored task description or envelope;
- a successful Grill or test by itself.

A direct current user instruction can authorize its explicit scope without an
envelope. The envelope exists to make one such instruction durable and
conditionally reusable; it does not weaken explicit authorization rules.

`gf做 <bounded target>` and `gf! <bounded target>` are direct current
instructions only when the fixed `gf-local-safe-v1` profile was previously
previewed and approved. The host must still apply the Orchestrator's allowlist,
target-resolution, Grill, unresolved-decision, and scope-drift checks. A bare or
ambiguous target, an undeclared action, or an unknown action is denied. If the
grant must survive an unattended interval or a later host turn, materialize and
validate the strict envelope instead of treating the shortcut as permanent
consent.
