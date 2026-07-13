<!-- markdownlint-disable MD013 -->

# 73 执行计划：Task Delivery 与 Deferred Task Review 公共工作流

## 0. 文档状态

- 日期：2026-07-13
- 版本：V01
- 状态：reviewed draft，等待 Grill Finalizer；不是实施授权。
- 公开命名：Task Analysis、Task Plan、Task Delivery、Task Review、Task Completion Summary。
- 本地编号：`73` 只用于本地计划治理，不得进入公开 MCP enum、模板类型、工具提示或用户操作说明。
- 主文档：本文件是本轮 workflow 迭代唯一活动计划。
- Companion Artifacts：实施后同步 bundled workflow、shared skills、MCP 工具契约、测试和公开文档；不存在并行计划真值。

### 目标

建立一条可被普通任务、学习任务和软件开发任务共同使用的公共生命周期：

`Capture → Task Analysis → Task Plan → Execution → Task Delivery → Completion → Deferred Task Review`

其中：

- Capture 保持快速，不生成附件；
- Analysis 负责开始前的判断；
- Plan 负责执行前的承诺和节点；
- Delivery 负责实际交付事实；
- Review 负责过程效率、返工、知识和长期上下文；
- 完成任务与深度回顾默认解耦。

### 完成定义

1. 四阶段模板与可组合 Profile 完整。
2. Delivery 在完成前作为版本化任务附件写入并 readback。
3. 默认 finish 不自动生成深度 Review 或 Review Card。
4. 用户可在任务完成后独立发起 Review，并安全恢复部分成功的写入链。
5. Agent 始终以 Granoflow 最新状态为准，不覆盖其他设备的更新。
6. 公开语义、bundled/shared skills、工具描述、测试和长期文档一致。

## 1. 决策冻结

### 1.1 已确认决策

- 一个完整 base contract 服务所有任务；`learning` 与 `software_development` 是可组合的薄 Profile。
- 进入 Plan 或 Execution 的任务在完成前必须生成 Delivery；仅 capture 后取消、放弃或从未执行的任务不强制补写。
- 用户手工验收节点不阻塞后续安全执行；验收状态变化本身不重写 Delivery。
- Task Review 默认延后。只有用户明确要求“完成并回顾”时才走 explicit inline review compatibility。
- Review Card 始终委托唯一 card authoring owner，不在本 workflow 复制实现。
- Project Context 只有 `project_snapshot.yaml` 和 `project_rules.yaml`；不创建 Milestone YAML。
- active milestone 使用 description managed block；archived milestone 使用 `completionSummary`。
- 第一版不新增 `reviewedAt` 或 `reviewStatus` 数据库字段，用结构化 Review marker 区分状态。
- 旧 `taskReview` / `reviewCardDrafts` wire 参数本次不删除、不改型；patch 版本不得移除。
- 实际代码和运行态证明当前事实；active Project Rules、Specification 和 Decision Record 证明规范意图。冲突必须报告并闭环，不能静默选一边。

### 1.2 条件式跨项目决策

阶段 1 必须验证 running App 是否提供：

- task attachment 的条件式或幂等创建；
- completed task 的安全 `taskReview` 更新；
- revision conflict 返回与 readback；
- Project Context 与 Milestone managed context 的安全写入。

如果缺少其中任一能力，本计划允许补齐 App-owned Local HTTP API/capability，再同步 MCP。不得用 MCP 内部锁、CLI wrapper、SQLite 或 best-effort 覆盖来伪装强一致性。

该条件式扩展已经纳入本计划，不需要在阶段 1 通过后增加一次形式化用户批准。只有实际缺口要求改变本计划已冻结的 scope、数据模型、用户体验或不可逆行为时，才重新请求用户决策。

### 1.3 旧规则冲突分类

| 旧语义                                  | 新语义                                         | 分类                                    | 闭环                                                 |
| --------------------------------------- | ---------------------------------------------- | --------------------------------------- | ---------------------------------------------------- |
| finish 时自动写有意义的 `taskReview`    | 默认 Delivery 后完成，Review 延后              | `auto_resolved_as_design_change`        | 更新 bundled/shared workflow、README、安装演示与测试 |
| finish 时自动创建 Review Card           | 卡片只在独立 Review 中经 preview/approval 创建 | `auto_resolved_as_design_change`        | 删除默认自动指导，保留 explicit inline compatibility |
| MCP 保持薄封装、业务规则由 App/API 拥有 | 条件式写入能力缺失时补 App-owned API           | `auto_resolved_as_old_rule_still_valid` | 能力放在 App，不在 MCP 重写业务逻辑                  |
| secrets、权限和确认 fail closed         | Review/Delivery 增加更多持久化内容             | `auto_resolved_as_old_rule_still_valid` | 数据最小化、秘密扫描、确认 gate 和 readback 必须保留 |

## 2. 范围

### In Scope

- Task Delivery base template、两个薄 Profile 和 workflow。
- Task Review base template、两个薄 Profile 和 workflow。
- Task Completion Summary managed block。
- Project Context promotion entry contract。
- Task Plan 模板的 Profile、Delivery 节点与公开命名修订。
- finish 默认语义、explicit inline compatibility 和 deferred Review routing。
- bundled workflow、shared copilot/runner、README、安装演示、目录文案和测试同步。
- 条件式 App/API 能力补齐，仅在阶段 1 证明现有能力不足时启用。
- 旧长期规则、snapshot/spec/decision 文档与新语义的一致性回写。

### Out of Scope

- 新增 Review Queue UI 或任何 Flutter 页面、组件、布局和视觉设计。
- 自动判断情绪、人格、动机或主观效率分数。
- 自动把每个 Review 机械追加进 Project Context。
- 新建第二套 Review Card authoring。
- MCP 直接访问 SQLite/Drift，运行 App，截图或编排发布。
- 本轮自动发布 npm、MCP Registry 或其他目录。
- 删除 legacy finish 参数；未来移除需要 breaking version、caller audit、迁移说明和兼容期。

### 不得退化

- 快速插入任务仍不生成 Analysis/Plan/Delivery。
- Analysis 未 finalized 且 planning-ready 前不得规划。
- Plan 未明确确认前不得执行。
- 节点必须有可交付标准、验证证据和下游启动条件。
- 手工验收不阻塞后续安全节点。
- 节点完成和父任务完成仍由 App/NodeService 业务规则负责。

## 3. 公共语义与显示文本

| 语义                    | 定义                 | 公共文件                    | 机器状态示例               | 简体中文显示示例   |
| ----------------------- | -------------------- | --------------------------- | -------------------------- | ------------------ |
| Task Analysis           | 本任务开始前的判断   | `task-analysis-template.md` | `analysis_status`          | 任务分析           |
| Task Plan               | 本任务执行前的计划   | `task-plan-template.md`     | `plan_status`              | 任务计划           |
| Task Delivery           | 本任务实际交付事实   | `task-delivery-template.md` | `delivered_with_residuals` | 已交付（有遗留项） |
| Task Review             | 本任务过程回顾       | `task-review-template.md`   | `confirmation_required`    | 需要确认           |
| Task Completion Summary | 描述中的简短收尾索引 | managed marker block        | `pending/completed`        | 待回顾/已回顾      |

机器 enum 保持稳定、语言无关；用户界面或本地化回复使用语言对应的显示文本，不把下划线 enum 直接展示给普通用户。

### 用户旅程差异

- Task Delivery：回答“最后交付了什么、证据是什么、与原计划有何不同”。
- Task Review：回答“过程是否高效、哪里返工、以后如何做得更好、哪些知识值得长期保存”。
- Delivery 是完成前的事实 gate；Review 是完成后的可选独立工作，不得相互替代。

## 4. 文档时效与证据规则

所有模板必须在标题和 metadata 后显示简短作用域声明。

- Task Analysis：`Scope notice: This is pre-task analysis, not the project's current state. If later evidence conflicts, use the evidence-backed later record and preserve the difference.`
- Task Plan：`Scope notice: This is the pre-execution plan, not a completion record. Task Delivery governs what was actually delivered.`
- Task Delivery：`Scope notice: This records this task's delivery as of delivered_at. Later work may change it; verify current state against living context and actual evidence.`
- Task Review：`Scope notice: This reviews this task's process. Use Task Delivery for its result and verified living context for current project state.`
- Project/Milestone Context：`Freshness notice: Living context may lag behind implementation. Report conflicts and propose the required document or implementation update.`

### 判断当前事实

1. 当前代码、可重复测试、运行态和外部可验证状态；
2. 已检查 freshness 的 Project/Milestone living context；
3. 最新未 supersede 的 Task Delivery；
4. Task Plan；
5. Task Analysis。

后写文档不天然正确。证据不足或 stale 的文档不能覆盖更强事实。

### 判断规范意图

- active Project Rules、Specification 和 Decision Record 是规范依据。
- 代码偏离规范只证明当前实现偏离，不自动废止规范。
- conflict report 至少包含 conflicting statement、双方证据、推荐动作、更新目标和是否需要确认。

## 5. 模板 Contract

### 5.1 Profile 组合

四阶段使用同一个组合语义：

```yaml
profiles: [] | [learning] | [software_development] | [learning, software_development]
```

组合方式：

1. base template 始终完整加载；
2. 按 `learning`、`software_development` 的固定顺序追加已选择 Profile；
3. Profile 只增加领域字段和验收要求，不覆盖或删除 base 字段；
4. 同名要求合并为更强的共同 gate，不复制章节；
5. 不使用运行时 YAML include 或隐式模板继承。

### 5.2 Task Plan

- 删除 `project_73`、`project_76` 等公开类型。
- 每个执行节点必须有 Owner、Preconditions、Action、Deliverable、Delivery Standard、Completion Condition、Verification Evidence、Acceptance、Downstream Startup Requirements、Stop Conditions。
- 最终执行节点生成、上传并 readback Task Delivery。
- Plan 物质变化生成新版本；执行进度不改写 immutable Plan attachment。

### 5.3 Task Delivery

```yaml
document_type: task_delivery
schema_version: 1
task_id: <id>
profiles: []
delivery_version: <positive integer>
delivery_status: draft | delivered | delivered_with_residuals | awaiting_manual_acceptance | superseded
source_analysis: <attachment reference>
source_plan: <attachment reference>
supersedes: null | <prior attachment>
delivered_at: <timestamp>
based_on_task_updated_at: <timestamp>
content_sha256: <sha256>
acceptance_status_as_of: accepted | partially_accepted | awaiting_manual_acceptance | not_required
```

固定章节：Final Outcome、Deliverables、Differences From Analysis、Differences From Plan、Actual Change Surface、Verification Evidence、Manual Acceptance、Residuals And Deferred Work、Handoff And Usage、Traceability。

规则：

- 文件名为 `task-delivery-vNN.md`；读取附件列表后取最高版本加一。
- 上传前后按 task id、version 和 content hash 查重。
- 相同版本和相同 hash 是幂等重试；相同版本但不同 hash 是冲突，不得覆盖或删除任一附件，必须重新读取并生成下一版本或进入冲突处理。
- 实际交付事实材料变化时生成新版本并 `supersedes`；仅验收状态变化时只更新节点和 Task Completion Summary。
- 每个 deliverable 记录位置/标识、状态、证据和使用方式。
- Analysis/Plan 差异分类为 assumption invalidation、scope change、execution deviation 或 evidence change。

Learning Profile 追加能力基线、能力变化、独立证据、错误修正、剩余差距和延迟复习入口。

Software Development Profile 追加实际行为、代码/API/schema/UI delta、兼容/迁移、静态门禁、测试/build/runtime、发布状态、rollback 和文件/方法预算差异。

### 5.4 Task Review

结构化 Review 第一行固定为：

```html
<!-- granoflow-task-review:v1 -->
```

状态判定：

| `taskReview` 状态                 | 语义                  | 行为                                                    |
| --------------------------------- | --------------------- | ------------------------------------------------------- |
| 空                                | 未回顾                | 可创建结构化 Review                                     |
| 包含一个有效 marker               | 已结构化回顾          | 读取 operation state 后恢复或生成新版本化修订           |
| 非空且无 marker                   | 用户/旧 workflow 内容 | 先展示保留原文的 merge proposal 或明确 replace proposal |
| marker 重复、缺失闭合、倒序或嵌套 | 无法安全解析          | fail closed，要求人工处理                               |

固定章节：Outcome Assessment、Time Analysis、Time Evidence And Confidence、Rework And Waste、What Worked、Efficiency Problems、Next-Time Adjustments、Knowledge And Experience、Review Card Results、Project/Milestone Context Promotion、Residual Risks And Follow-ups。

```yaml
timezone: <IANA timezone>
attribution_method: telemetry | bounded_transcript_estimate | mixed | unavailable
evidence_coverage_ratio: <0..1 | unknown>
review_operation_id: <stable id>
review_steps:
  review_write: completed | deferred | confirmation_required | failed | unchanged
  cards: completed | deferred | confirmation_required | failed | unchanged
  project_context: completed | deferred | confirmation_required | failed | unchanged
  milestone_context: completed | deferred | confirmation_required | failed | unchanged
  completion_summary: completed | deferred | confirmation_required | failed | unchanged
```

时间字段：elapsed、discussion、AI execution、waiting、manual acceptance、rework。每项记录 value、confidence 和简短 evidence summary。

时间算法：

- `exact` 只来自 telemetry/session events；transcript 推算只能是 `estimated`。
- transcript 默认不跨越超过 5 分钟的无活动间隔；无法分类的剩余时间保持 unknown，不自动算 waiting。
- 并行 tool intervals 先合并为 wall-clock union；重叠按更具体、更强证据切成互斥区间。
- rework 是 discussion/AI execution 的标签和子集，不重复计入总时间。
- 用户对区间的明确修正优先。

效率建议必须包含 trigger、action、owner、expected benefit 和 validation。

Review 写入顺序：

1. draft/preview，取得 Review 正文确认；
2. 安全写入 `taskReview` 并 readback；
3. Review Card preview/approval/apply/readback；
4. Project Context promotion；
5. Milestone Context promotion；
6. Task Completion Summary 更新与最终 readback。

每个 material step 后持久化 operation state。重试必须从最新 Granoflow 状态恢复，已完成步骤不得重复创建卡片、附件或 YAML entry。

### 5.5 Task Completion Summary

公开名称使用 Task Completion Summary；内部 marker 冻结为 v1：

```html
<!-- granoflow-task-completion-summary:v1:start -->
## Task Completion Summary - Final outcome: - Delivery status: - Task Analysis: - Task Plan: - Task
Delivery: - Manual acceptance: - Review status: pending | completed - Deferred review steps: -
Residuals: - Next entry point:
<!-- granoflow-task-completion-summary:v1:end -->
```

无 marker 时可追加一个 block；一个合法 pair 只替换内部内容；重复、缺失、倒序或嵌套 marker 返回 `task_completion_summary_markers_invalid`，不得改写 description 其他内容。

Task 完成时默认 Review pending。带 Review marker 的正文写入并 readback 后可标 completed；cards/context 的 deferred 状态必须单独显示。

### 5.6 Project/Milestone Context Promotion

Project promotion entry：

```yaml
- id: <content-derived stable id>
  kind: snapshot | rule | decision | lesson | anti_pattern
  scope: project | milestone
  milestone_id: null | <id>
  summary: <short factual summary>
  rationale: <why it matters later>
  future_trigger: <when to recall it>
  recommended_action: <what to do>
  evidence:
    task_ids: []
    delivery_attachments: []
    review_cards: []
  first_observed_at: <timestamp>
  last_verified_at: <timestamp>
  status: active | superseded | retired
  supersedes: null | <stable id>
```

stable id 由 scope、milestone id、kind、来源 task id 和规范化语义摘要生成；随机 UUID 不能单独承担去重。

目标映射：current fact → snapshot；durable rule/boundary → rules；durable decision → decision entry；active-stage context → active milestone description；archived-stage summary → completionSummary；主动回忆知识 → Review Card；一次性流水账 → taskReview only。

Milestone managed block：

```html
<!-- granoflow-milestone-context:v1:start -->
Freshness: current | stale | partial | source_gap | reconcile_failed Last verified at:
<timestamp | unknown>
  Context:
  <bounded stage context>
    Evidence: <short references> <!-- granoflow-milestone-context:v1:end --></short></bounded
  ></timestamp
>
```

active milestone 只替换 description 中该 block；archived milestone 不改 description，只通过既有安全入口维护 `completionSummary`。

## 6. 并发、隐私与失败恢复

### 6.1 跨设备并发

- 长连接通知只是“状态可能变化”的信号，不能替代写前 read。
- 每次 attachment、taskReview、description、node、card、Project Context 或 Milestone Context material write 前重新读取目标。
- API 支持时必须发送 `expectedUpdatedAt`、revision 或 idempotency key。
- `409` 后重新读取，只重算受影响 diff；若最新状态改变已确认语义，重新确认该部分，禁止 last-write-wins。
- readback 验证语义结果，不只检查 HTTP success。

### 6.2 Capability fallback

若 attachment 或 taskReview 缺少安全条件式/幂等写入：

1. 停止对应 material write；
2. 保留本地草稿和 capability evidence；
3. 补 App-owned API/capability 与测试；
4. MCP 只暴露薄工具契约；
5. 能力 readback 通过后恢复原 operation。

不得降级为静默覆盖、无条件 replace、进程内锁或假定只有一个设备。

### 6.3 大小与数据最小化

- 阶段 1 读取 API advertized limits 或验证真实限制；计划不虚构固定数字。
- 超限时先压缩重复表达；仍超限则保留安全本地附件/摘要并报告，不静默截断证据或 marker。
- Delivery、Review、Card 和 Context 只保存派生区间和简短证据摘要，不复制原始聊天、完整 tool logs、屏幕内容或无关个人信息。
- token、OTP、恢复码、auth URL、环境秘密和凭据不得进入任何持久化产物。
- 未获授权读取的历史记为 evidence gap，不推测补全。

## 7. 影响面

### MCP Server

新增 references：

- `task-delivery-template.md`
- `task-delivery-profile-learning.md`
- `task-delivery-profile-software-development.md`
- `task-delivery-workflow.md`
- `task-review-template.md`
- `task-review-profile-learning.md`
- `task-review-profile-software-development.md`
- `task-review-workflow.md`
- `task-completion-summary-template.md`
- `project-context-promotion-entry.yaml`

修改：`skills/granoflow-agent-workflow/SKILL.md`、Plan/Review/Context references、`src/tools.ts`、相关测试、README 和公开 docs。

`granoflow_task_finish` 默认 guidance 改为 Delivery/Completion；legacy review 参数只在 explicit inline review 中转发。本次不增加重复 Review Card primitive。

### Shared Skills

同步 `granoflow-task-copilot` 与 `granoflow-task-runner` 的 routing、finish、review、card、safety 和 Plan workflow。优先指向 canonical bundled references，避免复制漂移。

本轮不修改本地 70–74 writer family 和 `project-doc-system` 的内部编号规则。

### App / Local HTTP API

默认预期无改动。仅当阶段 1 证明条件式/幂等 attachment 或 taskReview 能力缺失时，补 App-owned API/capability、冲突码和测试；不新增 UI，不默认新增数据库字段。

## 8. 分阶段实施

### 阶段 1：Capability 与规则基线

1. 记录 running App/version/capability surface。
2. 验证 completed task 的 taskReview 更新、marker preservation、revision conflict 和 readback。
3. 验证 task attachment list/create/readback、大小限制、条件式或幂等创建。
4. 验证 node、Review Card、Project Context 和 Milestone context 安全入口。
5. 扫描公开数字术语与旧自动 Review 语义。
6. 产出 capability evidence：endpoint、method、required fields、revision/idempotency、limits、error codes、readback、test path。

硬 gate：证据全部满足才进入阶段 2；能力缺失则走已批准的 App-owned 补齐路径。若缺口要求改变已冻结 scope/数据模型/用户体验，计划回到用户决策。

### 阶段 2：模板族与状态协议

1. 新增 Delivery/Review base、Profile、workflow。
2. 新增 Task Completion Summary 和 promotion entry。
3. 修订 Plan Profile 与 Delivery node。
4. 固定 marker parser、version/hash/stable-id 算法和显示文本映射。
5. 加入 scope/freshness notices。

### 阶段 3：完成与回顾 workflow

1. Delivery：read latest → diff Analysis/Plan → version/hash → safe upload → readback → completion summary。
2. Finish：Delivery 和节点 gate 满足后完成，默认不写 Review/cards。
3. Review：read latest → time/rework analysis → preview/confirm → resumable writes → final readback。
4. 所有写入实现 revision conflict、幂等恢复、privacy filtering 和 marker fail-closed。

### 阶段 4：MCP 契约与兼容

1. 更新 attachment 描述以支持 Analysis/Plan/Delivery。
2. 更新 finish description/dry-run guidance。
3. 保留 legacy inline payload 的 wire behavior。
4. 增加 deliver/review routing，不复制业务逻辑。

### 阶段 5：Shared 与公开文档同步

同步 copilot/runner、README、安装演示、directory listing 和必要 release checklist。把旧自动 Review 语义作为 design replacement 删除或改写，不能保留两套默认路径。

### 阶段 6：验证与交付

1. 运行静态/contract 测试和 `npm run check`。
2. 执行 Plan → Delivery → Completion → Deferred Review smoke。
3. 执行 409、其他设备更新、中途失败、重复 operation、secret redaction smoke。
4. 回读附件、task、nodes、taskReview、cards、completion summary 和 context。
5. 生成本次迭代 Task Delivery；若有对应 Granoflow task，上传并 readback。
6. 完成规则一致性闭环声明。

## 9. 测试清单与顺序

### 9.1 已存在、直接复用

- `tests/tools.test.ts`：tool registration、finish request sequence、legacy review import、attachment forwarding、node concurrency、Project Context capability/readback。
- `tests/api.test.ts`、`tests/config.test.ts`、`tests/setup.test.ts`：token redaction 和 API/config 安全基线。
- `scripts/release-preflight.mjs`：公开文件秘密字面量和过期文案扫描逻辑，可复用其模式但不把 release 当本轮授权。

### 9.2 需要修改

- `tests/tools.test.ts`
  - 默认 finish guidance 不再自动 Review/cards；
  - explicit inline legacy 参数继续原样转发；
  - attachment tool 描述包含 Delivery；
  - capability gap、409 与 readback guidance；
  - resource 列表包含新 references。
- 现有 bundled workflow contract assertions：把旧“automatic taskReview”断言改为 deferred Review 默认语义。

### 9.3 需要新增

新增 `tests/task-workflow-contracts.test.ts`，覆盖：

- 四阶段 scope notices；
- base-only、learning、software development、双 Profile 组合；
- Delivery filename/version/hash/supersedes；
- Task Review marker 四态：空、结构化、未标记历史内容、非法 marker；
- Task Completion Summary 与 Milestone managed block 幂等替换；
- time interval union、5 分钟 idle cap、rework 子集；
- Review 分步失败恢复；
- attachment/taskReview revision conflict；
- 手工验收后不生成新 Delivery；
- 同 operation 不重复 card/attachment/YAML entry；
- secret/transcript/tool-log redaction；
- Project/Milestone freshness 与 conflict report；
- 公开内容无 `project_73/project_76`。

若 conditional App/API 补齐被触发，阶段 1 evidence 必须先列出 App 仓库中“已有复用/需要修改/需要新增”的具体测试路径，再开始 App 修改。

### 9.4 执行顺序

实现前：

1. 对现有相关 Vitest 运行定向基线；
2. 运行 `npm run check`，记录与本任务无关的既有失败；
3. 完成 capability smoke，不写生产数据。

实现中：

1. 先写/更新 contract tests；
2. 再实现单一阶段；
3. 每阶段运行对应定向 Vitest；
4. App/API conditional change 先跑 App-owned 测试，再跑 MCP tests。

实现后：

1. `npm run check`，必须 exit 0，不允许绕过 lint/type/test 失败；
2. 定向秘密扫描和 public-number scan；
3. 隔离测试任务的真实 workflow smoke/readback；
4. cleanup/restore 测试数据并验证没有遗留污染。

## 10. 验收矩阵

| 验收项            | 通过条件                                                  | 证据层级                    |
| ----------------- | --------------------------------------------------------- | --------------------------- |
| 公共生命周期      | 四阶段模板、routing 和语义一致                            | 文件/contract test          |
| Profile           | 单独和组合均不重复、不削弱 base                           | contract fixture            |
| Delivery          | 事实、delta、evidence、manual acceptance、residuals 完整  | attachment readback         |
| Delivery 幂等     | 相同 operation 不重复；冲突不覆盖                         | fault-injection/readback    |
| Deferred Review   | finish 默认不写 Review/cards                              | Vitest + smoke              |
| Legacy inline     | 旧参数组合保持 wire contract                              | Vitest                      |
| Review marker     | 空/结构化/未标记/非法四态正确                             | parser fixture              |
| Review 恢复       | 任一步失败后从最新状态恢复且不重复                        | fault-injection             |
| 跨设备并发        | 409 后重算，不覆盖其他设备更新                            | conflict fixture + runtime  |
| 手工验收          | 不阻塞安全执行；状态变化不重写 Delivery                   | node/readback smoke         |
| Context promotion | 查重、确认、目标映射和 unchanged 正确                     | YAML/managed block readback |
| 隐私              | 无 secrets、原始 transcript 或完整 tool logs              | redaction tests/scan        |
| 规则一致性        | 旧自动 Review 语义已从长期/public docs 移除               | reference scan              |
| 数据库/UI         | 未触发时无 schema/UI diff；触发例外有独立证据             | git diff/capability report  |
| MCP gate          | `npm run check` exit 0                                    | command output              |
| 真实流程          | Delivery、Completion、Review 和 Context 均从 App readback | runtime evidence            |

实现层证据只能支持“已实现/已覆盖”；运行 smoke 才能支持“流程可运行”；真实用户/真实环境成功才支持“正式通过”。

## 11. 风险、阻塞与回滚

### 局部阻塞

- Card apply 等待批准：保留 preview/operation id，继续其他已确认步骤。
- rules/decision promotion 等待确认：保留 proposal，允许 factual/non-conflicting 步骤继续。
- Review 中途失败：保存逐步状态，下一次从最新状态恢复。
- 409：重读并重算受影响 diff；新状态改变语义时只重新确认该部分。
- running App 不可用：完成静态/fixture 工作，真实 readback 保持 blocker。

### 全局阻塞

- completed task 无法安全更新 taskReview；
- Delivery attachment 无法条件式/幂等写入和 readback，且 App-owned 补齐路径不可实施；
- 必须破坏已发布 wire contract 才能实现新默认；
- 无法防止 Review/Context 写入 secrets 或覆盖其他设备内容；
- 阶段 1 capability evidence 未通过，却没有本计划允许的安全补齐路径。

### 回滚

- bundled/shared templates 和 routing 可恢复旧 references，但不得删除已生成历史附件。
- 工具 description/guidance 可回退；legacy 参数无需数据迁移。
- 错误 Delivery 用新版本 `supersedes`，不删除审计历史。
- conditional App/API 变更必须有向后兼容 feature/capability gate；MCP 只在 capability advertized 后使用。
- 真实 smoke 使用隔离测试任务，结束后 cleanup/restore 并 readback。

## 12. Grill-Me Handoff

### auto_resolved_from_doc

- Delivery 版本：读取最新附件，最高版本加一；hash/版本冲突 fail closed。
- Review 恢复：operation id 和逐步状态写入结构化 taskReview，每步 readback。
- 时间归因：互斥 wall-clock interval；rework 是子集；无证据保持 unknown。
- Milestone：active description managed block，archived completionSummary，无 Milestone YAML。

### auto_resolved_from_context

- legacy finish 参数继续兼容，但不再是默认 workflow。
- 公开内容禁止本地数字类型；内部 writer family 不改名。
- 当前 MCP 已有 task/node revision 能力，但 attachment/taskReview 强并发能力必须由阶段 1 实测。
- Project Context canonical attachments 只有 snapshot/rules 两个。

### user_confirmed

- capability 缺失时，允许补 App-owned 条件式/幂等 API，再同步 MCP。
- 接受 docs-modify 建议 A1–A10；拒绝额外阶段批准、虚构大小数字和假设 PUT endpoint。

### requires_user_decision

- 当前无。

### deferred_non_blocking

- 真实 API limits、endpoint method 和 App test paths：阶段 1 evidence 中确定。
- npm/MCP Registry 发布：不属于本计划实施授权，另行发起 release。

后续 Grill-Me 只追问实施后新矛盾、未被本矩阵覆盖的问题，或会改变 scope/ownership/验收的真实新决策。

## 13. 收尾

- 实施完成后生成 Task Delivery，而不是把本计划改写成完成报告。
- 更新 Project Snapshot：仅记录实际已实现的 workflow/capability。
- 更新 Project Rules/Specification：记录语义名、数字隔离、Delivery/Review 边界、card owner 和并发不变量。
- 更新 Decision Record：记录完成与回顾解耦、legacy compatibility 和条件式 App-owned capability 决策。
- 规则一致性闭环声明必须为“已一致”，或明确列出未一致原因、owner 和下一步；不能以 residual risk 代替。
- 实施完成后再执行 post-iteration review、长期文档回补、最终测试和真实 readback。
- git commit、push 和 release 均需用户另行授权；release 必须从云端版本计算最小可发布版本。
