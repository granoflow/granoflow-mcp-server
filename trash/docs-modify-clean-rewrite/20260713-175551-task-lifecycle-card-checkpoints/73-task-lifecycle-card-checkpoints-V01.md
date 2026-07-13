# 73 执行计划：贯穿任务生命周期的阶段化卡片工作流

## 0. 文档状态

- 日期：2026-07-13
- 版本：V01
- 状态：draft，等待评审与确认；本文件不授权实施。
- 上游结论：卡片不是 Task Review 的附属产物，而是从 Task Analysis 开始参与任务的动态知识层。
- 生命周期：`Analysis → Plan → Execution → Delivery → Completion → Deferred Review`。
- 卡片主链：`read linked cards → search similar cards → classify → preview → approve → apply → readback`。
- 唯一 authoring owner：bundled `granoflow-review-card-draft`；其他 workflow 只决定何时调用，不复制搜索、去重、质量、确认和写入逻辑。
- 公开兼容：保留现有 `review_card`、`granoflow_review_card_*` 工具名，不把本地 `73` 编号写入公开类型或提示。

### 目标

1. Analysis 开始时读取并使用已有卡片；在 Analysis 阶段即可正式创建、关联或修订卡片，不必等到任务完成。
2. Plan、Execution、Delivery 和 Deferred Review 分别执行 Card Checkpoint，判断关联卡片是否需要新增、修订、重新关联或保持不变。
3. 不同阶段允许使用不同知识和经验，但对相同知识优先修订或关联既有卡片，避免按阶段制造重复卡片。
4. 收集箱任务与项目任务都能安全制卡；不为了制卡强迫用户先选择项目或里程碑。
5. 卡片仍遵守来源、证据、去重、preview、operation-level approval、apply 和 practice-ready readback 门禁。

### 完成定义

- bundled workflow 和 shared skills 采用同一个阶段化 Card Checkpoint contract。
- Analysis 模板明确记录已使用、创建、修订、关联、候选和未处理的卡片。
- App authoring 支持现有未删除的收集箱任务，并将其卡片放入现有“未归类”牌组。
- capability 明确声明 `taskRequired=true`、`projectTaskRequired=false` 和 inbox authoring 支持。
- 每一阶段可判定输出 `linked | created | updated | unchanged | deferred | conflict | not_applicable`。
- 任务完成仍不自动触发深度 Review，但完成前能证明 Delivery 阶段 Card Checkpoint 已处理或明确 deferred。
- App、MCP、bundled/shared skills、测试和公开文档一致。

## 1. 决策冻结

### 1.1 卡片的生命周期角色

卡片同时承担两种职责：

- **输入知识**：已有知识、项目规则和历史经验用于改进当前阶段判断。
- **输出记忆**：本阶段出现且已经达到证据门槛的新知识、纠错或经验被保存供后续阶段和未来任务使用。

因此每个阶段的顺序固定为：

```text
读取任务最新状态与已关联卡片
→ 搜索可能相关的其他卡片
→ 把可靠卡片作为本阶段输入
→ 判断本阶段知识变化
→ link / update / create / unchanged / deferred
→ preview + 用户确认
→ apply + practice-ready readback
→ 在本阶段文档中记录结果
```

读取和搜索是只读操作，可以在询问用户前执行。搜索结果、任务完成、分析确认或此前一般性兴趣都不授权卡片写入。

### 1.2 各阶段职责

| 阶段            | 主要输入                            | Card Checkpoint 的职责                                                   | 典型输出                                                              |
| --------------- | ----------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| Analysis        | 任务、材料、项目上下文、已有卡片    | 建立知识基线；用已有卡片辅助七维分析；把来源可靠且当前需要的知识正式制卡 | link、source-backed create、对旧卡的证据性修订                        |
| Plan            | Analysis final、方案、规则、依赖    | 检查计划引入的决策边界、专业术语、操作规则与风险知识                     | project-rule card、decision-boundary update、unchanged                |
| Execution       | 节点证据、错误、工具结果、用户修改  | 在知识或经验发生实质变化时处理卡片；临时日志不制卡                       | correction update、new verified knowledge、evidence-backed experience |
| Delivery        | 实际交付、验证、Analysis/Plan delta | 让卡片与实际交付一致；纠正被实现证据推翻的旧结论                         | reconcile/update/link/deferred                                        |
| Completion      | Delivery readback、节点状态         | 只确认 Delivery Card Checkpoint 已形成明确状态；不自动启动深度 Review    | completed/unchanged/deferred 状态索引                                 |
| Deferred Review | 全过程、验收、返工与时间证据        | 最终去重、质量审计和经验沉淀；不是第一次集中制卡                         | durable experience、merge/update、final card results                  |

### 1.3 卡片证据门槛

- **来源知识**：用户提供的材料、本地文件、规范、官方文档、可靠查询或任务生成的内部真值文档已经支持该结论时，可在 Analysis 创建。
- **项目规则**：只有规则已经确认或存在 active specification/decision evidence 时才制卡；候选方案不能写成已生效规则。
- **历史经验**：Analysis 可以关联或创建已有历史事实支持的经验卡，但必须标明证据来自过去事件，不得伪装成本任务产出。
- **本任务经验**：只有相应事件已经发生、未来触发明确且达到 experience worthiness gate 后才能创建；通常发生在 Execution、Delivery 或 Review。
- **假设、待确认问题和预测**：只记录为 card candidate，不创建正式卡片。
- **临时命令、一次性状态、登录信息、秘密和无未来触发的活动日志**：不创建卡片。

Learning 任务可以在 Analysis 创建用于当前学习的知识卡，但不新增“问题卡”“前测卡”等数据库类型。仍使用 App 已支持的 note/card schema；问题、前测和练习目标只是卡片内容用途，不是新持久化 enum。

### 1.4 写入确认

- 每个阶段可把本阶段的多个操作合成一个 preview batch。
- 用户可以批准全部或只批准指定 operation IDs/fields。
- Analysis 文档确认不自动等于卡片批准；允许提供组合回复，例如“按推荐写入分析初稿并批准卡片操作 A、B”，但必须能区分两种授权。
- 前一阶段的批准不覆盖后一阶段新出现的卡片或修改。
- 已授权的 batch apply 仍必须使用未变化且未过期的 preview token/hash。
- 后续阶段发现卡片发生跨设备变化时，旧 preview 失效，必须重新读取、重新比较和重新 preview。

### 1.5 重复、冲突与修订

- 相同知识优先 `link_existing` 或 `update_existing_and_link`，不按 Analysis/Plan/Delivery 阶段各创建一张。
- related 但回答不同问题的卡片允许并存，不能因语义接近自动合并。
- 来源知识与项目经验冲突时，不用局部经验覆盖通用来源事实；分别保存适用范围并在 note 中解释边界。
- 修改 shared note 时必须展示所有受影响卡片和任务，并继续使用 field-level approval。
- 无法安全判断是修订还是新建时，返回 `conflict` 或 `deferred`，不静默写入。
- 卡片历史仍由 App 当前同步与实体历史能力决定；本计划不伪造独立版本档案。

## 2. 收集箱任务能力结论

### 2.1 当前阻塞

running App contract 当前公开：

```text
projectTaskRequired: true
```

`AiAgentReviewCardAuthoringPersistence.projectTask()` 通过 task → milestone → project 的 inner join 判断 authoring 资格；收集箱任务会被 `project_task_required` 拒绝。

### 2.2 已有底层能力

现有数据和 service 已经具备收集箱制卡所需基础：

- `review_task_note_links` 和 `review_task_card_links` 直接以 `task_id` 关联任务，并不要求 project id。
- `ReviewCardDeckSystemWriter.ensureDeckForTask()` 使用 left join；任务没有 project 时会调用 `ensureUncategorizedDeck()`。
- “未归类”系统牌组及 card assignment 已存在。
- authoring preview/apply 已经以 `taskId` 为主键，并具有 token/hash、partial approval、shared-note impact 和 readback。

因此推荐只解除 authoring service 的人工 project gate，复用现有 task link 和未归类牌组，不新增数据库字段或迁移。

### 2.3 新 contract

- authoring 要求目标 task 存在且未删除，不要求 project/milestone。
- preview envelope 的 `projectId` 允许为 `null`；同时保留 `taskId`。
- missing/deleted task 返回稳定 `task_required` 或等价新错误；不得继续使用会误导用户的 `project_task_required`。
- 收集箱任务创建的新卡分配到现有未归类牌组，并与 task/note 建立正常关联。
- 任务以后被归入项目时，本计划不自动移动既有 immutable deck assignment；是否迁移属于独立 deck-policy 设计，不在本轮暗中处理。
- capability 改为：

```yaml
taskRequired: true
projectTaskRequired: false
inboxTaskAuthoring: true
uncategorizedDeckFallback: true
```

## 3. 阶段化 Card Checkpoint Contract

所有阶段使用相同结果结构；可写入阶段文档，不新增 task 数据库字段：

```yaml
card_checkpoint:
  phase: analysis | plan | execution | delivery | review
  checked_at: <timestamp>
  based_on_task_updated_at: <timestamp>
  input_card_ids: []
  operations:
    linked: []
    created: []
    updated: []
  unchanged_card_ids: []
  candidates: []
  status: linked | created | updated | unchanged | deferred | conflict | not_applicable
  evidence: []
  deferred_reason: null | <reason>
  readback: completed | not_required | failed
```

规则：

1. `input_card_ids` 记录实际参与本阶段判断的已关联卡片，不代表这些卡片由本阶段创建。
2. `candidates` 只保存尚未达到证据或授权门槛的最小摘要，不得伪装成已写卡片。
3. `created/updated/linked` 只有 App apply 和 practice-ready readback 后才能填写。
4. `unchanged` 必须表示完成了检查且无需调整，不等于跳过检查。
5. `deferred` 记录缺少来源、用户未批准、capability 不可用或当前阶段不宜固化的原因。
6. `conflict` 表示卡片或 shared note 出现无法自动合并的变化；必须重新 preview 或请求用户判断。
7. phase provenance 保存在 Analysis/Plan/Delivery/Review 文档及 execution node evidence 中；本轮不为卡片表新增 phase 字段。

## 4. 文档与节点调整

### 4.1 Task Analysis

- 在提出七维问题前读取 task export 中已关联卡片，并搜索相关卡片。
- AI 推荐必须明确引用哪些已有卡片影响了判断。
- Analysis 初稿加入 `Card Checkpoint`，记录知识基线、已使用卡片、正式操作和候选。
- 用户授权写分析初稿时可以同时批准一个明确定义的 card batch，但两种授权必须分别可解析。
- Grill 发现知识假设错误时，重新执行 checkpoint；需要修卡时再次 preview。

### 4.2 Task Plan

- Plan 继承 Analysis Card Checkpoint 结果，不重复创建相同卡片。
- 新增 `Knowledge And Card Plan`：列出预计使用的知识、可能出现的知识变化和何时触发 checkpoint。
- 每个执行节点增加 `Knowledge/Card Delta Trigger`，只在出现新概念、纠错、规则变化或可复用经验时触发节点内 checkpoint；不得为每个节点机械制卡。
- Plan confirmation 不自动批准执行阶段的未来卡片操作。

### 4.3 Execution

- 节点开始前读取最新 task、nodes、linked cards 和跨设备变化。
- 节点完成时先判断是否发生 material knowledge/card delta。
- 有 delta：执行 card owner 流程并把结果写入 node evidence/handoff。
- 无 delta：记录 `unchanged`，不展示空卡片问卷。
- 卡片 preview/approval 等待不会阻塞与其无关的安全执行节点；当前节点能否完成仍由其 Delivery Standard 决定。

### 4.4 Task Delivery 与 Completion

- Delivery 增加 `Card Reconciliation`，列出实际交付使用和产生的卡片、与 Analysis/Plan 的差异、未处理候选和冲突。
- 完成前要求 Delivery checkpoint 状态可判定；`deferred` 允许完成，但必须写明原因和后续入口。
- Completion Summary 增加当前卡片状态、已关联数量/标识和 deferred 项。
- Completion 仍不自动启动 Deferred Review，也不自动批准新卡片。

### 4.5 Deferred Task Review

- Review 读取各阶段 checkpoint，而不是假定此前没有制卡。
- `Review Card Results` 改为最终审计：去重、纠错、经验门槛、shared-note impact、遗漏和后续复习入口。
- Review 只为全过程才证明成立的经验、此前 deferred 的候选或最终纠错创建/修订卡片。
- Review 卡片步骤可以 `completed | unchanged | deferred | confirmation_required | failed | not_applicable`，不影响已完成任务状态。

## 5. 修改范围

### 5.1 Granoflow App

预计修改：

- `lib/core/services/ai_agent_review_card_authoring_persistence.dart`
- `lib/core/services/ai_agent_review_card_authoring_service.dart`
- `lib/core/local_http_api/local_http_api_ai_agent_tools.dart`
- 对应 authoring service、capability 和 Local HTTP API tests
- 相关 Local HTTP API/OpenAPI/spec 文档

实现边界：

- 把 `projectTask()` 改为 task-owned authoring context lookup，允许 nullable project/milestone。
- preview/apply 只验证 task 存在和未删除。
- 继续调用 `ensureDeckForTask()`；不在 API 层复制 deck fallback 业务逻辑。
- 保留 preview integrity、expiry、partial approval、stale conflict、shared-note impact 和 readback。

### 5.2 Granoflow MCP server

预计修改：

- `skills/granoflow-review-card-draft/SKILL.md`
- `skills/granoflow-agent-workflow/SKILL.md`
- Analysis、Plan、Delivery、Review template/workflow/profile references
- Task Completion Summary template
- `src/tools.ts` 中卡片工具说明或 capability guard（仅在现状需要时）
- bundled contract tests、tool forwarding/capability tests
- README、安装演示或目录文案中的事实冲突

必须保留现有 `granoflow_review_card_similar`、`granoflow_review_card_authoring_preview`、`granoflow_review_card_authoring_apply` 名称和参数兼容。

### 5.3 Shared skills

预计修改：

- `/Users/will/code/skills/granoflow-task-copilot/`
- `/Users/will/code/skills/granoflow-task-runner/`

shared skills 只路由阶段和记录 checkpoint；所有卡片判断与写入仍委托 bundled card owner。

### 5.4 Out of scope

- Card Practice UI、任务 UI、Review Queue 或新的卡片页面。
- 新卡片数据库类型、phase 字段、operation-history 表或 migration。
- 自动移动收集箱任务卡片到后来加入的项目牌组。
- 未经确认自动 apply 卡片操作。
- 把每个节点、日志、命令或任务都机械转换成卡片。
- 删除或重命名现有公开 MCP 卡片工具。
- npm、MCP Registry、App 发布或部署。

## 6. 数据库与 UI 判断

### 数据库表结构：无变化

依据：

- task-note/task-card link 已直接支持任意现有 task id。
- 未归类 deck 和 task-based deck resolver 已存在。
- 新 phase/checkpoint 信息进入阶段文档和 node evidence，不进入新表或字段。
- 不新增 migration、schemaVersion、索引、触发器、回填或 sync serializer。

如果实施测试证明现有 FK、sync 或 deck assignment 无法支持收集箱 task，必须停止本 73、报告证据并先修订数据库方案，不能临时绕过。

### UI：无变化

依据：

- 本轮修改 Agent workflow、Local HTTP API capability 和既有 authoring service。
- 不改变页面布局、组件、显隐、空态、错误态或 App 用户可见交互。
- preview/approval 仍通过现有 MCP/Agent 对话表面完成。

如果需要新增 UI 才能安全批准、显示冲突或迁移 deck，本 73 必须回到 draft 并先给出界面草图与复用组件判断。

## 7. 代码结构预算

App 预计修改现有文件，不新增大型 service：

| 文件/职责                                                                     | 文件目标                                               | 方法目标                                                                    | 拆分规则                                                     |
| ----------------------------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `ai_agent_review_card_authoring_persistence.dart`：task/card 持久化查询与写入 | 修改后不显著增加总行数，优先替换旧 project-only lookup | task context lookup ≤ 35 行                                                 | 只做数据库映射，不加入阶段判断                               |
| `ai_agent_review_card_authoring_service.dart`：preview/apply 编排             | 新增逻辑净增长 ≤ 40 行                                 | 单方法优先 ≤ 80 行；超过时按 preview validation/apply validation 真职责拆分 | 不复制 deck 或 workflow 规则                                 |
| `local_http_api_ai_agent_tools.dart`：capability advertisement                | 净增长 ≤ 15 行                                         | 单 capability builder ≤ 50 行                                               | 只声明能力，不执行业务判断                                   |
| tests                                                                         | 每个测试只验证一个 contract                            | helper 优先 ≤ 60 行                                                         | inbox/project/missing/stale 分 fixture，不复制完整数据库装配 |

不得机械搬文件、按行数切 helper、创建无领域职责的 util，或为了绕过门禁而拆分。接近软限制时先重新划分 service/persistence/capability 边界。

## 8. 实施步骤

### Phase 1：冻结 fixture 与 capability

1. 在 App 建立 project task、inbox task、missing/deleted task、跨设备 stale card/note fixtures。
2. 证明 inbox task 当前返回 `project_task_required`，并证明 `ensureDeckForTask(inbox)` 返回未归类 deck。
3. 为新 capability 和错误语义先写失败测试。
4. 在 App 仓写 companion plan，引用本 73，声明无 DB/UI 变化。

验收：现状缺口与底层可复用能力都有可重复证据。

### Phase 2：解除 App project gate

1. 将 persistence lookup 改为 existing task context，允许 nullable project/milestone。
2. preview/apply 改为 task existence gate。
3. inbox create/link/update 使用现有未归类 deck 和 task links。
4. 更新 capability 与 Local HTTP API/spec 文档。
5. 验证 project task 行为、preview token/hash、partial approval、stale conflict 和 readback 无回归。

验收：project 与 inbox task 均能 preview/apply/readback；missing/deleted task fail closed。

### Phase 3：更新唯一 card owner

1. 将 `granoflow-review-card-draft` 从“完成/回顾制卡”语境扩为任意任务阶段的 authoring owner。
2. 增加阶段输入、证据门槛、同知识修订、跨设备 reread 和 checkpoint result contract。
3. 删除“必须属于项目”的旧规则，改为读取 capability；旧 App 仍声明 project-only 时安全 deferred，不假装成功。
4. 保留 search → AI classification → preview → approval → apply → practice-ready readback 主链。

验收：只有一个 owner 定义卡片质量和写入；其他 workflow 不复制其规则。

### Phase 4：接入生命周期各阶段

1. Analysis 在七维问题前读取/搜索卡片，并在初稿和 Grill 后记录 checkpoint。
2. Plan 增加 Knowledge And Card Plan 与节点 delta trigger。
3. Execution 在 material knowledge delta 时调用 owner，无 delta 记录 unchanged。
4. Delivery 增加 Card Reconciliation；Completion Summary 增加卡片状态。
5. Review 改为各阶段结果的最终审计，而不是第一次制卡。
6. 同步 shared copilot/runner 和 unattended runner；无人值守环境不能替用户批准 card apply。

验收：每个阶段都能正确产生 linked/created/updated/unchanged/deferred/conflict，且普通完成不自动启动 Review。

### Phase 5：一致性与真实冒烟

1. 运行 bundled contract tests 和 shared skill structure/forward tests。
2. 运行 App 静态门禁和 authoring/Local HTTP API tests。
3. 用一个 project task 和一个 inbox task 做真实流程：Analysis create → Plan unchanged/update → Execution correction → Delivery reconcile → Review final audit。
4. 每次 apply 后检查 task links、deck assignment、card/note 内容、practiceReady 和 task export 中 linked cards。
5. 扫描旧“只在 Review/finish 制卡”“project task required”公开语义。

验收：两类任务都完成全链 readback，无重复卡、无未经批准写入、无第二套 authoring owner。

## 9. 验收判定表

| 验收项            | 通过条件                                                                         |
| ----------------- | -------------------------------------------------------------------------------- |
| Analysis 使用卡片 | 初始分析在提问前读取 linked/similar cards，并能引用其影响                        |
| Analysis 正式制卡 | 可靠知识可在 Analysis preview、批准、apply、practice-ready readback              |
| 阶段复查          | Plan、Execution、Delivery、Review 都输出可判定 checkpoint 状态                   |
| 经验门槛          | 当前任务尚未发生的预测不能被写成 experience card                                 |
| 去重              | 同知识跨阶段优先 link/update，不按阶段重复创建                                   |
| 修订安全          | stale card/shared note 使旧 preview 失败并要求重新 preview                       |
| 收集箱任务        | inbox task 可创建/关联/修订卡片并进入未归类 deck                                 |
| 项目任务回归      | 原 project/milestone deck 与 task link 行为不变                                  |
| 缺失任务          | missing/deleted task fail closed，不创建孤立 card/note                           |
| 用户确认          | 无批准 operation ID 不执行 apply；阶段批准不跨阶段继承                           |
| Completion 边界   | Delivery checkpoint 可 deferred，但 completion 不自动启动 Review 或 card apply   |
| Review 职责       | Review 最终审计各阶段结果并补全过程经验，不重复创建已有卡                        |
| API 兼容          | 现有 MCP 工具名和请求兼容，capability 准确反映 inbox 支持                        |
| DB/UI             | 无 migration、schemaVersion、UI 代码或页面变化                                   |
| App 门禁          | 项目规则要求的 analyze、format、tests、rules/static gates 通过                   |
| MCP 门禁          | `npm run check` 通过                                                             |
| Shared skills     | 格式、结构、引用和适用 forward tests 通过                                        |
| 真实冒烟          | project/inbox 两个 fixture 完成阶段化 create/update/unchanged/reconcile/readback |

## 10. 风险与停止条件

- **卡片过度生成**：以未来触发、来源/经验门槛、相似卡搜索和 unchanged 结果控制；不要求每阶段一定写卡。
- **分析被制卡打断**：搜索只读先行；写操作合并为阶段 batch，一次 preview/approval；无变化不展示空问卷。
- **错误知识过早固化**：假设留在 candidates；正式卡必须有来源或已发生经验；后续阶段强制 reconcile。
- **同卡多阶段反复改写**：只有 material knowledge delta 才 update；措辞偏好不触发无意义 revision。
- **shared note 扩散影响**：展示全部受影响 cards/tasks，并使用 field-level approval。
- **收集箱 deck 语义不清**：复用现有未归类 deck，不自动创建项目或移动牌组。
- **跨设备并发**：每阶段从最新 task export/card snapshot 开始；stale preview fail closed。
- **App 能力缺口扩大**：如果必须迁移 DB、新增 UI 或改变 deck assignment 不变量，停止实施并修订本 73。
- **授权扩大**：分析/计划确认不代表卡片 apply、发布、发送、删除或外部操作授权。

## 11. 回滚

1. 回退 bundled/shared lifecycle checkpoint 文案和测试。
2. 恢复 App `projectTaskRequired=true` 与原 authoring task gate。
3. 回退 capability advertisement 和相关 MCP 描述。
4. 不需要数据库回滚；本轮无 migration。
5. 已通过明确批准创建的 inbox 卡片和 task links 保留为用户数据，不自动删除；必要时由现有卡片管理流程处理。
6. 回滚后 inbox task 的新 authoring 请求返回明确 capability limitation，不伪报成功。

## 12. 文档回写

实施完成后检查并按事实更新：

- bundled Task Analysis、Task Plan、Task Delivery、Task Review 和 Completion Summary templates/workflows；
- bundled card authoring owner；
- shared copilot/runner；
- Local HTTP API capability/OpenAPI/spec；
- MCP README、安装演示和目录文案；
- 如无新的长期不变量，不额外创建数字编号公开文档；如形成稳定 deck policy，再单独更新长期 spec/decision record。

## 13. 待评审问题与 AI 推荐

当前没有阻止本计划进入 Grill 的未决产品问题。AI 推荐如下：

1. **Analysis 阶段正式制卡，但仍需 card-operation approval。** 原因：提前制卡与防止静默写入可以同时成立。
2. **每阶段必须检查，但不要求每阶段写卡。** 原因：`unchanged` 是正常成功结果，可避免卡片膨胀。
3. **收集箱卡进入现有未归类 deck。** 原因：底层能力已经存在，无需强制项目归属或新增 schema。
4. **不持久化 card phase 字段。** 原因：阶段文档、node evidence 和 task-linked readback 已足以追溯；新增字段会不必要地扩大 DB/sync 范围。
5. **任务后来归入项目时不自动迁移 deck assignment。** 原因：现有 assignment 具有独立不变量，迁移策略应另行设计和确认。
