# Implementation Contract Semantic Replay

## When To Read

Read this reference after a UI implementation has a runnable build and before
Task Delivery. Do not load it during Project Definition, Analysis, or ordinary
non-UI work. Analysis owns product truth; this gate only proves that the
running implementation still realizes that truth.

## Responsibility

This reference owns runtime semantic coverage from the accepted Screen Content
Contract to the running App. It does not own:

- visual comparison, which remains in `prototype-implementation-fidelity` and
  rendered fidelity;
- file, method, class, data-structure, flow, or UML separation, which remains
  in `implementation-design-fidelity` and `software-structural-budget`;
- product redefinition, which must reopen Analysis;
- build, screenshot, device, or App orchestration inside the MCP server.

The host runs the application and captures evidence. The MCP skill records and
validates evidence without adding App APIs or execution tools.

## Required Order

1. Read back the accepted platform matrix, Content Contract, Prototype Bundle,
   prototype semantic review, and Analysis Technical Package SHA values.
2. Confirm the current `execution_authorization` and user-facing `run` receipt.
3. Reconcile the implementation with the Structural Change Forecast and pass
   Implementation Design Fidelity. `modular_split: needs_split` blocks here.
4. Produce a runnable build and a current implementation snapshot.
5. Generate the minimum complete runtime target set.
6. Exercise every contract element on every runtime target and capture
   deterministic evidence.
7. Run the linter, an independent AI semantic reviewer, and an independent
   Final Verifier.
8. Run rendered visual fidelity. The gates may share screenshot artifacts but
   never share or infer status.
9. Only then may Task Delivery proceed.

## Implementation Snapshot

Use `granoflow_implementation_snapshot_v1`:

```yaml
schema: granoflow_implementation_snapshot_v1
files:
  - path: lib/features/example/view.dart
    sha256: ""
build_ref: ""
build_sha256: ""
snapshot_sha256: ""
```

Paths are unique, sorted, normalized relative POSIX paths. Include every
in-scope source, resource, generated contract input, and build configuration
that can change delivered behavior. The digest is canonical JSON with
recursive key sorting and excludes `snapshot_sha256`.

## Replay Contract

Use `granoflow_implementation_contract_semantic_replay_v1`:

```yaml
schema: granoflow_implementation_contract_semantic_replay_v1
applicability: required
implementation_author_id: ""
platform_matrix_sha256: ""
content_contract_sha256: ""
prototype_bundle_sha256: ""
prototype_semantic_review_sha256: ""
technical_package_sha256: ""
implementation_snapshot_sha256: ""
preconditions:
  app_readback_status: verified
  execution_authorization_status: valid
  run_status: valid
  implementation_design_fidelity_status: complete
  runnable_build_status: passed
runtime_targets:
  - id: ""
    platform_id: ""
    layout_family_id: ""
    test_version: ""
    device_class: ""
    runtime_artifact_ref: ""
    runtime_artifact_sha256: ""
rows:
  - contract_element_ref: ""
    runtime_target_id: ""
    runtime_binding: { kind: dom, ref: "" }
    capture_ref: ""
    capture_sha256: ""
    status: verified
deterministic_runtime:
  status: passed
  runtime_target_ids: []
  evidence_refs: []
open_blockers: []
authorization_effect: none
ai_semantic_review:
  reviewer_id: ""
  status: passed
  evidence_refs: []
  reviewed_replay_sha256: ""
final_verifier:
  verifier_id: ""
  status: passed
  evidence_refs: []
  verified_replay_sha256: ""
status: passed
replay_sha256: ""
```

For non-UI backend or documentation work, use `applicability:
not_applicable`, a `task_type` of `backend`, `documentation`, or
`non_ui_software`, and a concrete `rationale`. Historical completion alone is
not an exemption for reopened UI work.

## Runtime Coverage

Build the smallest target set that covers:

- every supported platform and each required layout family at least once;
- every supported platform and each required test version at least once.

Each target uses a declared device class. Extra targets are allowed; a full
Cartesian product is not required.

For every target, cover every canonical element emitted by the Screen Content
Contract:

- `screen:*` and ordinary elements require a runtime binding and capture;
- `action:*` and `navigation:*` additionally require interaction evidence;
- `state:*` and `permission:*` additionally require state capture;
- `field:*` and `data_source:*` additionally require data evidence.

Binding kinds are `dom`, `accessibility`, `test_id`, and `native_semantics`.
When Web HTML is supplied to the linter, each `dom` binding must have a matching
`data-contract-ref`.

`approved_platform_exception` is allowed only with `platform_exception_ref`,
`approved_exception_evidence_ref`, and a rationale. It does not permit an
undeclared product difference.

## Review And Digest

The implementation author, AI semantic reviewer, and Final Verifier must be
distinct. Both reviewers bind the current Replay digest and provide evidence.
The digest excludes `replay_sha256`, `status`, `ai_semantic_review`, and
`final_verifier`.

Any changed source digest, implementation snapshot, runtime target, binding,
capture, or evidence invalidates the old review. Open blockers, failed
deterministic runtime, failed reviewers, or `authorization_effect` other than
`none` block Delivery.

Run:

```bash
python3 skills/granoflow-agent-workflow/scripts/lint_implementation_contract_semantic_replay.py \
  replay.yaml \
  --platform-matrix platform.yaml \
  --content-contract content.yaml \
  --prototype-bundle bundle.yaml \
  --prototype-semantic-review semantic.yaml \
  --technical-package technical.yaml \
  --implementation-snapshot snapshot.yaml
```

For Web evidence, append
`--html runtime_target_id=/absolute/path/to/runtime.html`.

## Change Return

- Implementation defect: revise code, rebuild, regenerate the snapshot, and
  replay again.
- Product behavior defect: reopen Analysis through change-impact fanout before
  implementation resumes.
- New physical or responsibility boundary: update Planning and the Structural
  Change Forecast before continuing.
- A material failed replay or changed remediation method must also append a
  factual event under `implementation-learning-ledger.md`; a later passing
  replay does not erase it.
- `grill-me` and visual `design-review` never substitute for this proof.

## Fail-Closed Codes

- `implementation_contract_replay_required`
- `implementation_contract_source_digest_mismatch`
- `implementation_contract_target_coverage_missing`
- `implementation_contract_element_missing`
- `implementation_contract_interaction_failed`
- `implementation_contract_state_unverified`
- `implementation_contract_data_binding_unverified`
- `implementation_contract_runtime_failed`
- `implementation_contract_ai_failed`
- `implementation_contract_verifier_failed`
- `implementation_contract_open_blockers`
- `implementation_contract_replay_digest_mismatch`
- `implementation_contract_authorization_invalid`
