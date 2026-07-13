# Task Analysis And Execution

Read this reference when the user asks to analyze, plan, start, execute, or move
forward one selected Granoflow task. Use `daily-pending-task-triage.md` for date,
batch, or all-unfinished-task scopes.

Runtime behavior is multilingual. Public README, npm, registry, and directory
copy remains English-only; localized prompts and replies belong here and in
tests.

## Trigger Examples

- `Analyze the first task`
- `Start the first task`
- `请分析第一个任务`
- `执行第一个任务`
- `处理排在最前面的任务`

## Phase 0: Resolve And Read

Resolve exactly one active task before analysis. `First task` means the first
active task only when app/API order matches the user-visible order. Other
supported references include task id, exact or partial title, and
project/milestone scope.

Never claim a task is the first active task when that order cannot be verified.

- Multiple matches: ask the user to choose.
- No match: offer the quick requirement-capture workflow.
- Unreliable `first task` order: show a short candidate list.

Read enough task detail to establish title, description, status, dates, existing
nodes, prior review, project/milestone ids, and current project/milestone
descriptions. Treat descriptions as context, not task facts. Do not invent
missing context.

Gap codes:

- `project_context_unavailable`
- `milestone_context_unavailable`
- `project_context_orphaned`
- `milestone_context_orphaned`

## Three-Axis Analysis State

Keep document lifecycle, analysis decision, and planning readiness separate:

```yaml
analysis_status: unanalysed | awaiting_confirmation | draft | grill_in_progress | awaiting_final_confirmation | finalized
decision: proceed | needs_input | user_action | split | redefine | defer | abandon | completion_audit
planning_readiness: yes | no
```

`analysis_status=finalized` does not imply `planning_readiness=yes`. Only a
confirmed `decision=proceed` analysis that passes every readiness gate may enter
planning.

## Phase 1: Prefill The Seven-Dimension Analysis

Read [task-analysis-template.md](task-analysis-template.md). Always use the
complete base template, then append zero or more thin profiles in this order:

- [task-analysis-profile-learning.md](task-analysis-profile-learning.md)
- [task-analysis-profile-software-development.md](task-analysis-profile-software-development.md)

Profiles are composable:

```yaml
profiles: [] | [learning] | [software_development] | [learning, software_development]
```

For legacy reads only, map `task_type=learning` to `[learning]`,
`task_type=software_development` to `[software_development]`, and legacy
software work with `purpose=learning` to both profiles. New attachments write
only `profiles`. Profiles add requirements and never weaken the base contract.

Before drafting recommendations, read the task's linked cards and search for
relevant similar cards. Load `granoflow-review-card-draft` and its canonical
`lifecycle-card-checkpoints.md` reference. Existing cards may inform the
analysis; any link, update, or create proposal remains a separately approved
card operation. If capabilities are unavailable, record
`card_context_unavailable` without inventing card state.

Prefill from task facts, files, user messages, project context, and verified
evidence. Separate:

- confirmed facts;
- materials and evidence;
- AI inference;
- unknown information.

Do not turn the template into a blank questionnaire.

If the available facts cannot support a directional recommendation, record the
legacy diagnostic `not_enough_information`, set `decision=needs_input`, and ask
only for information that can change the decision.

## Phase 2: One Decision Batch With AI Recommendations

Present every unresolved directional question in one batch. `Every` means every
question that can still change Outcome, Evidence, Boundaries, responsibility,
decision, or planning readiness—not every field in the template.

For each item use:

```text
问题:
当前理解:
AI 推荐:
推荐理由:
其他选择:
采用推荐的影响:
需要你确认:
```

Compress locally resolved facts under `AI 已确认`. The batch must cover the
seven dimensions where relevant:

1. Trigger
2. Outcome
3. Evidence
4. Context
5. Boundaries
6. Risks
7. Decision

The user may reply:

```text
全部按推荐，写入初稿并开始 Grill Me
```

That reply authorizes only:

- creating or updating the analysis draft;
- attempting attachment upload only when a task-attachment capability is
  explicitly advertised;
- updating the controlled analysis-summary block;
- starting the Grill conversation.

It authorizes card operations only when the same reply also explicitly accepts
identified operation IDs. Normalize draft and card approvals separately; do
not infer one from the other.

It does not authorize planning, nodes, execution, completion, publishing,
messages, payment, login, deletion, or automatically accepting new Grill
recommendations. If the user supplies information without authorizing the draft,
continue the conversation without writing files or task fields.

## Phase 3: Write The Analysis Draft

Create `task-analysis-<safe-task-id>-v01.md` with:

```yaml
analysis_status: draft
decision: <current decision>
planning_readiness: no
```

The draft must contain all seven base sections, the matching profile section,
facts versus inference, evidence strength, current decision, Grill review,
planning readiness, and the Analysis Card Checkpoint. Simple tasks may be short
but may not omit the dimensions.

### Description summary

Preserve the original task description. Manage at most one block:

```text
<!-- granoflow-analysis-summary:start -->
- Profiles: <none | learning | software_development | both>
- 状态: <analysis_status>
- 结论: <decision>
- 核心判断: <1-3 sentences>
- 验收方向: <strongest evidence>
- 责任: AI | 用户 | 双方
- 当前阻塞: 无 | <blocker>
- 分析文档: <attachment or safe path>
- 文档状态: attached | local_reference | attachment_api_unavailable
- 下一步: <state-level action>
<!-- granoflow-analysis-summary:end -->
```

Update rules:

- no markers: append one block;
- exactly one valid pair: replace only its contents;
- duplicate, missing, reversed, or nested markers: fail closed with
  `analysis_summary_markers_invalid`;
- never rewrite content outside the markers.

### Attachment capability

Prefer an app-owned task attachment only when capability discovery explicitly
advertises it. Project-context attachments are not task attachments. Without a
task attachment capability, save a safe local Markdown file, record
`local_reference` and `attachment_api_unavailable`, and never claim attachment
or sync success. If neither attachment nor a safe file is possible, keep a
compressed summary in description and report the gap.

Read the original task back after any description or attachment write and verify
that the write belongs to the resolved task.

## Phase 4: Grill The Draft

Set `analysis_status=grill_in_progress`. Granoflow must have a bundled fallback;
third-party availability is optional.

Minimum attacks:

- Is the Outcome only a surface symptom?
- Can Evidence produce false success?
- Does Out of scope exclude necessary work?
- Is AI-capable work assigned to the user?
- Which inference could overturn the analysis?
- What second-order problem follows from the recommendation?
- Should the task split, redefine, defer, or stop?
- For learning: does Evidence prove independent mastery?
- For software: does Evidence cover project gates and the real user surface?

Each Grill item contains:

```text
Grill 问题:
攻击的原结论:
AI 推荐:
推荐依据:
如果判断错误的后果:
需要用户确认:
```

Rules:

- An installed, callable `grill-me` may enhance the conversation.
- Select only relevant gstack lenses when explicitly available; do not run the
  full engineering suite for general or learning tasks.
- Third-party absence or failure immediately falls back to bundled Grill.
- A request to start Grill does not accept future directional recommendations.
- Evidence-backed factual edits that preserve confirmed intent may update the
  draft; changes to Outcome, Evidence, Boundaries, responsibility, or decision
  require user confirmation.
- Every accepted finding updates the main analysis sections, not only the Grill
  appendix.
- When Grill changes a knowledge assumption, re-run the Analysis Card
  Checkpoint. New or changed card writes require a fresh preview and explicit
  operation approval.

### Grill budget

Ordinary tasks get 最多两轮 of directional Grill. If directional uncertainty
remains after two rounds, set `decision=needs_input`, list the missing input, and
stop instead of interrogating indefinitely. A high-risk task may continue only
after explaining why another round is necessary and what it will close.

## Phase 5: Confirm The Final Analysis

When directional questions close, set
`analysis_status=awaiting_final_confirmation` and show:

- changes from draft to proposed final;
- final decision and rationale;
- unresolved non-blocking risks;
- planning readiness;
- constraints a future plan must inherit.

Only after the user replies:

```text
确认分析终稿
```

may the agent set `analysis_status=finalized` and update the document and
controlled summary.

Set `planning_readiness=yes` only when:

- facts and inference are separated;
- Outcome, scope, and non-goals are clear;
- observable Evidence exists;
- task type and responsibility are known;
- missing information, risks, and assumptions are visible;
- directional Grill questions are closed;
- `decision=proceed`;
- the user confirmed major tradeoffs and the final analysis.

Every non-`proceed` decision has `planning_readiness=no`.

## Phase 6: Plan Or Stop

When planning readiness is yes, ask exactly:

```text
分析已经收敛，建议进入计划阶段。是否开始编写计划文档？
```

Do not write a plan or execute automatically. Analysis names only state-level
next actions. File, command, node, implementation, rollback, and verification
steps belong in the plan.

If the user requests planning or execution for a task without a confirmed
analysis final, enter this analysis workflow first. Simple tasks may be concise
but do not bypass draft authorization, Grill, or final confirmation.

## Planning And Execution After Confirmation

Read [task-plan-workflow.md](task-plan-workflow.md). It is the single owner for
Plan authoring, immutable attachment versions, deliverable nodes, handoffs,
manual acceptance, current-state reconciliation, execution writeback, and
node-driven task completion. The Plan must cite the active analysis final and
inherit Outcome, Evidence, Boundaries, Risks, and confirmed decisions.

Retrieve prior cards or related tasks only when the confirmed analysis shows
that history can materially improve the plan. Record `card_context_unavailable`
when needed card evidence cannot be retrieved; never invent prior experience.

For AI-completable work, execute only the confirmed Plan. For user-only work,
write `验收：<object>` or other user nodes and leave them pending without
blocking later safe AI nodes. The running Granoflow app must advertise the task
node workflow capability; otherwise record `task_node_api_unavailable` and stop
before claiming durable node writeback.

Use `waiting-for-user-input.md` for authorization, login, payment, private
materials, secrets, or other user-only blockers. Never treat missing permission
as permission.

Execute only after user confirmation. Read the original task back after node or
fallback writes. Do not compute embeddings, inspect app storage, expose raw
similarity scores, invent prior experience, or create cards outside the
confirmed card workflow.

## Completed Work Without Prior Analysis

When work is already complete, write a factual retrospective analysis and a
completion audit. Do not fabricate or relabel them as a pre-execution analysis
or plan.
