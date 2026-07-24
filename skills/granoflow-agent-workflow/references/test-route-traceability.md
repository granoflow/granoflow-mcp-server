# Test Route Traceability

Read this reference during Task Analysis/Test Plan and before Integration or
E2E campaign orchestration.

## Contract

Emit `granoflow_test_route_traceability_v1` and bind:

`source fact → journey step → task requirement → acceptance → test layer → evidence`

Each row records:

- `route_id`, `journey_id`, `step_ids`, and `source_fact_ids`;
- `requirement_refs` and `acceptance_refs`;
- `test_layer`: `unit`, `integration`, or `e2e`;
- `path_kind`: `service_path`, `component_path`, `human_path`, or
  `os_capability`;
- test path, assertions, evidence, doubles policy, and status;
- visible entry/result and selected host ids for E2E;
- E2E scope, navigation method, bypassed steps, and ordered interaction
  evidence for every covered visible step;
- covered failure modes for platform-boundary unit routes.

The Project Work step's `required_test_layers` is authoritative. Do not force
all three layers when the step declares fewer. Every declared layer must have a
covered route.

## Fidelity rules

- A service path cannot close E2E or a user-visible human path.
- Integration uses `service_path` for service collaboration and
  `component_path` when a real component and its state owner must be exercised
  around a controllable external adapter.
- A human path belongs to E2E and starts from a named visible entry.
- An OS capability route uses real host evidence; mocks/test doubles cannot
  close it.
- Plugin/OS failure modes declared by the journey step must be covered by unit
  routes, including fallback and cancellation where applicable.
- `feature_e2e`, `journey_e2e`, and `full_project_e2e` are distinct. Only the
  final full-project campaign may claim complete user-path delivery.
- E2E navigation methods are `app_launch`, `visible_control`, `os_control`,
  `direct_url`, `deep_link`, `direct_route`, or `state_injection`.
- `full_project_e2e` accepts only the first three. Every covered step records
  its visible control, user action, before/after observation, and driver or host
  event reference in Project Work order. A screenshot is result evidence, not
  proof that the user action occurred.
- Feature/journey shortcuts declare `bypassed_step_ids`. A bypassed step cannot
  simultaneously be covered, and shortcut routes cannot claim
  `full_user_path`.

For every visible background activity, add
`background_activity_id` and execute this sequence:

1. Start the activity and observe that it started.
2. Observe a first background event from a state/event/host signal.
3. Operate one declared protected visible control.
4. Observe a second background event.
5. Prove the user's action still holds.
6. Invoke a declared exit action and prove the activity stopped.

A fixed wait is not event evidence. Calling an exit callback is not proof that
the activity ended. Visible activities require a `component_path` Integration
route and a selected-host `human_path` E2E route. Do not add an extra unit route
when there is no separately testable controller or reducer.

The ledger digest binds the current Project Work source-fact and journey-step
digests. An independent review must pass the current digest.

Lint with:

```bash
python3 skills/granoflow-agent-workflow/scripts/lint_test_route_traceability.py \
  task-work.yaml --project-work project-work.yaml
```

Campaign suite plans for traced Project Work set
`test_route_traceability_loaded: true` and list `journey_step_ids` per case.
