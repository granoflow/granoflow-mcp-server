# Authorization Envelope Contract

Read this file when drafting, confirming, validating, revoking, or auditing
delegated authorization.

## Durable Ownership

The controller Granoflow Task owns the only full envelope body in its active,
hash-verified Task Work attachment. The envelope uses
`receiptPolicy: app_readback_external`; it does not contain its own attachment
id or SHA-256 because that would be a self-referential hash.

After upload, the App readback forms a receipt:

```json
{
  "envelopeId": "gfda-...",
  "authorizationOwnerTaskId": "...",
  "attachmentId": "...",
  "attachmentSha256": "..."
}
```

Each target Task Work stores this receipt, not a copy of the envelope. Before
every gate, the host reads that attachment again, verifies the App-owned hash,
checks current target nodes for revocation or changed instructions, and only
then sets `receiptVerified: true`.

## Envelope Schema

`granoflow_delegated_authorization_v1` is a strict JSON object. Unknown fields
fail as `invalid_schema`. Required fields are:

- identity: `schema`, `status=confirmed`, `envelopeId`,
  `authorizationOwnerTaskId`, `receiptPolicy`, `sourceRef`;
- time: offset-aware `issuedAt` and absolute `expiresAt`;
- task/phase: `taskIds` and four independent `phaseGrants`;
- Plan: one absolute path and lowercase SHA-256 binding for every task;
- scope: absolute `allowedRepos`, repo-relative `allowedPathGlobs`, and
  `allowedActions`;
- safety: complete `forbiddenActions`, `requiredGateFacts`, and explicit
  `invalidationConditions`.

The four grant keys are `analysisConfirmation`, `planningPermission`,
`planConfirmation`, and `executionAuthorization`. One user reply may grant all
four, but no grant implies another.

Path globs cannot be absolute, escape with `..`, or use an unrestricted `**`.
Allowed suffix forms such as `docs-temp/**` remain bounded to their declared
repository prefix.

## Gate Facts

The validator consumes a separate strict facts object:

- `host`, `taskId`, `phase`, offset-aware `now`, and `planHash` after Planning;
- `repo`, repo-relative `paths`, and `requestedActions`;
- `analysisGrillPassed`, `planningConfirmed`, `readinessGrillPassed`;
- `unresolvedDecisionCount`, `scopeEscalated`, `revoked`, `stateFresh`, and
  `receiptVerified`.

The host owns current App reads and receipt verification. The validator owns
only deterministic comparison; it does not authenticate a user, query the App,
or decide subjective scope.

## Stable Result And Reasons

Every policy result contains `decision`, `envelopeId`, `phase`, optional
`planHash`, `reasonCode`, and `evaluatedScope`. An ordinary denial exits normally
so every host can route the reason without parsing stderr.

Allowed uses `decision=allowed` and `reasonCode=ok`. Denials include:

- `invalid_schema`, `expired`, `revoked`, `phase_not_granted`;
- `gate_not_passed`, `unresolved_decision`, `stale_state`;
- `repo_not_allowed`, `path_not_allowed`, `action_not_allowed`;
- `unknown_action`, `forbidden_action`, and `scope_drift`.

Unknown state always fails closed. Plan hash mismatch, a new repo/path, or
`scopeEscalated=true` is scope drift, not a reason to rewrite the envelope on the
agent's own authority.

## Non-delegable Actions

Every valid envelope keeps deletion outside the versioned Plan, user-data
deletion, approved-asset overwrite, git commit/push, publish/deploy, login,
payment, secret/2FA access, and external messages in `forbiddenActions`.
Creating or invoking this skill never changes that boundary.
