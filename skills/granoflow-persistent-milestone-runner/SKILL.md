---
name: granoflow-persistent-milestone-runner
description: Persistently run one Granoflow milestone with provider-neutral workers, bounded leases, progress checkpoints, anti-livelock handling, interaction waits, and evidence-gated completion.
---

# Granoflow Persistent Milestone Runner

Use this skill when one confirmed milestone may need to continue for hours or days without treating one Agent process, one chat turn, or one summary as the lifetime of the work.

## Keyword

- `#persistent-milestone-runner`
- `#milestone-runner`
- `#unattended-milestone`

## Core Contract

- Granoflow App/API owns milestone, task, node, attachment, and completion truth.
- The optional runner is an external process. It never creates an in-process MCP timer or a parallel task database.
- Each worker is finite. Durable lease, heartbeat, checkpoint, and attempt state let another worker resume after exit or crash.
- A worker command is supplied by the host or a user Skill. This public skill does not choose a provider, model, or model-escalation ladder.
- Worker exit code, final text, summary, or self-reported `complete` is progress evidence only. Acceptance requires App/API readback, an accepted content/hash-readable Task Delivery, and finished nodes when present.
- Repeated attempts without new evidence move to `replan_required`; one further stagnant attempt moves to a visible, resumable interaction wait. Other eligible tasks continue.

## Thread Execution Modes

The thread reports its mode before execution. An agent does not infer routing
from a self-reported model name or reasoning tier; the user or host configuration
owns model selection.

- `interactive` is the default when the user did not choose a mode. The thread
  works normally and does not need to predeclare node lanes.
- `unattended` is explicit. The thread declares its allowed node lanes, actions,
  stop conditions, and handoff. Ordinary `[confirm]` nodes are skipped, while
  `[action]` nodes for login, payment, publish, deployment, secrets, destructive
  changes, or external communication remain real interaction boundaries.
  Local device capability inventory does not become a mandatory test matrix:
  when the project supports the current development platform, unattended test
  nodes target only that platform. When it does not, the worker deterministically
  selects one already-available supported official simulator/emulator, falling
  back to an installed E2E-capable third-party VM. It never installs a new VM
  stack or image.
- `layered_handoff` is explicit. Each worker declares one or more capability
  lanes such as `[plan]`, `[dev]`, or `[test]`. It may claim only the first
  unfinished matching node after every preceding required node is finished.

`[dev]` includes implementation, unit tests, static gates, and preparation plus
static/code validation of integration or screenshot scripts. `[test]` means a
later task actually runs those scripts and records runtime evidence. A task does
not need `[test]` when integration or screenshot execution is not required.

## Authorization Before Run

Resolve project defaults once with `granoflow_agent_preferences_get(projectId)`
before selecting the execution mode or Git checkpoint policy. The runner may
consume those values, but preferences never create authorization and never
weaken task, test, Delivery, secret, destructive-action, or acceptance gates.

Every non-dry run requires a confirmed `granoflow_milestone_authorization_v1` manifest. It records full-runtime-access readiness, internal phase preauthorization, every required external capability as `granted`, `excluded`, or `interaction_required`, credential references, expiry, and a reference-only secret policy. It never contains secret values.

An updated manifest or a changed Granoflow task releases the applicable wait on the next cycle. The runner consumes authorization; it never writes or confirms its own grant.

Checkpoints:

- Resolve `granoflow_agent_preferences_get(projectId)` once before mode selection.
- Preferences never create authorization or weaken acceptance gates.
- Non-dry run without confirmed manifest → stop before worker launch.
- Runner never writes or confirms its own authorization grant.

## Run

Preview one milestone without executing a worker:

```bash
granoflow-persistent-milestone-runner \
  --milestone-id <id> \
  --dry-run --once
```

Run continuously with a host-supplied worker:

```bash
granoflow-persistent-milestone-runner \
  --milestone-id <id> \
  --authorization-manifest /private/path/authorization.json \
  --worker-command '<agent command>' \
  --workspace /absolute/project/path
```

Run one unattended local worker responsible for normal automated lanes:

```bash
granoflow-persistent-milestone-runner \
  --milestone-id <id> \
  --execution-mode unattended \
  --authorization-manifest /private/path/authorization.json \
  --worker-command '<agent command>' \
  --workspace /absolute/project/path
```

Run one worker in a layered handoff (repeat `--lane` for multiple lanes):

```bash
granoflow-persistent-milestone-runner \
  --milestone-id <id> \
  --execution-mode layered_handoff \
  --lane dev \
  --authorization-manifest /private/path/authorization.json \
  --worker-command '<low-cost coding agent command>' \
  --workspace /absolute/project/path
```

Generate the always-present acceptance report after implementation gates. The
manifest explicitly marks integration and screenshot evidence as `passed`,
`failed`, `planned_not_run`, or `not_required`; `not_required` still needs a
reason. Key screenshots are embedded into the HTML, while absent screenshots
produce a complete text-only report.

```bash
python3 skills/granoflow-persistent-milestone-runner/scripts/acceptance_report.py \
  --manifest /absolute/path/acceptance-report.json \
  --output /absolute/path/acceptance-report.html
```

The worker command must accept the generated task packet as its final argument. It may optionally write the structured report described in [worker-report.md](references/worker-report.md). A missing report never weakens the App/API completion gate.

Checkpoints:

- Dry-run (`--dry-run --once`) previews milestone without executing a worker.
- Worker exit or self-reported `complete` is progress evidence only—not acceptance.
- Stagnation → `replan_required`, then visible interaction wait; independent tasks continue.
- Acceptance requires App/API readback, accepted Task Delivery, and finished nodes.
- Generate acceptance HTML even when integration/screenshot tests are `not_required`.

## Rules

- [must] Continue until all milestone tasks are evidence-accepted, explicitly excluded through the confirmed charter, waiting on a visible interaction, cancelled, or proven impossible to continue safely.
- [must] Keep attempt history bounded and store only ids, hashes, enums, timestamps, and stable reason codes.
- [must] Let a changed task or authorization manifest resume from the saved task/node entry point.
- [must] Keep user-facing progress snapshots distinct from completion summaries.
- [must] Produce an acceptance HTML even when integration and screenshot tests are not required.
- [must] Keep non-selected supported platforms as `tested: false` external-device
  handoffs. A later user reply equivalent to “知道了” acknowledges the handoff
  and may complete acceptance, but never converts it to tested evidence.
- [must] Preserve only key screenshots and summarize code, database, workflow, and verification changes.
- [must_not] Never repeat an unchanged failed strategy indefinitely.
- [must_not] Never persist tokens, passwords, OTPs, recovery codes, auth URLs, private keys, or raw worker transcripts.
- [must_not] Never let a user extension weaken authorization, secret, destructive-action, or acceptance gates.

## References

- Read [runtime-contract.md](references/runtime-contract.md) before operating or diagnosing the runner.
- Read [authorization-manifest.md](references/authorization-manifest.md) before creating or updating the milestone authorization manifest.
- Read [worker-report.md](references/worker-report.md) before integrating a worker command or user routing Skill.
- Read [acceptance-report-manifest.md](references/acceptance-report-manifest.md)
  before generating the final acceptance HTML.

## Success Criteria

- A crashed or exited worker can be replaced after lease expiry without losing the task checkpoint.
- Premature summaries do not complete tasks.
- Stagnation becomes replan, then visible interaction, while independent tasks remain runnable.
- The public contract remains provider-neutral and supports user Skill overrides through the worker command/report interface.
