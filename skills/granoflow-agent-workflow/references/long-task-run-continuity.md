# Long-Task Run Continuity

Single owner for **long-running agent work** that risks early loop cutoffs or
conversation summarization. Host agents differ (Cursor, Claude Code, Codex,
OpenCode, custom runners). This contract is **host-agnostic**: it never requires
a vendor product name as a hard token.

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

## Three Layers For Unattended Completion (do not conflate)

A host wake / recurring-tick mechanism can be robust and still fail to finish a
Granoflow project. Unattended full-pipeline completion needs **all three**:

| Layer | Portable name                      | Solves                       | Does **not** solve                            |
| ----- | ---------------------------------- | ---------------------------- | --------------------------------------------- |
| Auth  | Unattended interaction contract    | Do not ask; defer external   | What to resume after cutoff; when to wake     |
| A     | **Durable run plan / Project SoT** | **What** to resume next      | Waking the agent; ask-budget                  |
| B     | **Collaborative planning surface** | Optional host planning UI    | Continuity if unavailable                     |
| C     | **Host wake surface**              | **When** the agent re-enters | Phase truth, ask-budget, or next-step content |

Mnemonic: **wake re-enters; unattended avoids questions; durable plan names the
next step.** Satisfying only Layer C (host wake / loop) is necessary but not
sufficient for project → delivery.

Ask-budget and residual rules stay in `unattended-interaction-contract.md`.
This file owns Layers A–C continuity mechanics.

## Continuity Surfaces (Layers A / B / C)

| Layer | Portable name                      | Required?                                        | Purpose                                                                                                   |
| ----- | ---------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| A     | **Project SoT** (durable run plan) | **Yes** for long / unattended project runs       | `temp/project-sot.yaml`: stages + coarse work_items + next_step; survives summarization; regen if missing |
| B     | **Collaborative planning surface** | When the **host exposes** it                     | Optional host UI/mode that helps structure work before/while executing                                    |
| C     | **Host wake surface**              | When the **host exposes** it for long unattended | Recurring / event wake so work continues after turn cutoff or idle without a human 「继续」               |

Layer B / C **local labels** are host-specific and must not appear as hard tokens
in skills. Examples of local labels (informative only, never required wording):

- some IDEs: “Plan” / “Plan mode”; recurring `/loop` or monitored-shell ticks
- some CLIs: planning / architect subcommand; cron / heartbeat `--once`
- some agents: “create a plan first” turn; external worker pollers

**Do not** equate chat-session host wake (Layer C) with `granoflow-gfmcp-runner`
or other out-of-band task workers—they are different host paths that may share
the same Layer A file format.

Agents **Must** detect Layer B / C by **capability**, not by brand name:

```text
collaborative_planning_surface:
  availability: available | unavailable | unknown
  activation: host_native_switch | in_chat_structured_plan | none
  # optional note for logs only — never fail on the string:
  host_local_label: <free text or omit>

host_wake_surface:
  availability: available | unavailable | unknown
  kind: interval_tick | event_watcher | external_runner | none
  # optional note for logs only — never fail on the string:
  host_local_label: <free text or omit>
  # required when arming a wake while Layer A is active:
  bound_run_plan_path: temp/project-sot.yaml
```

Rules:

1. Prefer activating Layer B when `availability: available` and the host allows
   switching without inventing unauthorized UI.
2. If Layer B is `unavailable` / `unknown`, **do not block**. Proceed with Layer
   A only.
3. When Layer C is `available` for a long / unattended run that may hit turn
   cutoff or idle stop, **arm wake bound to Layer A** (see Host Wake Tick
   Protocol). If Layer C is `unavailable` / `unknown`, **do not block**—keep
   advancing Layer A in the current turn and emit a notice that human 「继续」
   or an external runner may be needed after cutoff.
4. User-facing text: say 「先写一份可续跑的执行计划」 / 「若当前工具有规划界面可一并打开」 /
   「若当前工具支持定时唤醒，会按执行计划下一步续跑」— not a requirement that
   names one vendor’s mode.

## Triggers (long task)

Treat as long when any of:

- user authorizes implement across a **milestone** or multiple tasks
  (e.g. 「开始实施」「开始实施 M1」);
- work clearly spans multiple Execution turns / many files;
- unattended implement / campaign for software milestones;
- prior turn was cut off by loop/summary limits and work remains;
- a host wake tick fires while an active durable run plan still has solvable
  next steps (resume via Host Wake Tick Protocol—do not re-derive the project
  from chat alone).

Short single-file fixes are exempt unless unattended milestone implement applies.

## Durable Run Plan (Layer A) — hard

For **project-bound** long / unattended runs, Layer A **is** the **Project SoT**.
Do not maintain a second parallel `temp/run-plan-*.md` format.

### Location

```text
temp/project-sot.yaml
```

Owner skill: `granoflow-project-sot` (`referenceId: project-sot`). Skeleton:
`skills/granoflow-project-sot/references/project-sot-template.yaml`.
Create after `project_init` done; expand after `milestones_created`; lint with
`lint_project_sot.py`.

If `temp/project-sot.yaml` is missing (or `temp/` wiped), **regen before continue**:

```text
python3 skills/granoflow-project-sot/scripts/regen_project_sot_from_app.py \
  --project-id <uuid> --repo-root <path> --force --migrate-legacy
```

Skipping regen when required → `project_sot_missing`.

Before each long/unattended resume (host wake tick or new Agent turn after
cutoff): App-readback current Project Work (and any other non-empty
`source_digests` keys), fill `source_digest_verification`, then:

```text
python3 skills/granoflow-project-sot/scripts/lint_project_sot.py \
  temp/project-sot.yaml --require-digest-match
```

Mismatch or missing verification → `project_sot_stale` (do not continue on
a stale digest). Legacy alias: `project_e2e_sot_stale`.

Also load:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-project-sot",
  referenceId: "project-sot"
)
```

### Minimum contents

Follow `granoflow-project-sot` / `project-sot`: eight lifecycle `stages`,
coarse `work_items` (task 3.1/3.2, milestone pack + implement, project
campaigns), and a single `next_step`. Skill-internal details stay out of the
file.

Legacy alias: `long_run_plan_missing` / `long_run_plan_stale` still apply when
the SoT file is absent or its `next_step` / stage rows were not refreshed after
cutoff. Prefer the `project_sot_*` codes when linting the SoT document
(`project_e2e_sot_*` remains a legacy alias).

Fail closed:

- `long_run_plan_missing` / `project_sot_missing` — long/unattended project
  run without an active SoT file (regen first if wiped)
- `long_run_plan_stale` / `project_sot_stale` — continuing after
  summary/cutoff without refreshing `next_step` / statuses, or
  `--require-digest-match` failed against App readback
- `project_sot_*` — schema / affinity / pack-before-implement invariants
  (see `granoflow-project-sot` / `project-sot`)

## Unattended Entry Continuity Checklist (hard)

When the user **enters or switches into** unattended for a **whole-project**,
**milestone-wide**, or **final-delivery** scope, the **same wave Must** complete
this checklist before deep Analysis / Implement waves that risk turn cutoff:

1. **Load** this reference and `granoflow-project-sot` / `project-sot` via MCP.
2. **Create or update** `temp/project-sot.yaml` with a concrete `next_step`
   (skeleton after `project_init` is enough; expand after portfolio ready;
   regen from App if missing).
3. **Probe Layer B** (`collaborative_planning_surface`):
   - `available` → activate / enter without asking;
   - `unavailable` / `unknown` → continue with Layer A only (do not block).
4. **Probe Layer C** (`host_wake_surface`) — **Must attempt** the probe on
   unattended long / whole-project runs:
   - `available` → **Must arm** wake bound to the active SoT using the
     **canonical wake payload** below (Host Wake Tick Protocol);
   - `unavailable` / `unknown` → **do not block**; emit a user-visible
     `host_wake_unavailable_notice` that includes the **canonical resume
     prompt** (never a bare 「继续」 / “continue”) so a human or later host
     can re-enter on `next_step`.
5. **Card-Truth Readiness Gate (RB/UIT)** — When the project uses
   `reality_boundary_index` and/or `route_ui_truth_index`, run
   `unattended-card-truth-batch-gate.md` in this wave: verify App/capabilities,
   **auto-apply** seed gaps and pending `will_change` (preview→apply→index
   upsert), then `lint_unattended_card_truth_ready.py`. Set
   `card_truth_batch_gate.status: blocked` only for external/capability blockers
   — **not** because the run is unattended.
   Do not enter deep unattended Implement/E2E claiming UIT/RB Delivery closed
   while apply readback is missing.

Skipping the SoT create/update on this entry fails closed as
`project_sot_missing` / `long_run_plan_missing`. Asking solely to enable a
host-local planning UI fails closed as
`collaborative_planning_surface_confirm_in_unattended`. Card-truth gate
failures: `card_truth_batch_gate_missing` / `card_truth_batch_gate_blocked`.

**Canonical whole-project unattended utterance** (natural-language trigger;
contract body stays English):

```text
请用无人值守模式根据 docs 下的产品文档和用户故事生成 granoflow 项目并完成和交付它。长跑维护 Project SoT（temp/project-sot.yaml），并在宿主支持时按 SoT next_step 定时唤醒续跑。
```

English equivalent intent: unattended generate-from-docs → full delivery
including E2E; maintain Project SoT; arm host wake on `next_step` when the
host exposes Layer C.

**Canonical resume prompt** (user-visible when Layer C is unavailable, and the
semantic core of every wake payload):

```text
Unattended Granoflow continue: load long-task-run-continuity and granoflow-project-sot; read bound_run_plan_path (temp/project-sot.yaml); regen if missing; run Host Wake Tick Protocol for exactly next_step; update the SoT; re-arm if solvable work remains.
```

## Collaborative Planning Surface (Layer B)

### Interactive

When Layer B is available, **request or enter** it at the start of a long task
(host-native switch or structured in-chat plan—whatever the host supports).
Still create Layer A in the same wave.

### Unattended

Follow **Unattended Entry Continuity Checklist** item 3. When Layer B is
`available`, the host **Must** activate / enter that built-in Plan or planning
mode **at the moment of unattended entry** (and keep it for the long run)—no
asking whether to plan. When Layer B is not available, unattended **Must**
still create/update Layer A and continue solvable work—never stall waiting for
a missing host UI.

Asking the user solely to enable a host-local planning UI under unattended fails
closed as `collaborative_planning_surface_confirm_in_unattended`.

## Host Wake Surface (Layer C)

### When to arm

For **unattended** long / whole-project / campaign runs: **Must probe** Layer C
in the entry wave (see Unattended Entry Continuity Checklist). Then arm Layer C
when **all** of:

1. the run is long or unattended implement / campaign (see Triggers);
2. `host_wake_surface.availability: available`;
3. an active Layer A file exists with a concrete **Next step**.

When Layer C is `unavailable` / `unknown` after the required probe, emit
`host_wake_unavailable_notice` with the canonical resume prompt and continue
solvable work in the current turn—do **not** fail closed solely for a missing
wake surface.

Do **not** arm a wake whose payload is only 「继续」 / “continue” with no plan
path. That fails closed as `host_wake_prompt_missing_next_step`.

### Host Wake Tick Protocol (hard when Layer C is used)

Each wake / tick **Must** run this sequence—no status-only turn that leaves the
plan unchanged while solvable work remains:

1. **Read** the Project SoT at `bound_run_plan_path` (default
   `temp/project-sot.yaml`; regen if missing). Lint when materially updating.
2. **Execute exactly one** `next_step` work item (skill black box). Apply
   `unattended-interaction-contract` (`continue` / `defer_item` /
   `complete_with_residuals`)—do not invent mid-tick questions.
3. **Update** the same SoT file: stage / work_item statuses, `next_step`,
   evidence, `updated_at`. Stale next-step after a productive tick →
   `long_run_plan_stale` / `project_sot_stale`.
4. **Re-arm or stop:**
   - If solvable work remains and the run is not paused/stopped → re-arm Layer
     C with a payload that still names `bound_run_plan_path` and instructs the
     Tick Protocol (not a bare continue). Forgetting to re-arm while work
     remains and Layer C was in use → `host_wake_not_rearmed`.
   - If only allowed residuals remain → emit Unattended Residual Report, set
     SoT `status: completed` or `paused`, and **do not** re-arm.
   - If the user asked to stop → kill tracked wake PIDs / cancel heartbeat and
     do not re-arm.

### Wake payload shape (portable) — canonical

Hosts differ; the durable invariant is the **semantic payload**, not a vendor
sentinel string. Prefer JSON beside the host’s wake line. The `prompt` field
**Must** be the **canonical resume prompt** from Unattended Entry Continuity
Checklist (or an equivalent that still names load → read SoT → one `next_step`
→ update → re-arm):

```json
{
  "prompt": "Unattended Granoflow continue: load long-task-run-continuity and granoflow-project-sot; read bound_run_plan_path (temp/project-sot.yaml); regen if missing; run Host Wake Tick Protocol for exactly next_step; update the SoT; re-arm if solvable work remains.",
  "bound_run_plan_path": "temp/project-sot.yaml"
}
```

Arming Layer C without binding that path (or with a missing SoT file) fails
closed as `host_wake_unbound_from_run_plan`.

### What Layer C must not pretend

- Layer C does **not** authorize publish/secrets/device work.
- Layer C does **not** replace Layer A: a ticking wake with no next step is a
  false progress loop.
- Layer C does **not** replace GFMCP / external runners; do not claim a chat
  wake proves an out-of-band worker is alive.

## Relationship

| Concern                                      | Owner                                   |
| -------------------------------------------- | --------------------------------------- |
| Milestone Plan acceptance (design artifacts) | `milestone-plan-acceptance-pack.md`     |
| Per-task Plan Design Gate                    | `plan-design-gate.md`                   |
| Surviving long agent loops / host variance   | **this file**                           |
| Host wake bound to durable next step         | **this file** (Layer C)                 |
| Project orchestration SoT (Layer A file)     | `granoflow-project-sot` / `project-sot` |
| Plain-language gloss for users               | `workflow-jargon-plain-language.md`     |
| Unattended ask budget                        | `unattended-interaction-contract.md`    |

## Admission Test

1. Was this reference loaded for a long or unattended implement run?
2. Does an active `temp/project-sot.yaml` exist and name `next_step`?
3. Were Layers B / C referenced only via availability, not a required vendor name?
4. Unattended entry: was the Unattended Entry Continuity Checklist completed in
   the same wave (SoT + Layer B probe + Layer C probe/arm or
   `host_wake_unavailable_notice`)?
5. Unattended + Layer B available → activated without an acknowledgement question?
6. If Layer C is used: is wake payload the canonical resume shape bound to the
   SoT path, and does each tick run read → one next_step → update → re-arm-or-stop?
7. After a productive tick, is `next_step` refreshed (not stale)?
