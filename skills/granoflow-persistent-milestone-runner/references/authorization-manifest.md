# Milestone Authorization Manifest

`granoflow_milestone_authorization_v1` is a user-confirmed, reference-only JSON manifest consumed by the runner on every cycle.

Required fields:

- `schema`, `status=confirmed`, `milestoneId`, offset-aware `issuedAt` and `expiresAt`;
- `runtimeAccess.required=full` and `runtimeAccess.observed=full`;
- `autoConfirmInternalGates=true` for already confirmed in-scope phase gates;
- `requiredExternalCapabilities`, plus one exact entry per required name in `externalCapabilities`;
- each capability has `disposition=granted|excluded|interaction_required`, bounded `taskIds`, and a credential reference only when granted;
- `secretPolicy.referenceOnly=true` and `secretPolicy.persistValues=false`.

The manifest does not authenticate a platform account. `granted` means the user authorized the named action and a usable external credential reference is expected; the worker still verifies live platform readiness. `excluded` removes that delivery surface from the confirmed milestone. `interaction_required` creates or preserves a resumable interaction node.

### Early inventory alignment (unattended)

Under explicit unattended, populate `requiredExternalCapabilities` /
`externalCapabilities` from the **External Capability Inventory** in
`unattended-interaction-contract` **before** deep milestone worker loops when
the classes are knowable from docs/Project Work. Prefer one early batch of
`granted` / `excluded` / `interaction_required` over mid-run surprises.

If a capability becomes visible only from implementation evidence later:

- add or update the manifest entry (`interaction_required` or keep `excluded`
  with new evidence);
- park the dependent work in `deferred_external_work`;
- **do not** stall unrelated tasks—schedule residual handling toward the end of
  the solvable queue (see unattended contract **Late discovery**).

Updating authorization changes the manifest fingerprint. The runner revalidates it next cycle and may resume a waiting task without interrupting an unrelated worker already inside an atomic action.

Never put a token, password, OTP, recovery code, auth URL, private key, or cookie in this manifest. Prefer platform CLI auth, OS credential stores, or a project-approved ignored private file; record only its reference.
