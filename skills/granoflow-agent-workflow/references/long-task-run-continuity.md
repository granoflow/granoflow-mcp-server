# Long-Task Run Continuity

Single owner for **long-running agent work** that risks early loop cutoffs or
conversation summarization. Host agents differ (Cursor, Claude Code, Codex,
OpenCode, custom runners). This contract is **host-agnostic**: it never requires
a vendor product name.

## Mandatory Load

Load via MCP before starting a **long task** (see Triggers) or an **unattended**
implement / campaign run:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "long-task-run-continuity"
)
```

Skipping the load on a long or unattended implement run fails closed as
`long_task_continuity_unread`.

## Two Layers (do not conflate)

| Layer | Portable name                      | Required?                               | Purpose                                                                               |
| ----- | ---------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------- |
| A     | **Durable run plan**               | **Yes** for long / unattended implement | On-disk stages + next step + evidence paths; survives summarization and host switches |
| B     | **Collaborative planning surface** | When the **host exposes** it            | Optional host UI/mode that helps structure work before/while executing                |

Layer B’s **local label** is host-specific and must not appear as a hard token in
skills. Examples of local labels (informative only, never required wording):

- some IDEs: “Plan” / “Plan mode”
- some CLIs: planning / architect subcommand
- some agents: “create a plan first” turn

Agents **Must** detect Layer B by **capability**, not by brand name:

```text
collaborative_planning_surface:
  availability: available | unavailable | unknown
  activation: host_native_switch | in_chat_structured_plan | none
  # optional note for logs only — never fail on the string:
  host_local_label: <free text or omit>
```

Rules:

1. Prefer activating Layer B when `availability: available` and the host allows
   switching without inventing unauthorized UI.
2. If Layer B is `unavailable` / `unknown`, **do not block**. Proceed with Layer
   A only.
3. User-facing text: say 「先写一份可续跑的执行计划」 / 「若当前工具有规划界面可一并打开」—
   not a requirement that names one vendor’s mode.

## Triggers (long task)

Treat as long when any of:

- user authorizes implement across a **milestone** or multiple tasks
  (e.g. 「开始实施」「开始实施 M1」);
- work clearly spans multiple Execution turns / many files;
- unattended implement / campaign for software milestones;
- prior turn was cut off by loop/summary limits and work remains.

Short single-file fixes are exempt unless unattended milestone implement applies.

## Durable Run Plan (Layer A) — hard

### Location

```text
temp/run-plan-<scope>-v<n>.md
```

Examples: `temp/run-plan-M1-implement-v1.md`,
`temp/run-plan-project-unattended-v1.md`.

Scope defaults to the active milestone key for milestone implement; use
`project` only for true cross-milestone unattended campaigns.

### Minimum contents

```yaml
---
doc_type: durable_run_plan
scope: M1 # or project
project_id: ""
status: active # active | paused | completed | superseded
interaction_mode: interactive | unattended
collaborative_planning_surface: available | unavailable | unknown
acceptance_pack_path: temp/milestone-plan-acceptance-M1-v1.md # when applicable
updated_at: <ISO8601>
---
```

Body **Must** include:

1. Goal (one short paragraph)
2. Ordered stages with status `pending | in_progress | done | blocked`
3. Current next step (single concrete action)
4. Evidence pointers (tests run, files touched, pack path)
5. Stop / pause conditions

Update the same file as stages complete. Bump `v<n>` only on material replans.

Fail closed:

- `long_run_plan_missing` — long/unattended implement without an active durable
  run plan file
- `long_run_plan_stale` — continuing after summary/cutoff without refreshing
  next step / stage status

## Collaborative Planning Surface (Layer B)

### Interactive

When Layer B is available, **request or enter** it at the start of a long task
(host-native switch or structured in-chat plan—whatever the host supports).
Still create Layer A in the same wave.

### Unattended

When the user declared unattended **and** Layer B is `available`, the host
**Must** activate it for the run (no asking whether to plan). When Layer B is
not available, unattended **Must** still create/update Layer A and continue
solvable work—never stall waiting for a missing host UI.

Asking the user solely to enable a host-local planning UI under unattended fails
closed as `collaborative_planning_surface_confirm_in_unattended`.

## Relationship

| Concern                                      | Owner                                |
| -------------------------------------------- | ------------------------------------ |
| Milestone Plan acceptance (design artifacts) | `milestone-plan-acceptance-pack.md`  |
| Per-task Plan Design Gate                    | `plan-design-gate.md`                |
| Surviving long agent loops / host variance   | **this file**                        |
| Plain-language gloss for users               | `workflow-jargon-plain-language.md`  |
| Unattended ask budget                        | `unattended-interaction-contract.md` |

## Admission Test

1. Was this reference loaded for a long or unattended implement run?
2. Does an active durable run plan exist and name the next step?
3. Was Layer B referenced only via availability, not a required vendor name?
4. Unattended + Layer B available → activated without an acknowledgement question?
