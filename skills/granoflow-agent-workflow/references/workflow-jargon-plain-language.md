# Workflow Jargon → Plain Language

Single owner for **user-facing chat and progress notices**: when a workflow
token that users rarely meet outside Granoflow/MCP appears, the host **Must**
pair it with a plain-language gloss and a concrete “what you can say/do next.”

Internal Task Work YAML, fail-closed codes, and App attachment metadata may keep
exact tokens. This contract governs what the **user is asked to read or reply
to**.

## Mandatory Load

Before a user-visible turn that mentions any token in the Glossary (or an
equally opaque peer such as `plan_design_gate_status`), load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "workflow-jargon-plain-language"
)
```

Skipping the load and dumping bare tokens at the user fails closed as
`workflow_jargon_unexplained`.

Also apply `project-interaction-style.md` (default beginner-safe).

## Hard Rule

In interactive user-facing prose (including Project Lifecycle Progress Board
`next_action.summary` / recommendation lines):

1. **Do not** end a turn with only opaque tokens
   (e.g. bare `execution_authorization` / `run` with no gloss).
2. Prefer **everyday verbs** first; put the token in parentheses once if useful
   for continuity with records.
3. Always add **what the user should do or say** when the next step needs them
   (a suggested reply phrase is ideal).
4. Unattended: still use plain language in notices; do not ask style questions;
   do not invent confirmation questions solely to explain jargon.

Fail closed:

- `workflow_jargon_unexplained` — user-facing next step uses Glossary tokens
  without plain gloss + action cue
- `workflow_jargon_action_missing` — explained the term but gave no concrete
  user action / suggested phrase when the phase needs the user

## Phrase Shape (recommended)

```text
<通俗结论>。
（内部名：<token>）
你现在可以：<动作>；例如直接回复「<建议话术>」。
```

Shorter is fine when the project style is `concise`, but the gloss + action cue
must remain.

## Glossary (minimum set)

Localize the gloss to the conversation language. Tokens stay English.

| Token / phrase                                          | Plain gloss (zh example)                                                 | What the user can do (zh example)                                   |
| ------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `execution_authorization`                               | 还差一步「允许真正开始改代码/做实现」的授权；Plan/验收通过不等于已经开工 | 若同意开工，直接说「开始实施」或「实施 M1」                         |
| `run` / `gf做` / 实施指令                               | 告诉 AI：**现在可以按已确认的方案动手做**                                | 回复「开始实施」；需要限定范围时说「开始实施 M1」或「实施这个任务」 |
| Plan Design Gate / `plan_design_gate`                   | 实施前的设计验收：测试用例、流程、数据结构等是否够用                     | 看验收册后回复「确认 Plan 验收册」或指出要改的地方                  |
| milestone Plan acceptance pack / 验收册                 | 把本里程碑 Plan 产物（文案、表结构、流程图、测试用例等）收成一份给你验收 | 打开验收册核对后说「确认」；通过后才能谈开工                        |
| Readiness Grill                                         | 开工前再检查一遍：依赖、原型、预测文件等是否齐                           | 一般由 AI 自检；缺东西时按提示补充或确认                            |
| `execution_authorization: not_requested`                | 还没申请「可以动手」                                                     | 需要动手时说「开始实施」                                            |
| Structural Change Forecast / 结构预测                   | 打算改哪些文件/模块的预告（不是让你背代码）                              | 通常只需知晓；有明显跑题再说                                        |
| `needs_decision`（库/依赖）                             | 要用到一个新的重要第三方能力，需你拍板                                   | 按提示选同意/换方案/暂停                                            |
| Unattended / 无人值守                                   | AI 尽量自己往下做，少打断你；遇外部阻塞会记下来                          | 一般不用回「确认进度板」；有 Residual 报告时再处理                  |
| Durable run plan / 可续跑执行计划                       | 落盘的分阶段执行清单（下一步、证据），换会话/换工具也能续                | 一般由 AI 维护；你只需在暂停时说「暂停」或改范围                    |
| Collaborative planning surface / 协作规划面             | 当前 Agent/IDE **若有**的规划界面或规划模式（各产品名称不同）            | 有则让 AI 打开；没有也不必强求，以可续跑执行计划为准                |
| Host-local “Plan mode” 等品牌名                         | 某宿主的本地称呼，不是跨 Agent 硬门禁                                    | 勿要求用户只会说某个 IDE 的模式名；说「开始实施」即可               |
| Integration campaign Closing Summary / 集成测试收尾总结 | 用大白话说明：查了什么、过没过、对你有什么影响、还剩什么、下一步说啥     | 读总结；有遗留就按提示补材料；全过可说「项目收尾」                  |
| `failure_class` / `product_code` / `test_harness`       | 问题出在「产品本身」还是「检查脚本写错了」                               | 一般不用回这些词；看收尾总结里的「对你有什么影响」即可              |

Agents **May** extend the table for peer tokens with the same phrase shape.
Do not invent synonyms that hide the real gate (e.g. do not say “随便改吧”
when authorization is still required).

## Progress Board And Next-Action

When `project-lifecycle-progress-board.md` recommends implement:

- **Bad:** `next: execution_authorization / run`
- **Good:** `下一步：真正开始写代码。你可以说「开始实施」（或「开始实施 M1」）。`

Keep machine fields (`stage_id`, codes) intact in YAML; gloss the
user-visible summary.

## Relationship

| Concern                              | Owner                                            |
| ------------------------------------ | ------------------------------------------------ |
| Audience / verbosity                 | `project-interaction-style.md`                   |
| Product UI string quality            | `user-visible-copy-boundary.md`                  |
| When Execution may start (gates)     | Task Work / `plan-design-gate` / acceptance pack |
| Long-run continuity (host-agnostic)  | `long-task-run-continuity.md`                    |
| How to **say** those gates to humans | **this file**                                    |

## Admission Test

1. Was this reference loaded when Glossary tokens appeared in user-facing text?
2. Did the user get a plain gloss?
3. If their reply is required, was a concrete suggested phrase given?
