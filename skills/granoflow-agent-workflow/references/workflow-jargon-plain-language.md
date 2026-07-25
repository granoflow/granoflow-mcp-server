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

| Token / phrase                                          | Plain gloss (zh example)                                                                                     | What the user can do (zh example)                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `execution_authorization`                               | 还差一步「允许真正开始改代码/做实现」的授权；Plan/验收通过不等于已经开工                                     | 若同意开工，直接说「开始实施」或「实施 M1」                                  |
| `run` / `gf做` / 实施指令                               | 告诉 AI：**现在可以按已确认的方案动手做**                                                                    | 回复「开始实施」；需要限定范围时说「开始实施 M1」或「实施这个任务」          |
| Plan Design Gate / `plan_design_gate`                   | 每个任务自己的实施设计：测试用例（unit/IT/e2e 文本）、流程、数据结构等是否够用                               | 任务 Plan 齐后看里程碑验收册；`gf规`/`开始实施`会在分析齐套后自动连跑 Plan   |
| milestone Plan acceptance pack / 验收册                 | 里程碑级活文档：汇总各任务文案/表结构/流程图/UML/三类测试用例 Markdown，转 HTML 给你点开验收                 | 点开带清晰文件名的 HTML（或 Markdown）`file://` 链接核对后说「确认」         |
| Pack Case sync / 验收册用例对账                         | 验收册里的测试用例 ID 必须和各任务 Plan 里的一致，不能只写在一边                                             | 一般由 AI 自检；若报 Case 对账失败，让 AI 先对齐再验收                       |
| Pack Delivery reconcile / 验收册兑现对账                | 做完任务交付时，对照已确认验收册声明文案/结构/流程/用例是否兑现；有偏离必须写回                              | Delivery 前看对账声明；有漂移应要求返工或改册再确认                          |
| soft-merge / 3.1→3.2 Analysis→Plan                      | `gf析` 可停在待定稿；**确认/定稿分析即开启同任务 Plan**；SoT 钉 next_step 在该任务 3.2                       | 定稿分析后会直接进 Plan；只要分析先别定稿                                    |
| 交互调度（默认）                                        | 每个任务分析完就做计划；全部任务 A+P + 里程碑验收册通过后再统一实施、单测，再全量 IT，再 E2E                 | 默认即如此；无需选择「广度/深度」                                            |
| 无人值守调度                                            | 里程碑内先做完全部分析→Plan 并验收册通过，再实施（含 Layer B），然后下一里程碑（方案 1）                     | 说「无人值守」即切换；已完成阶段不重做                                       |
| Readiness Grill                                         | 开工前再检查一遍：依赖、原型、预测文件等是否齐                                                               | 一般由 AI 自检；缺东西时按提示补充或确认                                     |
| `execution_authorization: not_requested`                | 还没申请「可以动手」                                                                                         | 需要动手时说「开始实施」                                                     |
| Structural Change Forecast / 结构预测                   | 打算改哪些文件/模块的预告（不是让你背代码）                                                                  | 通常只需知晓；有明显跑题再说                                                 |
| `needs_decision`（库/依赖）                             | 要用到一个新的重要第三方能力，需你拍板                                                                       | 按提示选同意/换方案/暂停                                                     |
| Unattended / 无人值守                                   | AI 尽量自己往下做，少打断你；遇外部阻塞会记下来。切入时若 Agent 自带 Plan/规划模式会尽量打开                 | 一般不用回「确认进度板」；有 Residual 报告时再处理                           |
| Project SoT / 项目编排真源                              | 项目 `temp/project-sot.yaml`：粗步骤+下一步；skill 细节是黑盒；丢了可从 App 重生（不是 E2E 测试文件）         | 一般由 AI 维护；长跑/无人值守以它为准；旧名 Project E2E SoT 已弃用            |
| 整项目无人值守交付 + SoT 唤醒续跑                       | 一句「无人值守…生成项目并完成和交付」：入口就写 SoT；宿主能定时唤醒就按 `next_step` 续跑，否则给可复制续跑句 | 演示用完整句；中断后勿只说「继续」，应按 SoT / 续跑提示推进                  |
| SoT digest match / 编排真源摘要对账                     | 长跑续跑前，项目 SoT 记录的 Project Work 摘要要和 App 里当前内容一致                                         | 一般不用管；续跑报 stale 时让 AI 刷新 SoT 后再继续                           |
| Parallel Batch / 并行批次                               | 多个互不抢同一文件的任务一起做；抢同一文件则必须串行或分 worktree                                            | 一般不用管；出现评审链接时点开核对                                           |
| Parallel Batch Review Pack / 并行批次评审包             | `temp/parallel-batch-*-review-v*.md`：汇总各 worker 写了什么、Delivery、能否安全合并                         | 交互：点开 `file://` 后说「确认」或指出要拒的 worker；无人值守由 AI 自检采用 |
| host isolation / 宿主隔离                               | 子进程是否各自独立目录；没有隔离就不能多人同时改同一棵代码树                                                 | 一般不用选；报错时让 AI 改为串行或隔离后再跑                                 |
| Durable run plan / 可续跑执行计划                       | 对项目长跑即上列 SoT（不再另建平行 run-plan）                                                                | 同 SoT                                                                       |
| 验收册「计划基准」vs「兑现承诺」                        | Plan 结束列册链接=计划如此；Implement 结束再列同一链接=已按册做到                                            | 第二遍若发现没做到，应要求 AI 立刻返工                                       |
| Collaborative planning surface / 协作规划面             | 当前 Agent/IDE **若有**的规划界面或规划模式（各产品名称不同）                                                | 进无人值守时有则打开；没有也不必强求，以 SoT 为准                            |
| Host wake surface / 宿主唤醒面                          | 当前工具若支持定时/事件唤醒（各产品名称不同），到点再跑一轮，避免人说「继续」                                | 一般不用你操作；若唤醒空转可说「按 SoT 下一步继续」                          |
| Host Wake Tick Protocol / 唤醒续跑协议                  | 醒了以后：读 SoT → 只做 next_step → 更新 → 没做完再预约下一次唤醒                                            | 发现只汇报进度、不推进时，要求 AI 按协议续跑                                 |
| Host-local “Plan mode” / “/loop” 等品牌名               | 某宿主的本地称呼，不是跨 Agent 硬门禁                                                                        | 勿要求用户只会说某个 IDE 的模式名；说「开始实施」或「无人值守」即可          |
| Integration campaign Closing Summary / 集成测试收尾总结 | 用大白话说明：查了什么、过没过、对你有什么影响、还剩什么、下一步说啥                                         | 读总结；有遗留就按提示补材料；全过可说「项目收尾」                           |
| Layer A / 单任务完成验收                                | 某个任务自己做完：Delivery、报告、单测等（AI 自检为主）                                                      | 一般不用逐任务点确认；看清单知悉即可                                         |
| 确认验收即打钩                                          | 产物验收确认后，同一波就把 App 任务勾成 done；无人值守下 AI 自荐=已确认                                       | 交互：确认后应看到勾选；无人值守：跑完应收口为已完成                         |
| 确认里程碑验收=打齐任务钩                               | 里程碑 Layer B 确认时，同波把该里程碑所有 in-scope 子任务勾成 done                                           | 里程碑已验收时，列表里不应再留未勾子任务                                     |
| Layer B / 里程碑集成验收                                | 里程碑范围不可见 IT；无人值守在实施波次内跑，交互调度推迟到全量 IT 阶段                                      | 看集成验收/最终交付 IT 结果即可                                              |
| Milestone IT Suite Plan / 里程碑集成编排                | 删前先加/浏览/列表等，尽量少步骤的测试顺序                                                                   | 一般由 AI 编排                                                               |
| 最终交付 / 完整交付                                     | 里程碑交付止于不可见 IT；最终交付可随时开。仅 1 个里程碑则直进全面 E2E；多个则先全量单测+全部 IT 再全面 E2E  | 里程碑过了可说「开始最终交付」；E2E 始终查全项目                             |
| `acceptance_layers_fused`                               | 把单任务完成和里程碑集成验收混成一团「全部完成」                                                             | 要求 AI 拆成两段再看                                                         |
| `failure_class` / `product_code` / `test_harness`       | 问题出在「产品本身」还是「检查脚本写错了」                                                                   | 一般不用回这些词；看收尾总结里的「对你有什么影响」即可                       |
| 回轨 / re-entry                                         | 实施中途又改了早期需求：先写回真源、把阶段退回到 Analysis/Plan，再往下做，而不是口头改完继续写代码           | 看进度板「回轨」和下一步；可以说「按回轨继续」或指出还要改哪里               |
| `entry_kind`                                            | 本回合挂哪条流水线入口：新项目 / 新里程碑 / 零散任务 / 继续 / 中途回改                                       | 一般不用你报这个词；看进度板下一步即可                                       |
| `midstream_change`                                      | 已经在 Plan/实施/交付中，又确认改了早期需求或验收                                                            | 等 AI 写回并回轨后，按「下一步」回到 Analysis/Plan                           |
| `schedule_policy` / 调度策略                            | 由交互/无人值守自动推导；交互=全项目 A+P+册后再实施；无人=方案 1 里程碑全 A→P+册再 I                         | 无需选择；说「无人值守」即切换                                               |
| Stage 6 集成战役                                        | 系统编排并跑不可见 IT（单测不可及边界+最小旅程）；**不问**你是否同意                                         | 读 Closing Summary；下一步是 E2E                                             |
| Stage 7 E2E 完结后                                      | 宣告可见旅程测完；交互可问是否还要手工测试（要则帮本地部署）；无人值守直接结案                               | 交互可说「要手工测试」或「直接收尾」                                         |
| Stage 8 项目结案                                        | 祝贺式收口 + 列出交给最终客户/上线仍缺步骤（未做不标绿）                                                     | 读遗留清单；外外部项按 resume 条件自行处理                                   |

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
