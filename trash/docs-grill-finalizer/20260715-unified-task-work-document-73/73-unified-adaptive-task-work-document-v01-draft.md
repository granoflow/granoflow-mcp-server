# 73 实施计划：统一自适应 Task Work Document

Status: ready for review

Date: 2026-07-15

Source decisions:

- 用一个统一的 Task Work Document 取代独立 Task Analysis 与 Task Plan 文档家族。
- Analysis、Planning、Execution 继续保持独立语义和确认状态，不因物理文档合并而合并授权。
- 所有任务只强制保留 Outcome、Evidence、Scope、Risk、Next Action 五项最小核心。
- 其他段落按明确触发条件出现，不生成大量空标题或“当前无”。
- 小任务允许 `planning_status: not_required`；复杂度、风险或不确定性增加时，文档原位生长并进入 Planning。
- Task Delivery 继续独立，记录实际发生的结果，不能与事前判断混写。

## 用户目标

降低小任务的治理成本：一个明确、低风险、容易回滚的小 Bug 或文案修正，不应被迫
生成两份长文档、经历两次重复继承和维护两个 active attachment 指针。同时，普通和
复杂任务仍必须保留分析判断、计划确认、执行授权、不可变版本和交付证据。

最终体验应是：任务简单，统一文档自然很短；任务暴露复杂性时，同一文档按照触发
条件增加上下文、Profile、Skill、节点、依赖、授权、回滚和 Grill，而不是切换模板。

## 设计替换范围

本计划有意替换当前“Task Analysis 文档 + Task Plan 文档”的双文档设计。以下旧规则
不再作为新任务写入路径：

- 两个独立模板；
- 两个独立 active attachment 身份；
- Plan 重复继承 Analysis 的 Outcome、Evidence、Boundaries 和 Risks；
- 所有基础段落一律存在并填写“当前无”；
- 所有可执行任务都必须生成独立 Plan 文件。

以下规则继续有效：

- Analysis、Planning、Execution 是不同阶段；
- Analysis 确认不授权 Planning 或 Execution；
- Planning 确认不等于执行指令；
- 用户必须另行指示宿主实施唯一 active、已确认、hash-verified 的 Work Document；
- 发布、登录、密钥、付费、删除、外发、commit、push 等保留独立授权；
- App attachment 继续不可变，重大变化创建新版本并 readback；
- Task Delivery 和 Deferred Task Review 继续独立。

## 适用性裁剪

### 数据库与迁移

结论：无变化。

Task Work Document 仍使用现有 workflow Markdown attachment、task description managed
block、expected task revision、idempotency key 和 SHA-256 readback。不新增 App 表、字段、
索引、migration、schemaVersion、同步 serializer 或旧数据回填。历史 Analysis/Plan
attachment 保持可读，不做数据迁移和批量改写。

### UI

结论：无变化。

不修改 Granoflow App 页面、组件、布局、状态、错误态或用户可见文案。文档由宿主
Agent 通过现有 MCP attachment 工具创建和读取，不建设新的文档编辑 UI，因此无需
UI 草图或视觉验收。

### Local HTTP API 与 MCP TypeScript 工具

结论：无变化。

现有 attachment add/read、task description update/readback 和 node batch 工具足以承载
统一文档。新增 bundled Markdown reference 会被现有动态 manifest 自动发现；不修改
endpoint、`src/tools.ts` 或 `src/workflow-resources.ts`。若实施发现必须新增 App/API
状态字段或 MCP 运行时编排，停止并回到 Analysis，不得把业务状态机塞进 MCP。

## 统一文档与版本身份

### 文档类型

新增唯一新写入模板：

```text
task-work-document-template.md
```

建议 front matter：

```yaml
document_type: task_work
schema_version: 1
task_id: <id>
work_version: <positive integer>
supersedes: null | <prior task_work attachment>
profiles: [] | [learning] | [software_development] | [...future profiles]
analysis_status: draft | awaiting_confirmation | confirmed
decision: proceed | needs_input | user_action | split | redefine | defer | abandon | completion_audit
planning_status: not_assessed | not_required | draft | awaiting_confirmation | confirmed
execution_status: not_started | authorized | executing | blocked | completed
created_at: <timestamp>
updated_at: <timestamp>
```

`execution_status` 是该不可变版本创建时的阶段快照；实际节点进度继续由 Granoflow
nodes 和 task managed summary 负责，不因进度变化覆盖 attachment。

### 一个文档家族，不是覆盖同一附件

统一表示一个 active Task Work Document 家族，不违反 attachment 不可变规则：

```text
简单任务：
  task-work-v01
    analysis_status: confirmed
    planning_status: not_required

需要计划的任务：
  task-work-v01  分析确认检查点
       ↓ superseded by
  task-work-v02  在同一结构中加入 Planning，计划确认检查点

实施中发现重大变化：
  task-work-v03  修订相关核心字段/计划并重新确认
```

任意时刻只有一个 active Work Document。版本上传后必须读取 App-owned content/hash；
新版本验证成功后才能切换 active 指针。Finalizer 只能重写本地 working copy，不能
覆盖或移动 App attachments。

历史独立 Analysis/Plan attachment 保持原样，只用于 legacy read。新任务和重大修订
只写 `task_work`，不再创建新式独立 Analysis/Plan。

## 最小核心与条件化扩展

### 五项永远存在

所有 Work Document 必须包含：

```markdown
## Outcome

## Evidence

## Scope

## Risk

## Next Action
```

每项可以只有一句，但不能省略：

- Outcome：完成后什么变为真；
- Evidence：什么证据能够排除假成功；
- Scope：本次做什么以及必要的最小非目标；
- Risk：当前实质风险，低风险任务可写一句 `Low — <reason>`；
- Next Action：当前状态允许的下一步，不展开未经确认的实施细节。

这五项是最低控制面，不等于完整 Analysis 或 Plan 问卷。不得因任务简单而只写标题，
也不得用通用套话填充。

### 按触发条件出现

| 可选段落                      | 触发条件                                                  |
| ----------------------------- | --------------------------------------------------------- |
| Trigger / Reproduction        | 问题触发、复现方式或当前/预期行为会改变判断               |
| Context / Unknowns            | 背景材料、事实/推断区分或未知信息可能改变决策             |
| Alternatives / Decision       | 存在两个以上真实方案、需要方向选择或任务应拆分/停止       |
| Capability And Skill Routing  | 确实需要外部或专业 Skill                                  |
| Profile Additions             | 领域存在基础核心无法覆盖的固定证据或风险                  |
| Database / Migration          | 涉及 schema、旧数据、迁移、同步或回填                     |
| UI / Manual Acceptance        | 涉及页面、交互、视觉、设备侧或主观验收                    |
| API / Compatibility / Release | 涉及公开契约、调用方、包、注册表或部署表面                |
| Authorization Matrix          | 涉及登录、发布、付费、密钥、删除、外发等独立授权          |
| Recommended Approach          | 需要说明实施路径，且 Planning 已经开始                    |
| Execution Nodes               | 需要两个以上可独立交付/验收的步骤，或需要 Granoflow nodes |
| Dependencies And Handoffs     | 节点之间存在前置、并行或启动契约                          |
| Verification Plan             | Evidence 需要多种门禁、真实运行或人工验收                 |
| Rollback / Stop Conditions    | 失败不能简单撤销、风险会扩大或存在停止阈值                |
| Grill Review                  | 存在方向不确定、假成功、高风险或复杂依赖                  |
| Knowledge / Card Checkpoint   | 生命周期规则触发卡片搜索、候选或写操作                    |

不适用的段落不出现，不写空表格，也不写一串“当前无”。Profile 仍可组合，但只给
当前文档添加触发后的领域要求，不复制基础核心。

## 小任务 Token 与上下文预算

轻量与否按任务影响和不确定性判断，不按项目大小、仓库大小或预计代码行数判断。
一个大仓库里的明确局部修正可以很轻；一个小项目里的权限或迁移改动仍然必须进入
Planning。

### 最小充分写作

所有 Work Document 遵守：

> 每个段落只写足以支持当前决定、验证证据和下一阶段的内容；不复述任务描述、聊天
> 记录、其他段落、Skill 正文或项目通用背景。

对 `planning_status=not_required`：

- task-specific 正文软目标不超过 250 个中文字符或约 400 tokens；固定 front matter、
  marker 和 attachment 元数据不计入该目标；
- 这是复杂度报警线，不是截断内容的硬上限；不得为了达标删除关键风险或证据；
- 超出软目标时，宿主必须检查是否加入了未触发段落、重复背景或实现细节；
- 去重后仍明显超出，说明任务可能不再轻量，应重新评估并推荐
  `planning_status=draft`，而不是强行压缩或继续冒充小任务。

### 专业 Skill 调用预算

对 `planning_status=not_required`：

- 默认最多调用一个与当前问题直接相关、允许模型调用的专业 Skill；
- 任务已经明确且基础模型足以安全完成时，可以不调用外部 Skill；
- 用户明确指定的 Skill 仍按调用权限和授权规则处理；
- 如果需要同时调用诊断、架构、迁移、TDD 等多个专业能力，重新评估为 Planning，
  不能用多个 Skill 堆叠掩盖任务复杂度；
- `grill-finalizer` 不在小任务中固定调用；只有 Grill 触发时才进入其既有路由与
  bundled fallback。

### Progressive reference loading

宿主只读取当前状态真正需要的 bundled reference：

1. 先读取主 Agent Workflow 和统一 Work Document workflow/template；
2. 只有对应 Profile、外部 Skill、Card、Delivery、Review 或 legacy 条件触发时，才从
   manifest 读取该单个 reference；
3. 不得预加载全部 Profile、全部 lifecycle references、全部第三方 Skill 正文或所有
   辅助工具说明；
4. 当后续证据触发新段落时，再增量读取其唯一 owner。

reference manifest 是发现目录，不是“一次全部读取”的指令。小任务的低 Token 成本
必须同时由短正文、少 Skill 和按需 reference 三条规则保障。

## 阶段与确认门

### Analysis

初始文档先完成五项核心和所有已触发的分析段落。宿主预填已知事实，只询问能改变
Outcome、Evidence、Scope、Risk、Decision 或 Planning requirement 的问题。

Analysis 确认后：

```yaml
analysis_status: confirmed
```

这只确认任务判断，不授权写 Planning、创建 nodes 或实施。

### Planning requirement 决策

Analysis 确认前必须判断：

```yaml
planning_status: not_required | draft
```

只有全部满足时才能推荐 `not_required`：

- Outcome、Evidence、Scope 和 Next Action 已明确；
- 只有一个局部、可直接描述的实施动作；
- 不涉及数据库/迁移、公开 API、权限、安全、隐私、登录、付费或删除；
- 不涉及发布、外发、commit、push 或其他独立授权；
- 不需要产品方向、审美选择或多节点依赖；
- 验证方法明确且失败容易撤销；
- 不存在会改变方案的未知信息。

“代码行数少”不是充分条件。任一条件不满足或无法证明，就进入 Planning。

### Planning

`planning_status=draft` 时，在同一文档 working copy 中追加已触发的 Planning 段落。
只有实际需要的 Recommended Approach、节点、依赖、Skill strategy、验证、授权、回滚
和 Grill 出现。Planning 确认后创建下一不可变 `task-work-vNN`：

```yaml
analysis_status: confirmed
planning_status: confirmed
```

### Execution

无论 `planning_status=not_required` 还是 `confirmed`，都必须等用户另行指示宿主实施
唯一 active、confirmed、hash-verified Work Document。建议统一口令语义为：

```text
实施这个任务文档
```

旧的“实施这个 Plan”仍可用于 legacy Plan 或明确指向 active Work Document 的兼容
解析，但不能在存在多个候选或未验证版本时猜测。

`not_required` 只表示不需要独立 Planning 内容，不表示自动执行。执行型 Skill 也不能
在 Analysis 确认或文档写作阶段提前运行。

## Grill 与小任务成本

Grill 不再是每个文档固定出现的章节：

- 低风险、单一动作、证据明确且 `planning_status=not_required` 的任务，可以省略正式
  Grill 段；宿主仍做一次内部遗漏检查，但不生成空 Grill 文本。
- 进入 Planning、存在方向选择、跨模块、外部契约、迁移、安全、发布、不可逆动作或
  假成功风险时，增加 Grill Review。
- 需要 Grill 时继续优先调用已安装且允许模型调用的 `grill-finalizer`；不可用或失败
  立即 bundled Grill。
- 自动 Reviewer 只提供证据和建议，不拥有产品方向、审美或授权决定。

省略 Grill 必须由 `not_required` 判定证据支持，不能只因为用户希望更快。

## Description managed block

用一个 block 取代 analysis-summary 和 plan-summary 的新写入路径：

```text
<!-- granoflow-task-work-summary:start -->
- 状态: analysis=<status>; planning=<status>; execution=<status>
- 结论: <decision>
- Outcome: <one-line outcome>
- Evidence: <strongest evidence>
- 执行边界: <execution method and user action boundary>
- Work Document: <active attachment id/name or safe path>
- 版本: vNN
- 文档状态: attached | local_reference | attachment_api_unavailable | upload_failed
- 当前节点: 无 | <node>
- 待授权: 无 | <summary>
- 当前阻塞: 无 | <summary>
- 下一步: <state-level action>
<!-- granoflow-task-work-summary:end -->
```

旧 analysis/plan blocks 在 legacy read 时保留，不自动删除。首次写新 Work Document 时，
新 block 成为唯一 active summary；旧 blocks 标记为 legacy/superseded 或停止更新，但
不得改写 marker 外用户内容。重复、嵌套、缺失或反向 marker 必须 fail closed。

## Delivery 与后续生命周期

Task Delivery 继续是独立不可变文档，因为它记录实际结果而非事前判断。模板调整为：

```yaml
source_work_document: <active task_work attachment>
```

并使用：

- Differences From Work Document；
- 实际交付物和证据；
- 残留、人工验收和 handoff；
- Card Checkpoint 与 provenance。

Legacy Delivery 继续读取 `source_analysis` / `source_plan`。新 Delivery 不再双写这些字段。
Deferred Task Review 和 Completion Summary 同步引用 active Work Document，但生命周期
边界和完成 owner 不变。

## 兼容策略

- `task-analysis-template.md`、`task-plan-template.md`、各自 workflow 保留为 legacy
  compatibility reference，正文只说明旧 attachment 的读取规则和新写入 owner；不再
  暴露第二套可用于新任务的完整模板。
- 新增 `task-work-document-template.md` 和 `task-work-document-workflow.md` 作为唯一 owner。
- 历史 attachment 不转换、不覆盖、不删除。
- 旧口令、旧 summary marker 和旧 Delivery 字段仅用于 legacy read/resolve。
- 任何新建或重大修订从 `task_work schema_version: 1` 开始。
- 若宿主只能读取旧 npm package，它继续按旧流程工作；新 package 的 bundled Skill
  明确路由到统一 owner，不谎称旧附件已迁移。

## 受影响文件与结构预算

| 文件                                              | 责任与预算                                                   |
| ------------------------------------------------- | ------------------------------------------------------------ |
| `references/task-work-document-template.md`（新） | 唯一自适应模板，目标不超过 220 行                            |
| `references/task-work-document-workflow.md`（新） | 阶段、版本、触发、确认和兼容 owner，目标不超过 320 行        |
| `references/task-analysis-template.md`            | 收缩为 legacy read/redirect，目标不超过 60 行                |
| `references/task-plan-template.md`                | 收缩为 legacy read/redirect，目标不超过 60 行                |
| `references/task-analysis-execution.md`           | 收缩并路由统一 workflow，避免第二套状态机，目标不超过 100 行 |
| `references/task-plan-workflow.md`                | 收缩为 legacy Plan 与执行口令兼容，目标不超过 100 行         |
| `references/task-analysis-profile-*.md`           | 改为 Work Document 条件化 Profile，不复制模板                |
| `references/external-skill-routing.md`            | Analysis/Plan SSOT 术语改为 Work Document 阶段 SSOT          |
| `references/daily-pending-task-triage.md`         | 批处理改为每任务一个 Work Document，不改宿主循环 owner       |
| `references/task-delivery-template.md`            | 新写入改为 `source_work_document` 和统一 delta               |
| `references/task-delivery-workflow.md`            | 读取 active Work Document；保留 legacy source 兼容           |
| `references/task-completion-summary-template.md`  | Analysis/Plan 链接改为 Work Document，保留 legacy read       |
| `skills/granoflow-agent-workflow/SKILL.md`        | 主路由、catalog、生命周期和成功标准切到统一文档              |
| `README.md`                                       | 公共说明从双文档改为自适应统一文档                           |
| `tests/task-workflow-contracts.test.ts`           | 新模板、状态、最小核心、触发、legacy 和 Delivery 契约        |
| `tests/workflow-resources.test.ts`                | manifest/read 新 owner；现有安全测试不变                     |

不新增 TypeScript runtime 文件。Markdown owner 必须通过引用收敛，不能把完整规则同时
留在旧 Analysis、Plan 和新 Work Document 三处。

## 实施步骤

### 阶段 1：先锁定统一公共契约

1. 以契约测试定义唯一新写入 owner、五项核心、状态枚举和 `planning_status` 判定。
2. 测试 legacy references 不再包含可用于新写入的完整双模板。
3. 测试新增 reference 可由真实 package manifest 发现和读取。
4. 测试小任务软预算、最多一个专业 Skill 和 progressive reference loading 契约。

完成标准：测试先失败，且失败准确指向尚未存在的统一文档契约。

### 阶段 2：建立模板与 workflow owner

1. 新增统一模板和 workflow。
2. 写清条件化段落触发矩阵、版本检查点、summary marker、Grill 和执行授权。
3. 写清最小充分正文、轻量 Skill 调用预算和按需 reference 读取顺序。
4. 将 Analysis/Plan 旧 references 收缩为 legacy compatibility redirects。
5. 更新 learning/software Profile 和 external Skill routing 的术语。

完成标准：新任务只有一个模板入口；小任务只产生最小核心和必要元数据。

### 阶段 3：迁移生命周期消费者

1. Agent Workflow 主入口和批量 triage 改为每任务一个 Work Document。
2. Delivery、Completion Summary、Review/Card provenance 改为统一 source，同时保留
   legacy Analysis/Plan read。
3. README 更新用户可见工作流和执行口令。

完成标准：从捕获后的分析到实施、Delivery、Review 没有任何新写入路径要求双文档。

### 阶段 4：回归与收尾

1. 更新文档契约测试和 package reference smoke。
2. 搜索并分类所有 `Task Analysis` / `Task Plan` 残留：legacy compatibility、历史说明
   或错误的新写入语义。
3. 运行完整质量门禁，修复至绿色。
4. 回写本计划状态、实际差异和验证结果。

完成标准：旧附件可读，新任务只写统一文档，Delivery 保持独立。

## 验收判定

| #   | 验收项                           | 通过证据                                                                 |
| --- | -------------------------------- | ------------------------------------------------------------------------ |
| A1  | 新任务只有一个事前文档模板       | catalog 和 workflow 只指向 Task Work Document                            |
| A2  | 最小核心恰为五项                 | 模板强制 Outcome/Evidence/Scope/Risk/Next Action                         |
| A3  | 其他段落全部条件化               | workflow 有触发矩阵，模板不预生成无关空段                                |
| A4  | 小任务可无 Planning              | `planning_status=not_required` 有严格判定和测试                          |
| A5  | 行数少不能绕过风险               | 数据/API/安全/授权等任一项强制进入 Planning                              |
| A6  | 阶段授权仍独立                   | Analysis confirmation、Planning confirmation、Execution instruction 分离 |
| A7  | 一个 active 文档且附件不可变     | vNN/supersedes/hash readback/active switch 明确                          |
| A8  | 执行进度不覆盖 attachment        | nodes 和 summary 负责 runtime progress                                   |
| A9  | Grill 对小任务可省略但非任意跳过 | 省略条件绑定 `planning_status=not_required`                              |
| A10 | Delivery 继续独立                | 新 Delivery 使用 `source_work_document` 和统一 delta                     |
| A11 | 历史双文档可读                   | legacy redirects 和 Delivery legacy fields 明确                          |
| A12 | 新写入不再生成双文档             | SKILL、triage、README 和测试无双写路径                                   |
| A13 | 外部 Skill 路由继续有效          | Work Document 记录能力阶段和 fallback                                    |
| A14 | MCP 保持控制面                   | 无 App/API/DB/UI/runtime 新逻辑                                          |
| A15 | 新 references 可随包分发         | manifest/read/package smoke 通过                                         |
| A16 | 完整质量门禁通过                 | `npm run check` 退出码为 0                                               |
| A17 | 小任务正文有明确软预算           | `not_required` 目标为 250 中文字符或约 400 tokens，超出后重评而非截断    |
| A18 | 小任务不机械调用多个 Skill       | `not_required` 默认最多一个直接相关专业 Skill，可为零                    |
| A19 | reference 按触发渐进读取         | workflow 禁止预加载全部 Profile、lifecycle reference 和 Skill 正文       |

## 验证计划

实施过程中使用垂直 TDD，最终运行：

```bash
npm run check
```

重点断言：

- 统一模板包含五项核心但不包含所有可选空章节；
- `planning_status=not_required` 的全部禁止条件可从 workflow 读取；
- `not_required` 仍要求独立执行指令；
- Planning required 时，下一版本 supersedes 分析检查点版本；
- active 切换需要 attachment content/hash readback；
- execution progress 不修改不可变 attachment；
- Delivery 新写入只使用 `source_work_document`，legacy read 仍支持旧双 source；
- daily batch 每任务使用一个 Work Document，不把 batch outline 当作任务文档；
- external Skill routing、Profile、Card Checkpoint 和个人用户 Execution Mode 不回退；
- `planning_status=not_required` 明确包含正文软预算、最多一个专业 Skill 和超限升级规则；
- 初始路径只读取统一 workflow/template，其他 reference 必须由具体触发条件增量读取；
- package manifest 能发现并读取两个新 references；
- README 与 bundled Skill 一致。

不修改 UI、数据库或 API，因此不需要浏览器 E2E、migration 或 Local HTTP API 新 endpoint
测试。现有 MCP protocol smoke、package smoke 和全部测试必须保持绿色。

## 失败、回滚与停止条件

### 停止条件

- 统一文档需要新增 App schema、API endpoint 或 MCP runtime 状态机；
- 无法在不覆盖 attachment 的情况下表达同一文档逐步生长；
- `planning_status=not_required` 无法与执行授权明确分离；
- legacy attachment 读取必须依赖批量数据迁移；
- Delivery 无法同时支持新 source 和 legacy source；
- 为减少段落而必须删除 Outcome、Evidence、Scope、Risk 或 Next Action 任一核心。
- 小任务预算只能靠截断关键内容或跳过风险才能满足；
- 宿主无法避免在每个任务中预加载全部 references 或全部专业 Skills。

命中任一条件时停止实施并回到 Analysis，不以保留双写或绕过 readback 作为临时方案。

### 回滚

这是 bundled workflow 文档契约变更，没有数据迁移。若统一流程造成误执行、信息不足
或 legacy 读取失败：

1. 恢复旧 Analysis/Plan templates 和 workflow 为新写入 owner；
2. 恢复 SKILL、triage、Delivery、Completion Summary 和 README 双文档路由；
3. 保留历史 attachment 和已生成 Task Work Document，不删除用户数据；
4. 将新 references 标记为 deprecated read-only，而不是让旧 host 读取失败；
5. 重新运行 `npm run check`。

## 旧治理文档冲突与回写

`docs-temp/analysis/70-granoflow-three-layer-governance-20260715.md` 和既有控制面 73
明确区分 Analysis 与 Plan，并曾使用两个不可变 attachment。新意图不是取消阶段，而是
有意替换其物理双文档设计。实施时应在相关旧文档增加 superseded/addendum 指向本 73，
避免未来执行者把旧双模板恢复为新写入路径；控制面、不可变版本、readback 和授权门
仍继续有效。

## 实施授权语义

用户后续说“实施这个 73”，授权完成本计划全部阶段、文档契约迁移、测试和
`npm run check`。这不授权 commit、push、npm publish、第三方 Skill 安装或其他高风险
外部操作。

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
