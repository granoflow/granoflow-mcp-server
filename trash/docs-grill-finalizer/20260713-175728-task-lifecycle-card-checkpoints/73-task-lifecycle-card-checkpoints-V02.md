# 73 执行计划：贯穿任务生命周期的阶段化卡片工作流

> 本文是任务开始前的执行计划，不代表项目当前实际完成情况；若与本任务后续交付文档冲突，以交付文档为准。
> 交付文档只描述本次任务的实际交付，不保证后续任务没有继续修改；若与项目或里程碑长期文档冲突，以更新后的项目或里程碑文档为准。
> 项目、里程碑和长期文档可能更新不及时；若它们与实际代码或运行行为冲突，实施者必须显式报告并提出回写方案，持续恢复文档与代码的一致性。

## 0. 文档状态

- 日期：2026-07-13
- 版本：V02
- 状态：candidate-final；已应用 docs-modify 确认账本，等待 Grill Finalizer 终审；终审前不授权实施。
- 上游结论：卡片不是 Task Review 的附属产物，而是从 Task Analysis 开始参与任务的动态知识层。
- 生命周期：`Analysis → Plan → Execution → Delivery → Completion → Deferred Review`。
- 卡片主链：`read linked cards → search similar cards → classify → preview → approve → apply → readback`。
- 唯一 authoring owner：bundled `granoflow-review-card-draft`；其他 workflow 只决定何时调用和如何记录阶段结果，不复制搜索、去重、质量、确认或写入逻辑。
- 公开兼容：保留现有 `review_card`、`granoflow_review_card_*` 工具名，不把本地数字编号写入公开类型或提示。

## 1. 目标与完成定义

### 1.1 目标

1. Analysis 开始时读取并使用已有卡片；来源和授权满足门槛时，可在 Analysis 正式创建、关联或修订卡片。
2. Plan、Execution、Delivery 和 Deferred Review 分别执行 Card Checkpoint；Completion 不创建独立 checkpoint，只读取并确认 Delivery 结果。
3. 不同阶段可以使用或产生不同知识；同一知识优先关联或修订既有卡片，不按阶段制造重复卡片。
4. 项目任务和收集箱任务都可安全制卡；不得为了制卡要求用户先选择项目或里程碑。
5. 全程保留来源、证据、去重、preview、operation-level approval、apply、stale conflict 和 practice-ready readback 门禁。

### 1.2 完成定义

- bundled workflow 与 shared skills 使用同一个阶段化 Card Checkpoint contract。
- Analysis 模板记录实际使用的卡片、正式操作、候选和未处理项。
- App authoring 支持所有现有且未删除的任务；收集箱任务的新卡进入现有未归类牌组。
- capability 明确声明 `taskRequired=true`、`projectTaskRequired=false`、`inboxTaskAuthoring=true` 和 `uncategorizedDeckFallback=true`。
- 各阶段结果可判定为 `changed | unchanged | deferred | conflict | not_applicable`，具体 link/create/update 由 operations 记录。
- Completion 只读验证 Delivery checkpoint，并允许在明确 deferred 原因时完成任务；普通完成不自动启动深度 Review。
- App、MCP server、bundled/shared skills、OpenAPI、测试和公开文档一致。

## 2. 决策冻结

### 2.1 卡片在生命周期中的角色

卡片同时承担：

- **输入知识**：已有知识、项目规则和历史经验用于改进当前阶段判断。
- **输出记忆**：本阶段出现且达到证据与授权门槛的新知识、纠错或经验被保存，供后续阶段和未来任务使用。

每个具有 Card Checkpoint 的阶段遵循：

```text
读取最新任务状态与已关联卡片
→ 搜索可能相关的卡片
→ 以可靠卡片辅助本阶段判断
→ 判断是否发生 material knowledge/card delta
→ link / update / create / unchanged / deferred
→ preview + operation-level approval
→ apply + practice-ready readback
→ 在阶段文档或节点证据中记录结果
```

读取与搜索是只读操作，可在询问用户前执行。搜索命中、任务完成、分析确认或一般兴趣都不授权卡片写入。

### 2.2 各阶段职责

| 阶段            | 主要输入                            | Card Checkpoint 职责                                                 | 典型结果                                                          |
| --------------- | ----------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Analysis        | 任务、材料、项目上下文、已有卡片    | 建立知识基线；用已有卡片辅助分析；把来源可靠且当前需要的知识正式制卡 | link、source-backed create、证据性修订                            |
| Plan            | Analysis final、方案、规则、依赖    | 检查决策边界、术语、操作规则和风险知识                               | project-rule card、decision-boundary update、unchanged            |
| Execution       | 节点证据、错误、工具结果、用户修改  | 只在知识或经验发生实质变化时处理卡片；临时日志不制卡                 | correction update、verified knowledge、evidence-backed experience |
| Delivery        | 实际交付、验证、Analysis/Plan delta | 让卡片与实际交付一致，记录差异的接受、推翻或延期状态                 | reconcile、update、link、deferred                                 |
| Completion      | Delivery checkpoint、节点状态       | 不创建独立 checkpoint；验证 Delivery 状态并生成只读摘要              | confirmed、deferred summary                                       |
| Deferred Review | 全过程、验收、返工与时间证据        | 最终去重、质量审计和经验沉淀；不是第一次集中制卡                     | durable experience、merge/update、final audit                     |

### 2.3 证据门槛

- **来源知识**：用户材料、本地文件、规范、官方文档、可靠查询或任务内部真值文档支持结论时，可在 Analysis 创建。
- **项目规则**：仅在规则已确认或存在 active spec/decision evidence 时制卡；候选方案不能写成已生效规则。
- **历史经验**：Analysis 可关联或创建已由历史事实支持的经验卡，但必须标明证据来自过去事件。
- **本任务经验**：只有事件已发生、未来触发明确且通过 experience worthiness gate 后才能创建。
- **假设、待确认问题和预测**：只进入 candidate，不创建正式卡片。
- **临时命令、一次性状态、秘密和无未来触发的活动日志**：不得制卡。

Learning 任务可在 Analysis 创建用于当前学习的知识卡，但不新增“问题卡”“前测卡”等数据库类型；仍使用现有 note/card schema。

### 2.4 跨阶段知识溯源

知识可能在一个阶段出现、另一个阶段验证，再在后续阶段固化。相应 operation 或 candidate evidence 必须记录：

```yaml
origin_phase: analysis | plan | execution | delivery | deferred_review
validated_phase: null | analysis | plan | execution | delivery | deferred_review
applied_phase: null | analysis | plan | execution | delivery | deferred_review
evidence: []
```

这些字段属于阶段文档和节点证据，不进入卡片数据库，不替代卡片自身来源信息。

### 2.5 授权边界

- 每个阶段可以把多个卡片操作合成一个 preview batch。
- 卡片 apply 必须携带未变化且未过期的 `previewToken`、`previewHash` 和明确的 `approvedOperationIds`；局部修改还可携带 `approvedFieldsByOperation`。
- Analysis 初稿批准与卡片 operation 批准是两个独立授权。允许同一条用户回复同时表达两者，但 agent 必须分别解析和记录。
- 推荐组合确认格式：

  ```yaml
  analysis_draft: approve
  card_operations:
    approved_operation_ids: [card-op-1, card-op-2]
    approved_fields_by_operation: {}
  ```

- 只说“写入分析初稿”“按分析推荐执行”或批准上一阶段，都不能推导出当前卡片操作授权。无法明确解析时，不调用 apply。
- 后续阶段发现任务、卡片或 shared note 发生跨设备变化时，旧 preview 失效，必须重新读取、比较和 preview。

### 2.6 去重、冲突与修订

- 相同知识优先 `link_existing` 或 `update_existing_and_link`。
- related 但回答不同问题的卡片允许并存，不因语义接近自动合并。
- 来源知识与项目经验冲突时，分别保存适用范围并说明边界，不用局部经验覆盖通用事实。
- 修改 shared note 时展示所有受影响 cards/tasks，并继续使用 field-level approval。
- 无法安全判断修订还是新建时返回 `conflict` 或 `deferred`，不得静默写入。
- 卡片历史继续使用 App 当前同步与实体历史能力；本计划不伪造独立版本档案。

## 3. 收集箱任务能力合同

### 3.1 当前缺口与可复用能力

当前 App capability 为 `projectTaskRequired: true`，且 authoring persistence 通过 task → milestone → project inner join 判断资格，导致收集箱任务返回 `project_task_required`。

现有底层能力已经满足解除该人工门禁的基础：

- task-note/task-card links 直接以 `task_id` 关联任务。
- `ensureDeckForTask()` 使用任务上下文并已有 `ensureUncategorizedDeck()` fallback。
- authoring preview/apply 已具备 integrity、expiry、partial approval、stale conflict、shared-note impact 和 readback。

### 3.2 新合同

- authoring 只要求 task 存在且未删除，不要求 project 或 milestone。
- preview envelope 保留 `taskId`，`projectId` 允许为 `null`。
- 缺少 `taskId` 使用既有 `invalid_arguments`；missing/deleted task 统一返回：

  ```json
  {
    "ok": false,
    "error": {
      "code": "task_not_found",
      "message": "Task was not found."
    }
  }
  ```

- `task_not_found` 与旧 `project_task_required` 互斥；新版本不得继续以 project gate 拒绝现有收集箱任务。
- 收集箱任务创建的新卡进入现有未归类牌组，并正常建立 task/note/card links。
- 任务后来归入项目时，不自动移动既有 immutable deck assignment；迁移策略不在本轮范围。
- capability 固定为：

  ```yaml
  taskRequired: true
  projectTaskRequired: false
  inboxTaskAuthoring: true
  uncategorizedDeckFallback: true
  ```

## 4. Card Checkpoint Contract

所有具有 checkpoint 的阶段使用同一个文档结构，不新增任务数据库字段：

```yaml
card_checkpoint:
  phase: analysis | plan | execution | delivery | deferred_review
  checked_at: <timestamp>
  based_on_task_updated_at: <timestamp>
  input_card_ids: []
  operations:
    linked: []
    created: []
    updated: []
  unchanged_card_ids: []
  candidates:
    - summary: <minimal summary>
      origin_phase: <phase>
      evidence_needed: []
      revisit_phase: <phase>
  status: changed | unchanged | deferred | conflict | not_applicable
  evidence: []
  deferred_reason: null | <reason>
  readback: completed | not_required | failed
```

规则：

1. `status=changed` 表示 `operations.linked/created/updated` 至少一项非空；允许同一批次同时包含多种操作，不使用优先级或复合状态字符串。
2. `unchanged` 表示检查已完成且无需调整，不等于跳过检查。
3. `created/updated/linked` 只有 App apply 和 practice-ready readback 后才能填写。
4. `input_card_ids` 只记录实际参与本阶段判断的卡片，不表示它们由本阶段创建。
5. `candidates` 只保存尚未达到证据或授权门槛的最小摘要、缺少的证据和下次检查阶段。
6. `deferred` 必须写明缺少来源、用户未批准、capability 不可用或当前阶段不宜固化的原因。
7. `conflict` 表示卡片或 shared note 出现无法自动合并的变化；必须重新 preview 或请求判断。
8. `readback=failed` 时不得把对应操作记入成功数组；checkpoint 保持 conflict/deferred，并记录恢复入口。

Completion 不产生上述结构，只生成：

```yaml
completion_card_summary:
  delivery_checkpoint_status: <status>
  linked_card_ids: []
  deferred_items: []
  delivery_checkpoint_verified: true | false
```

## 5. 阶段工作流调整

### 5.1 Task Analysis

- 七维问题前读取 task export 中的 linked cards，并搜索 similar cards。
- AI 推荐明确引用影响判断的卡片。
- Analysis 初稿加入 Card Checkpoint，记录知识基线、输入卡、正式操作和 candidates。
- Analysis 初稿授权和 card apply 授权按 2.5 分别解析。
- Grill-Me 推翻知识假设时重新执行 checkpoint；需要写卡时重新 preview。

### 5.2 Task Plan

- 继承 Analysis checkpoint，不重复创建相同知识。
- 增加 `Knowledge And Card Plan`：预计使用的知识、可能变化和触发 checkpoint 的条件。
- 每个执行节点增加 `Knowledge/Card Delta Trigger`；只有新概念、纠错、规则变化或可复用经验才触发节点内检查。
- Plan confirmation 不批准执行阶段未来出现的卡片操作。

### 5.3 Execution

- 节点开始前读取最新 task、nodes、linked cards 和同步变化。
- 节点完成时判断是否发生 material knowledge/card delta。
- 有 delta：调用唯一 card owner，并把 checkpoint 结果写入 node evidence/handoff。
- 无 delta：记录 `unchanged`，不展示空卡片问卷。
- 卡片批准等待不阻塞与其无关的安全节点；当前节点能否完成仍由其 Delivery Standard 决定。

### 5.4 Unattended Runner

- 无人值守 runner 可以读取、搜索和生成 preview，但不得自行构造或推导 `approvedOperationIds`。
- 遇到待批准 preview 时，将 checkpoint 记录为 `deferred`，原因固定为 `confirmation_required`，并提供后续人工入口。
- runner 不调用 apply，不把 preview 当成写入成功，不阻塞与该写入无关的安全节点。
- contract tests 必须证明 unattended 模式无法越过 approval gate。

### 5.5 Delivery 与 Completion

- Delivery 增加 `Card Reconciliation`，逐项记录 Analysis/Plan 预期与实际交付的差异。
- 每项差异标记 `accepted | superseded | deferred`，附证据和对应 operation IDs。
- Delivery checkpoint 允许 deferred，但必须说明原因和后续入口。
- Completion 只验证 Delivery checkpoint 并生成只读 Card Summary，不启动 Deferred Review，不批准新卡片。

### 5.6 Deferred Review

- 读取各阶段 checkpoint，不假定此前没有制卡。
- `Review Card Results` 是最终审计：去重、纠错、经验门槛、shared-note impact、遗漏和复习入口。
- 只为全过程才证明成立的经验、此前 deferred candidate 或最终纠错创建/修订卡片。
- 卡片步骤可以 `completed | unchanged | deferred | confirmation_required | failed | not_applicable`，不改变任务已完成状态。

## 6. 跨仓修改范围与 Companion Plans

### 6.1 开工闸门

任何代码修改前，各仓必须建立并相互链接 companion plan：

| 仓库                 | 责任                                                                       | 前置依赖                               | 独立验收                                                          |
| -------------------- | -------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------- |
| Granoflow App        | task authoring context、inbox capability、错误码、deck fallback 与底层测试 | 无；先实施                             | project/inbox preview/apply/readback，missing/deleted fail closed |
| Granoflow MCP server | capability forwarding、card owner、阶段模板和公开契约                      | App contract 已冻结；可用 fixture 先行 | `npm run check`、工具兼容、capability contract                    |
| Shared skills        | 生命周期路由、Card Checkpoint、unattended 行为                             | bundled owner contract 已冻结          | structure/forward tests，无复制 authoring 逻辑                    |

主计划负责跨仓顺序与端到端验收；companion plan 负责各仓具体文件、测试、回滚和交付标准。

### 6.2 Granoflow App

预计修改：

- `ai_agent_review_card_authoring_persistence.dart`
- `ai_agent_review_card_authoring_service.dart`
- `local_http_api_ai_agent_tools.dart`
- authoring/capability/Local HTTP API tests
- OpenAPI、Local HTTP API spec 与相关长期文档

实现边界：

- 将 `projectTask()` 替换为 task-owned context lookup，project/milestone nullable。
- preview/apply 只验证 task 存在且未删除。
- 继续调用 `ensureDeckForTask()`，不复制 deck fallback。
- 保留 preview integrity、expiry、partial approval、stale conflict、shared-note impact 和 readback。

### 6.3 Granoflow MCP server

预计修改：

- `granoflow-review-card-draft` 与 `granoflow-agent-workflow`
- Analysis、Plan、Delivery、Review、Completion templates/references
- `src/tools.ts` 的必要 capability/tool 说明
- bundled contract、tool forwarding 与 capability tests
- README、安装演示或目录文案中的冲突事实

必须保持现有 `granoflow_review_card_similar`、`granoflow_review_card_authoring_preview`、`granoflow_review_card_authoring_apply` 名称和请求兼容。

### 6.4 Shared skills

预计修改：

- `/Users/will/code/skills/granoflow-task-copilot/`
- `/Users/will/code/skills/granoflow-task-runner/`

shared skills 只路由阶段和记录 checkpoint；所有卡片判断与写入委托 bundled card owner。

### 6.5 Out of scope

- Card Practice UI、任务 UI、Review Queue 或新卡片页面。
- 新卡片数据库类型、phase 字段、operation-history 表或 migration。
- 自动迁移收集箱任务卡片到后来加入的项目牌组。
- 未经 operation-level approval 自动 apply。
- 把每个节点、日志或命令机械转换成卡片。
- 删除或重命名公开 MCP 卡片工具。
- npm、MCP Registry、App 发布或部署。

## 7. 数据、同步与结构预算

### 7.1 数据库与 UI

- 数据库表结构无变化；不新增 migration、schemaVersion、索引、触发器、回填或 sync serializer。
- UI 无变化；preview/approval 仍通过现有 MCP/Agent 对话表面完成。
- 若测试证明现有 FK、sync 或 deck assignment 无法支持 inbox task，停止实施、报告证据并修订计划，不得临时绕过。
- 若安全批准或冲突展示必须新增 UI，计划退回 draft，并先给出界面与复用组件方案。

### 7.2 最新状态与 stale 处理

- 每阶段开始前重新读取 Granoflow 最新 task export、linked cards、card/note updated state。
- preview token/hash 只对其封装的 snapshot 有效；发现 task/card/shared note 更新后必须重新 preview。
- 不另造 MCP 侧缓存或版本系统；以 App 返回的最新 snapshot、preview integrity 和同步结果为真值。

### 7.3 代码结构预算

| 文件/职责             | 预算                                                    | 拆分规则                               |
| --------------------- | ------------------------------------------------------- | -------------------------------------- |
| authoring persistence | 优先替换 project-only lookup，task context 方法 ≤ 35 行 | 只做数据库映射                         |
| authoring service     | 新逻辑净增长目标 ≤ 40 行，单方法优先 ≤ 80 行            | 按 preview/apply validation 真职责拆分 |
| capability builder    | 净增长目标 ≤ 15 行，单方法 ≤ 50 行                      | 只声明能力                             |
| tests                 | 每个测试只验证一个 contract，helper 优先 ≤ 60 行        | inbox/project/missing/stale 分 fixture |

不得机械搬文件、按行数切 helper、创建无领域职责的 util 或为绕过门禁拆分代码。

## 8. 实施顺序与节点交付标准

### Phase 1：建立 companion plans 与基线

1. 三仓分别建立 companion plan 并互相链接。
2. App 建立 project、inbox、missing/deleted、stale card/note fixtures。
3. 运行相关现有测试并记录实施前基线。
4. 用失败测试证明 inbox 当前被 `project_task_required` 拒绝，同时证明 `ensureDeckForTask(inbox)` 可返回未归类 deck。

交付标准：现状缺口、可复用能力、各仓责任和基线结果均可重复；足以启动 App contract 修改。

### Phase 2：解除 App project gate

1. 改为 existing task context lookup，允许 nullable project/milestone。
2. preview/apply 使用 task existence gate，missing/deleted 返回 `task_not_found`。
3. inbox create/link/update 复用未归类 deck 与 task links。
4. 更新 capability、OpenAPI/spec 和 App tests。
5. 回归 project task、preview integrity、partial approval、stale conflict、shared-note impact 和 readback。

交付标准：project/inbox 均能 preview/apply/readback；missing/deleted fail closed；足以让 MCP 使用新 capability。

### Phase 3：更新 bundled card owner 与 MCP contract

1. 扩展 `granoflow-review-card-draft` 为任意任务阶段的唯一 authoring owner。
2. 增加阶段输入、证据门槛、溯源、同知识修订、跨设备 reread 和 checkpoint contract。
3. 删除“必须属于项目”的旧规则，改为读取 capability；旧 App 声明 project-only 时安全 deferred。
4. 保留 search → classification → preview → approval → apply → readback 主链。
5. 更新工具说明、templates、contract tests 和公开事实文档。

交付标准：唯一 owner 定义卡片质量与写入；公开工具保持兼容；足以供 shared skills 路由。

### Phase 4：接入生命周期与无人值守规则

1. Analysis 在提问前读取/搜索卡片，并在初稿和 Grill-Me 后记录 checkpoint。
2. Plan 增加 Knowledge And Card Plan 与节点 delta trigger。
3. Execution 只在 material delta 时调用 owner。
4. Delivery 增加 reconciliation；Completion 生成只读 summary。
5. Deferred Review 改为各阶段结果的最终审计。
6. shared copilot/runner 接入同一 contract；unattended runner 遇到 preview 必须 deferred。

交付标准：各阶段结果可判定；无重复 owner；普通完成不自动启动 Review；足以启动跨仓真实冒烟。

### Phase 5：跨仓一致性与真实冒烟

1. 运行三仓全部相关门禁。
2. 使用一个可清理 project test task 和一个可清理 inbox test task 执行：Analysis create → Plan unchanged/update → Execution correction → Delivery reconcile → Deferred Review audit。
3. 每次 apply 后检查 task links、deck assignment、card/note 内容、practiceReady 和 task export linked cards。
4. 验证 stale preview、partial approval、unattended deferred、Completion summary 和 rollback path。
5. 清理测试任务、卡片、notes、links 和未归类 deck assignments；清理前后记录数量，失败时报告残留 ID，不触碰非测试数据。
6. 扫描旧“只在 Review/finish 制卡”“project task required”和过期 Completion 语义。

交付标准：project/inbox 两条路径均完成真实 readback，无重复卡、无未经批准写入、无测试数据残留、无第二套 authoring owner。

## 9. 测试计划

各 companion plan 必须把以下矩阵映射为具体文件和命令。

| 分类         | 测试意图                                                                                                                                                                              |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 已存在可复用 | project task preview/apply/readback、preview integrity/expiry、partial approval、stale conflict、shared-note impact、deck fallback、MCP tool forwarding                               |
| 需要修改     | project-only rejection fixture、capability snapshot、错误码断言、card owner/Analysis/Plan/Delivery/Review contracts                                                                   |
| 需要新增     | inbox create/link/update、missing/deleted `task_not_found`、nullable projectId、Completion summary、复合 operations→changed、跨阶段 provenance、unattended no-apply、真实冒烟 cleanup |

实施前基线：运行所有“已存在可复用”和即将修改的测试，记录失败只能是已知 project-only 缺口。

实施后全集合：

- App：项目规则要求的 analyze、format、authoring、deck、Local HTTP API、sync/backup 相关测试。
- MCP server：`npm run check`，bundled contract、tool forwarding、capability tests。
- Shared skills：结构、引用、forward tests，以及 unattended approval guard。
- 跨仓：project/inbox 真实 smoke、stale/partial approval、readback 和 cleanup。

## 10. 验收判定

| 验收项            | 通过条件                                                                      |
| ----------------- | ----------------------------------------------------------------------------- |
| Analysis 使用卡片 | 提问前读取 linked/similar cards，并引用其影响                                 |
| Analysis 正式制卡 | 可靠知识完成 preview、明确 operation approval、apply、practice-ready readback |
| 复合操作          | 同批 link/create/update 记录为 `status=changed`，operations 明细完整          |
| 跨阶段溯源        | origin/validated/applied phase 与 evidence 可回读                             |
| 去重与修订        | 同知识优先 link/update；stale card/shared note 使旧 preview 失败              |
| 收集箱任务        | inbox task 可 authoring 并进入未归类 deck                                     |
| 项目任务回归      | project/milestone deck 与 task link 行为不变                                  |
| 缺失任务          | missing/deleted 返回 `task_not_found`，不创建孤立数据                         |
| 双重授权          | Analysis 批准不等于 card apply；无 approvedOperationIds 不写入                |
| 无人值守          | runner 不构造批准，preview 进入 deferred/confirmation_required                |
| Completion        | 不创建独立 checkpoint，只验证 Delivery 并生成只读 summary                     |
| Deferred Review   | 审计各阶段结果，只补全过程才成立的经验或 deferred candidate                   |
| API 兼容          | 公开 MCP 工具名和请求兼容，capability 准确                                    |
| DB/UI             | 无 migration、schemaVersion 或 UI 代码变化                                    |
| 规则一致性        | App、MCP、bundled/shared skills、OpenAPI、README 与实际代码一致               |
| 真实冒烟          | project/inbox 全链成功，测试数据清理完成                                      |

## 11. 风险与停止条件

- **卡片过度生成**：以未来触发、证据门槛、相似卡搜索和 unchanged 控制。
- **分析被打断**：只读搜索先行；写操作合并为阶段 batch；无变化不展示空问卷。
- **错误知识过早固化**：假设留在 candidates；正式卡必须有来源或已发生经验。
- **同卡反复改写**：只有 material delta 才 update。
- **shared note 扩散**：展示受影响 cards/tasks，使用 field-level approval。
- **跨设备并发**：每阶段从最新状态开始，stale preview fail closed。
- **无人值守越权**：禁止推导批准；只能 deferred。
- **测试数据污染**：测试 ID 可识别、范围隔离、计数核对并提供失败残留清单。
- **范围扩大**：若必须 migration、新 UI 或改变 deck assignment 不变量，立即停止并把计划退回 draft。
- **授权扩大**：分析/计划确认不代表卡片 apply、发布、发送、删除或外部操作授权。

## 12. 回滚

1. 回退 shared/bundled lifecycle checkpoint 文案、模板和测试。
2. 恢复 App `projectTaskRequired=true` 与 project-only authoring gate。
3. 回退 capability、错误码、OpenAPI 和 MCP 描述。
4. 运行 project-only、inbox rejection、capability snapshot 和 shared-reference 回滚验证。
5. 本轮无 migration，不需要数据库 schema 回滚。
6. 已经用户明确批准创建的 inbox 卡片和 links 属于用户数据，不自动删除。
7. 回滚后新的 inbox authoring 请求返回明确 capability limitation，不伪报成功。

## 13. 长期文档与规则冲突闭环

实施前扫描当前 72/spec/snapshot/decision-log 中以下旧语义：

- 卡片只能在 Review/finish 阶段创建；
- authoring 必须是 project task；
- Completion 自动触发 Review 或创建卡片；
- phase provenance 必须持久化到卡片数据库。

分类规则：

- 与用户新确认的“Analysis 即可制卡、全生命周期复查、inbox 可制卡”冲突的旧规则属于 `auto_resolved_as_design_change`，必须更新或下架。
- preview/approval、stale conflict、shared-note impact、immutable deck assignment、同步与数据安全规则属于 `auto_resolved_as_old_rule_still_valid`，必须保留。
- 发现无法以 90% intent-confidence 分类的长期规则时，停止对应实施节点并提交用户决策。

实施完成后按事实更新 bundled templates、card owner、shared skills、Local HTTP API/OpenAPI/spec、README 和项目/里程碑文档。代码与长期文档冲突必须显式报告并给出回写方案。

## 14. Grill-Me Handoff

### auto_resolved_from_doc/context

- 卡片从 Analysis 开始参与任务，并在各阶段动态复查。
- Completion 不创建独立 checkpoint。
- inbox task 复用未归类牌组，不要求项目。
- missing/deleted task 使用现有 `task_not_found` 契约。
- phase provenance 保存在阶段文档和节点证据，不新增数据库字段。
- unattended runner 不得自行批准 card apply。

### auto_resolved_as_design_change

- “只在 Review/finish 制卡”被全生命周期 Card Checkpoint 取代。
- “project task required”被“所有现有未删除 task 可 authoring”取代。

### auto_resolved_as_old_rule_still_valid

- preview、operation-level approval、partial approval、stale conflict、shared-note impact、readback 和 immutable assignment 继续有效。

### requires_user_decision

- 无。

### deferred_non_blocking

- 收集箱任务后来进入项目时是否迁移卡片牌组；保持独立 deck-policy 议题，本轮不处理。
- npm、MCP Registry、App 发布或部署；不属于本实施计划。

---

## 任务标准补充（2026-07-16）

1. 试图解决什么问题？
   以本文件原有目标和任务描述为准，解决该文档所对应的工程、流程或治理问题。

2. 准备用什么方式解决？
   按本文件既有分析、决策和计划执行；本补充不改变原方案，只把任务记录标准化。

3. 需要哪些前置条件？当前是否齐备？
   前置条件：本文件记录的上下文、相关代码/仓库、运行环境和必要授权。
   当前状态：对应任务已完成，前置条件视为已齐备；无法由历史证据确认的细节保留为待分析。

4. 预计需要多少实际工作时间？估计依据和不确定性是什么？
   历史工时未知。历史文档没有可靠的实际专注工作时间记录，不以日历耗时倒推；估计依据和不确定性待分析。

5. 达成什么条件视为验收通过？
   文档中的目标、交付物和验证条件已满足，Granoflow 对应任务状态为 done；具体以原文档列出的验收证据为准，未列明时以交付物可回读、质量检查通过且无未声明残余问题为准。
