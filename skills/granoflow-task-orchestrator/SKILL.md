---
name: granoflow-task-orchestrator
description: Infer task lifecycle intent from conversation context and orchestrate Granoflow capture, analysis, planning, execution, delivery, and completion through one short interface.
---

# Granoflow Task Orchestrator

Use this bundled MCP skill as the single upper-layer task entrypoint. It decides whether a request is an incidental capture, a context-rich task, an analysis or planning request, an end-to-end execution request, or an already-completed delivery audit, then delegates to existing Granoflow workflow owners without duplicating their contracts.

## Keyword

- `#gf`
- `#gf-capture`
- `#gf-analyze`
- `#gf-plan`
- `#gf-run`
- `#gf-finish`

## When to use

- Use whenever the user asks to record, analyze, plan, execute, finish, or otherwise manage work in Granoflow.
- Use when a new task idea appears during another active task and the agent must preserve it without derailing current work.
- Use when natural-language context may already be sufficient to enter Analysis, Planning, or safe local execution.
- Use Chinese shortcuts gf记, gf析, gf规, gf做, gf完 or ASCII aliases gf+, gf?, gf>, gf!, gf. only as explicit route overrides; plain gf uses automatic routing.

## Example requests

- 刚想到以后要优化首次同步，先记一下。
- gf析 把我们刚才讨论的导入兼容问题整理成可决策的分析。
- gf做 把刚才确认的两个任务建档、分析、计划、实现、验证并在 GF 完成。

## Workflow

Before routing a project-bound request, call
`granoflow_agent_preferences_get(projectId)`. Apply the resolved explanation and
execution defaults without asking repeated setup questions. Preferences may
select a normal path, but they never weaken Task Work, test, Delivery,
authorization, acceptance, Git-checkpoint, or external-action gates.

After every project-bound analyze / plan / run / finish stop (and whenever the
user asks for status or next steps), load
`granoflow-agent-workflow/project-lifecycle-progress-board` and end the turn
with a rendered progress board + recommended next action. Interactive mode keeps
phase confirmations; unattended mode shows the same board as display-only and
does not ask for board acknowledgement.

### 1. Classify lifecycle intent from context

Choose exactly one route: capture, enrich, analyze, plan, run, or finish_audit.

Actions:

- Read the current user imperative together with the active task, recent discussion, supplied evidence, current work relation, and target candidates.
- Use an explicit shortcut as a route override; otherwise classify semantically.
- Prefer capture for incidental side thoughts and finish_audit when evidence shows the work is already complete.
- If the work is already in Plan / Implement / delivery and the user confirms a
  change to early requirements, acceptance, or prototype: classify pipeline
  `entry_kind: midstream_change` (see `pipeline-attachment-and-reentry`). Delegate
  writeback + change-impact fan-out and stage rewind **before** analyze/plan;
  **never** route directly to `run`.
  Success criteria:
- The selected route explains why this is capture, enrichment, Analysis, Plan, run, or completion audit.
- A side thought cannot derail the active task.
- Confirmed midstream early-requirement changes do not skip re-entry.
  Checkpoints:
- Ask only when multiple existing targets would make a write unsafe; otherwise choose the safest useful route.
  Artifacts:
- intent decision
- routing facts
- fallback reason
  Rules:
- Low information falls toward capture or Analysis, never directly toward execution.
- Midstream confirmed early changes → writeback then analyze/plan; `run` is
  forbidden until rewind and board `next_action` say otherwise
  (`pipeline_reentry_skipped` if skipped).

### 2. Build the right-depth task record

Create or enrich a task at minimal, contextual, or execution-ready depth.

Actions:

- Read and apply `granoflow-agent-workflow/task-authoring-quality-contract` to
  every task the orchestrator creates, including capture, project-derived,
  milestone-derived, imported, and notification tasks.
- For minimal capture, preserve outcome and origin context only.
- For contextual or execution-ready records, add trigger, outcome, evidence, boundaries, example, completion signal, source task relation, and recommended next phase from known conversation facts.
- Resolve an existing project and active milestone only when the pair is strong; otherwise use inbox.
  Success criteria:
- The task is understandable later without reopening the chat.
- The description is richer only when the conversation actually provides the facts.
  Checkpoints:
- Do not invent acceptance criteria, implementation details, project structure, or urgency.
  Artifacts:
- task description
- placement decision
- capture depth
  Rules:
- Incidental capture never starts Analysis or creates nodes.

### 3. Choose placement and deadline

Apply one deterministic deadline ladder without turning every task into urgent work.

Actions:

- Use an explicit or fact-supported earlier date when present. Otherwise a milestone-bound task inherits the active milestone deadline in the shared MCP task-write runtime.
- Leave dueAt empty for side thoughts, someday/later work, inbox items with no timing signal, and weakly understood tasks.
- Never place a task after its milestone deadline without a separately resolved schedule change.
  Success criteria:
- Every inferred deadline has a visible factual reason.
- No-timing-signal tasks remain undated instead of receiving an arbitrary date.
  Checkpoints:
- If the placement pair is weak or timing evidence is absent, use inbox and no due date without asking.
  Artifacts:
- due-date reason
- project and milestone binding or inbox result
  Rules:
- Urgency language affects dueAt only when it refers to the task being recorded.

### 4. Run the selected lifecycle

Compose the existing task owners through the requested stopping point.

Actions:

- capture stops after create and id readback; enrich stops after a context-rich task readback.
- analyze runs Analysis plus bundled Grill and stops at the confirmed or
  decision-blocked Analysis state. End every Analysis turn with an explicit
  **Analysis Deliverables** table (done / pending / missing). UI-changing tasks
  must set `prototype_requirement: required` and Must obtain a confirmed
  `ui_prototype` before Analysis confirmation; missing prototype fails closed
  as `ui_prototype_required` / `analysis_deliverables_incomplete` and keeps the
  task in Analysis (Planning Must not start).
- plan consumes a finalized Analysis, creates Plan and nodes, runs Readiness Grill, and stops execution-ready. UI-changing tasks cannot pass Readiness without a visually confirmed `ui_prototype` (`derivedFrom` Design Baseline when present). Software tasks that will edit code cannot pass Readiness without a complete `Structural Change Forecast` (`structural_forecast_status: present_in_plan`); otherwise `structural_forecast_missing`.
- run composes create or resolve, Analysis, Grill, Plan, Readiness Grill, safe execution, verification, Delivery, node completion, and done-state readback. Never execute a UI-changing task while `ui_prototype_required` applies. Before the first software edit: run project-context Hard Gate (`project_snapshot.yaml` / `project_rules.yaml`); on conflict, interactive users confirm, unattended runs emit `revise_code` or `revise_context_yaml` explicitly; then show the structural forecast notice and stamp `notice_emitted`. Refuse edits with `project_context_check_missing`, `project_context_decision_not_emitted`, or `structural_forecast_not_shown`. Delivery/close requires `reconciled` plus `acceptance_report` or fail closed. For software: copy-only / 文字验证 tasks take **no** automated tests (`copy_change_tests_forbidden`). Otherwise judge unit-test sufficiency; add at most 2 integration tests only when insufficient; honor Project Work `integration_test_special_requirements` when adding IT; **do not execute** those integration tests (`integration_test_executed_by_agent` if the Agent runs them); recommend the user's **local machine** for the device and let the user confirm or choose (`integration_test_device_unselected` if still unselected when tests were added).
- finish_audit verifies already-produced evidence, writes Delivery, and closes only through the correct completion owner.
  Success criteria:
- Each phase has exactly one owner and the requested stopping point is respected.
- An end-to-end request does not stop merely because a phase transition was reached.
  Checkpoints:
- Batch decision-changing questions once; continue all independent safe work before waiting.
  Artifacts:
- phase trace
- A/P/D artifact references
- GF readbacks
  Rules:
- Use A, P, and D in user-facing shorthand while retaining canonical attachment metadata and compatible filenames internally.

### 5. Consume bounded command authorization

Allow gf做 or gf! to continue safe local task work without repeated phase confirmations.

Actions:

- Bind the user-origin command, exact target tasks, repositories, allowed local actions, exclusions, and expiry to a named local-run authorization profile.
- After Analysis and Readiness grills pass with no unresolved decisions or scope drift, bind the generated Plan hash and continue the already-approved phases.
- Revalidate current App facts before every phase. Under an explicit unattended
  declaration, execute solvable work; defer externally impossible items without
  blocking peers; end with an Unattended Residual Report
  (`unattended-interaction-contract.md`).
  Success criteria:
- A clear end-to-end local-run command can complete unattended within its scope.
- External, destructive, secret-bearing, and expanded actions still fail closed.
  Checkpoints:
- The shortcut contract itself must be previewed and explicitly approved before first use; future invocations name their target scope and act as explicit grants under that approved profile.
  Artifacts:
- authorization profile receipt
- phase evaluations
- plan hash binding or waiting reason
  Rules:
- Plain gf routing never increases authorization; only explicit natural-language imperatives or approved shortcut profiles grant actions.

## Rules

- [must] For project-bound work, emit the Project Lifecycle Progress Board + next
  action at each stop (`project_lifecycle_board_missing` if omitted). Unattended:
  display-only; never require confirming the board.
- [must] Expose one deep orchestration interface and delegate capture, Analysis, Plan, Execution, Delivery, completion, cards, and waiting to their existing owners.
- [must] Treat plain natural language as primary; shortcuts are optional route overrides and must not be required for semantic understanding.
- [must] Use explicit facts rather than a fake numeric confidence score: current-work relation, imperative strength, outcome clarity, boundary clarity, evidence sufficiency, timing signal, and target ambiguity.
- [must] Preserve inbox capture with no due date for incidental side thoughts, someday/later requests, weak placement, and missing timing evidence.
- [must] Never weaken the shared task title, plain-language, analogy, example,
  or change-evidence contract because a task came from a project, milestone,
  import, or automation path.
- [must] Batch unresolved directional questions once and continue automatically when the user has invoked an approved bounded local-run profile and all grills pass without scope drift.
- [must_not] Never infer publish, push, deletion, payment, login, secrets or 2FA, external messaging, approved-asset overwrite, or scope expansion from context or a shortcut.

## References

- Read [intent-and-maturity-routing.md](references/intent-and-maturity-routing.md) when Read before selecting capture, enrich, analyze, plan, run, or finish_audit.
- Read [task-depth-placement-and-dates.md](references/task-depth-placement-and-dates.md) when Read when creating or enriching a task.
- Read [short-command-contract.md](references/short-command-contract.md) when Read when parsing gf shortcuts or displaying lifecycle artifacts.
- Read [end-to-end-orchestration.md](references/end-to-end-orchestration.md) when Read for plan or run routes.
- Use [route_task_intent.py](scripts/route_task_intent.py) when a host needs a
  deterministic decision from structured routing and authorization facts.

## Success Criteria

- The workflow preserves preview -> confirm -> write as a hard gate.
- Every major step leaves a machine-readable artifact or validation result.
- Forward-test can be rerun from a fixed fixture without modifying the live skill directory.
