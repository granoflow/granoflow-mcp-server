# Implementation Learning Ledger

Read this reference during software implementation, Task Delivery, Deferred
Task Review, integration remediation, and E2E remediation. It owns the factual
record of material problems and better methods discovered by the implementing
AI. It does not replace Delivery, test evidence, Task Review, Experience, or a
Review Card.

## Purpose And Timing

The implementing AI may discover a wrong assumption, failed approach,
undocumented constraint, safer design, or reusable method that the user never
observes. Capture that learning when observable evidence exists, while the
task's active Task Work `execution` slot is still current. Do not wait for the
user to notice or for a later test campaign to reconstruct it from memory.

The ledger is implementation evidence, not a retrospective. Task Review may
consume it only after the task is complete. Integration and E2E remediation may
append later events and trigger a new Task Review revision.

## Materiality Gate

Record a `material` event when at least one is true:

- a build, test, static gate, runtime check, or contract replay failed and the
  resolution changed code, design, configuration, test coverage, or method;
- an authorized implementation approach was abandoned for a substantively
  different approach after observable evidence showed it was unsuitable;
- implementation exposed an incorrect Analysis, Planning, API, dependency,
  platform, data, permission, or responsibility assumption;
- the AI required two or more substantively different attempts and the
  successful method provides a useful future decision rule;
- a workaround, architecture correction, responsibility split, new guard, or
  new reusable technique was required;
- integration, E2E, or user acceptance found a material defect that required
  remediation after task completion.

Classify an event as `incidental` and omit it from the persisted ledger when it
is only a typo, formatting repair, expected red phase of a planned test,
one-off retry, routine compiler guidance, or action that changed no decision
and produced no reusable lesson.

The test is: could this event change how a future similar task is analyzed,
implemented, or verified? If not, it is execution noise.

## Persisted Contract

Store this nested record in the active Task Work `execution` slot:

```yaml
implementation_learning_ledger:
  schema: granoflow_implementation_learning_ledger_v1
  task_id: ""
  source_work_document_sha256: ""
  events:
    - event_id: ""
      observed_phase: implementation | integration_test | e2e_test | user_acceptance
      observed_at: ""
      trigger: test_failure | build_failure | static_gate_failure | runtime_failure | wrong_assumption | abandoned_approach | unexpected_constraint | architecture_correction | tool_or_environment_issue | better_method_discovered
      attempted_approach: ""
      observable_problem: ""
      evidence_refs: []
      root_cause: ""
      replacement_method: ""
      why_replacement_worked: ""
      validation_evidence_refs: []
      reusable_when: ""
      boundary_or_exception: ""
      materiality: material
      review_status: pending | included_in_review | not_reusable
      task_review_revision: null
  material_event_count: 0
  review_eligibility: not_required | required | included_in_review
  ledger_sha256: ""
```

Use canonical JSON with recursively sorted keys to calculate `ledger_sha256`,
excluding that field itself. Event ids are stable across retries. Correct an
event in place before Delivery; after completion, append a correction event or
use the existing post-completion revision path rather than erasing history.

## Evidence And Privacy

Persist only observable engineering facts:

- the attempted external action or implementation choice;
- the failure symptom and bounded evidence reference;
- the supported root-cause conclusion;
- the replacement method and validation evidence;
- the future trigger and applicability boundary.

Never persist hidden chain-of-thought, private scratch reasoning, raw
transcripts, complete terminal logs, secrets, credentials, auth URLs, or
unfiltered tool output. A concise evidence reference and factual conclusion are
enough.

## Delivery Reconciliation

Before Task Delivery:

1. Re-read failed commands, failed gates, changed plans, reopened nodes,
   contract-return paths, and implementation deviations.
2. Confirm every material event has one ledger row with failure and validation
   evidence.
3. Merge repeated symptoms that share one cause and replacement method.
4. Set `review_eligibility: required` when any material event can improve a
   future decision or method. Use `not_required` only when no material event
   remains.
5. Bind Delivery to the exact `ledger_sha256` and report the eligibility
   decision. Delivery records what happened; it does not write Task Review.

A successful final build or green test does not erase earlier material
learning.

## Deferred Review Handoff

After task completion, `review_eligibility: required` automatically creates a
Deferred Task Review candidate even when the user did not observe the issue or
request a review. The candidate must:

- summarize material events by cause and successful method, not command order;
- preserve failed approaches only when they explain a future decision;
- include validation and applicability boundaries;
- set included events to `included_in_review` with the written review revision;
- leave Card, Experience, and project-rule promotion to their existing
  independent gates.

The factual ledger persists even when the Review write awaits confirmation. An
unattended agent must not silently discard the candidate or claim user
acceptance.

Integration, E2E, and user-acceptance remediation append events to the same
logical ledger and revise Task Review after the affected task is green. A clean
first pass creates test evidence but no learning event and no Task Review
requirement.

## Fail-Closed Codes

- `implementation_learning_ledger_required`
- `implementation_learning_material_event_missing`
- `implementation_learning_evidence_missing`
- `implementation_learning_validation_missing`
- `implementation_learning_delivery_unreconciled`
- `implementation_learning_review_pending`
- `implementation_learning_digest_mismatch`
- `implementation_learning_hidden_reasoning_forbidden`
- `implementation_learning_incidental_noise_forbidden`
