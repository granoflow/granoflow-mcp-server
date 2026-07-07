# Task Analysis And Execution

Read this reference when the user asks the agent to analyze, start, execute, or
move forward one selected Granoflow task, such as `Analyze the first task`,
`Start the first task`, or an equivalent command in the user's language.

This is a single-task workflow. Use `daily-pending-task-triage.md` for batch due
tasks, date scopes, more-task scopes, or all unfinished tasks.

Public README, npm, registry, and MCP-directory copy must stay English-only.
Localized trigger examples belong in skill/runtime documentation and tests, not
canonical public listing copy. Runtime behavior is multilingual: accept
equivalent commands in the user's language and write explanations, questions,
plan summaries, task-node plans, and final reports in that language by default.

## Trigger Examples

Public English examples:

- `Analyze the first task`
- `Start the first task`

Localized examples:

- `请分析第一个任务`
- `执行第一个任务`
- `处理排在最前面的任务`

## Phase 0: Resolve The Target Task

Resolve the intended Granoflow task before analysis.

Supported references:

- `first task`, meaning the first active task in the running Granoflow app's
  current task order;
- task title;
- task id;
- partial title or description;
- project/milestone scoped description;
- relative phrasing, such as `the task about card schemas`.

Rules:

1. If the user says first task, read the task list and use the first active,
   non-done, non-trashed task in the app/API order only when that order is
   documented or clearly matches the user-visible surface.
2. If the API order is not reliable, state the ambiguity and ask the user to
   choose from a short candidate list.
3. If exactly one active task matches the user's description, use it.
4. If multiple tasks match, ask the user to choose.
5. If no task matches, ask whether to create a task through the requirement
   capture workflow instead.

After resolving, export or read enough task detail to understand:

- title and description;
- project and milestone ids or names;
- project description when the task has `projectId`;
- milestone description when the task has `milestoneId`;
- status;
- due/reminder data;
- existing nodes or checklist items when available;
- task review or previous history when available.

Project and milestone descriptions are planning context, not task facts. The
plan must separate task facts, project/milestone context, and AI inference. Use
active milestone descriptions as current phase context. Treat done, archived, or
otherwise inactive milestone descriptions as historical snapshots only.

Context gap codes:

- `project_context_unavailable`: project description cannot be read.
- `milestone_context_unavailable`: milestone description cannot be read.
- `project_context_orphaned`: task has `projectId`, but the project cannot be
  resolved.
- `milestone_context_orphaned`: task has `milestoneId`, but the milestone cannot
  be resolved.

Do not invent project or milestone context.

## Phase 1: Classify The Task

Classify the task into one primary branch:

- `ai_can_complete`: the agent can complete the task with current tools and
  user-confirmed permission.
- `ai_can_complete_after_input`: the agent could complete it after the user
  supplies information, files, login, authorization, or a decision.
- `user_must_complete`: the task requires physical-world action, private
  account action, subjective decision, payment, login, 2FA, credential handling,
  or another action the AI cannot safely perform.
- `not_enough_information`: the task is too vague to classify.

If the branch is `ai_can_complete_after_input`, use
`waiting-for-user-input.md` for blockers before execution. Do not treat missing
permission as permission.

If the branch is `not_enough_information`, ask the smallest useful
clarification question. If the missing information belongs in Granoflow, use the
waiting workflow so the user can add a durable response node. Do not run broad
retrieval to guess the missing scope.

## Phase 2A: Simple AI-Completable Task

Use this branch when the task is small enough to plan from the task itself
without meaningful historical retrieval.

Required steps:

1. Write a concise plan document or clearly labeled plan section.
2. Grill the plan internally.
3. Revise the plan.
4. Explain the revised plan to the user in plain language, with examples or
   analogies when useful.
5. Avoid invented opaque agent terms. If a technical term is necessary, preserve
   the English term and add the user's-language common translation in
   parentheses when the user's language is not English.
6. Let the user discuss, edit scope, reject the plan, or request another path.
7. After the user confirms, update the plan with final user feedback.
8. Execute according to the final plan.
9. Write evidence back to the task and finish only when completion is verified.

When a local plan document is created, preserve its safe path or attachment
status in final task evidence. If no separate file is useful, keep the plan as a
clearly labeled task plan section.

Simple tasks should not trigger broad memory retrieval only for theater. The
retrieval cost must be justified by ambiguity, risk, or expected value.

## Phase 2B: Complex AI-Completable Task

Use this branch when the task is broad, risky, technically uncertain, or similar
to prior Granoflow work.

Retrieval order:

1. Call capability discovery.
2. Retrieve related review cards or durable lesson cards through app-owned
   work-memory, context-pack, card-similarity, or vector-search capabilities
   when available.
3. Classify retrieved cards as successful experience, failure experience,
   warning, concept, or irrelevant.
4. If successful experience exists, write the plan using the relevant successful
   experience and cite the source task/card context.
5. If no successful experience exists but failure experience exists, explain
   the prior failure in the user's language and propose options, including
   abandon, defer, split, or redefine.
6. If card information is insufficient, retrieve related tasks through
   context-pack, task export, task-resolve/list filtering, or app-owned similar
   task surfaces.
7. Judge whether each related task is actually useful. Do not copy a past
   approach merely because it ranked as similar.

Retrieval gap codes:

- `context_pack_unavailable`: context packs are not advertised or fail closed.
- `card_context_unavailable`: card retrieval is unavailable for the needed
  scope.
- `related_task_context_unavailable`: related-task retrieval is unavailable for
  the needed scope.

When retrieval is unavailable, the agent may continue from current task facts
only when risk is low. It must not claim historical support that Granoflow did
not provide.

Plan requirements:

- state which prior cards or tasks were used;
- state which project or milestone descriptions were used as context;
- separate facts from inference;
- name known failure modes;
- include a recommended path and alternatives;
- include abandon, defer, split, or redefine options when history is mostly
  failure or the task value is questionable;
- include validation evidence;
- include blockers and user authorizations;
- include rollback or stop conditions when relevant.

Abandon, defer, split, and redefine are recommendations for user discussion.
They do not automatically change task status, delete the task, or close the
work.

After writing the plan, run a grill pass, revise, then explain the plan to the
user in plain language with examples or analogies. Accept discussion and update
the plan before execution. Execute only after user confirmation.

## Phase 3: Non-AI-Completable Task

Use this branch when the task should be completed by the user, not the agent.

Required steps:

1. Analyze why AI cannot complete the task.
2. Retrieve related cards or prior tasks only when they may contain useful
   experience.
3. Write a plan that breaks the task into user-action nodes.
4. Explain the plan in plain language.
5. Discuss with the user and revise the node plan.
6. After confirmation, write the plan back to the original Granoflow task.

Node plan requirements:

- one node per concrete user action;
- prerequisites and safe order;
- what evidence proves each node is done;
- where AI can help before or after each user action;
- warnings for login, payment, account changes, physical actions, privacy,
  credentials, irreversible changes, or subjective decisions;
- fallback if the user decides to abandon, defer, or split the task.

Writeback behavior:

1. Prefer first-class task-node APIs if the running app exposes them.
2. If task-node write APIs are unavailable, write the confirmed node plan into
   the task description or another documented field and record
   `task_node_api_unavailable`.
3. Read the original task back after node or fallback-field writeback. Verify
   the plan belongs to the intended task and contains the confirmed user-action
   nodes before claiming writeback success.
4. Do not mark the task complete.
5. Do not execute user-only nodes.

## Plan Grill

Every plan must pass an adversarial review before the agent asks for execution
or writeback confirmation.

Minimum grill questions:

- Did the agent resolve the correct task?
- Is the task truly AI-completable, or is a user-only action being hidden?
- If historical cards/tasks were used, are they relevant and source-backed?
- If history contains failure, did the plan explain failure instead of ignoring
  it?
- Does the plan include abandon, defer, split, or redefine when that may be the
  best option?
- Are approvals, logins, files, keys, payments, sends, deletes, publishes, or
  external-account actions explicit?
- Would a non-technical user understand the explanation?
- Does the final plan say what evidence will prove completion?

Every non-`keep` finding must be applied to the plan before showing it as final.

## User Discussion And Confirmation

After the grilled plan is ready, explain it to the user.

The explanation should:

- use the user's language;
- avoid unexplained jargon;
- use analogies or examples when helpful;
- tell the user what the agent will do next;
- identify which parts require the user;
- identify abandon, defer, split, or redefine options when relevant.

The user can discuss the plan in any form. Update the plan when the user changes
scope, priority, constraints, or preferred path.

Execution or writeback starts only after explicit confirmation.

## Execute Or Write Back

For AI-completable confirmed tasks:

- execute only the confirmed plan;
- use the waiting-for-user-input workflow when new blockers appear;
- keep evidence;
- update the task description or nodes when useful;
- finish the task with `granoflow_task_finish` only after completion is
  verified;
- create task reviews and card proposals only under existing review-card and
  completion rules.

For non-AI-completable confirmed tasks:

- write back the confirmed node plan;
- set reminders or current waiting nodes when supported and useful;
- report the node plan and what the user should do next;
- leave the task open for user completion.

## Boundaries

- Do not execute or write back before confirmation.
- Do not compute embeddings or vector scores in the MCP server.
- Do not inspect SQLite, Drift, app files, or local embedding stores.
- Do not expose raw vector scores as user-facing authority.
- Do not treat retrieved similarity as proof of relevance.
- Do not invent prior experience when Granoflow has no evidence.
- Do not create cards outside the existing confirmed review-card workflows.
