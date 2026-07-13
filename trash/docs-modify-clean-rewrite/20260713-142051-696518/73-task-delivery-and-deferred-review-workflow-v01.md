<!-- markdownlint-disable MD013 -->

# 73 执行计划：Task Delivery 与延后 Task Review 公共语义迭代

## 0. 文档角色

- 日期：2026-07-13
- 状态：draft，等待用户评审与 final 确认；本文件本身不授权实施。
- 本地编号说明：`73` 只属于当前项目的本地计划治理；公开 MCP、公开模板、工具描述和用户提示不得要求用户理解任何数字编号。
- 上游输入：
  - 已确认的 Task Analysis 交互式、渐进式与 Profile 设计；
  - 已确认的 Task Plan 附件、节点交付、下游启动需求、手工验收和最新状态回读设计；
  - 本轮关于 Task Delivery、延后 Task Review、效率分析、Review Card 和项目上下文晋升的讨论；
  - 当前 `granoflow-agent-workflow`、`granoflow-task-copilot`、`granoflow-task-runner`、`granoflow-review-card-draft` 和 Project Context YAML 实现。
- 本文角色：
  - 面向本地实施者的跨仓工程计划；
  - 冻结公开语义、模板 contract、完成与回顾边界、兼容迁移和验收方式；
  - 不把本地 `70/71/72/73/74/76` 术语发布给 MCP 用户。
- 完成定义：
  - Task Analysis、Task Plan、Task Delivery、Task Review 四阶段模板齐备；
  - 完成任务默认不再自动生成深度回顾或卡片；
  - Delivery 在完成前作为版本化任务附件写入并回读；
  - Review 可在任务结束后由用户单独发起，并完成时间、返工、卡片和项目上下文处理；
  - 公开内容不再暴露本地数字文档类型；
  - MCP 与共享 skills、测试和公开文档全部一致。

## 1. 适用性裁剪说明

- 本次实施类型：公开 MCP workflow、共享 skill、模板、TypeScript 工具描述与测试、文档治理。
- 本次适用章节：公开命名、模板体系、workflow 状态机、兼容行为、卡片委托、Project Context 晋升、测试与回滚。
- 本次明确不适用：
  - 数据库 migration、表、字段、索引、触发器和 schemaVersion；
  - Flutter UI、页面、组件、文案和交互；
  - 新增 Local HTTP API endpoint；
  - 自动创建新的项目、里程碑或 Review Card；
  - 发布 npm、MCP Registry 或其他目录；
  - 修改本地 `70-74` writer family 的编号规则。
- 裁剪原则：
  - 普适能力使用一个基础模板；
  - learning 与 software development 使用薄 Profile；
  - 不复制三套完整模板；
  - Review Card 继续由唯一 card authoring owner 处理；
  - Project Context 继续复用现有 canonical YAML 和里程碑上下文字段。

## 2. 上游结论与本次目标

### 2.1 已确认的问题

1. 当前公开 workflow 仍把“结束任务、写 taskReview、制作 Review Card”绑定在一起，不适合用户先完成、以后集中验收和回顾的工作方式。
2. 当前已有 Task Analysis 和 Task Plan 基础模板及 learning/software-development Profile，但缺少正式 Task Delivery 与 Task Review 模板。
3. 当前 Plan 模板仍公开出现 `project_73`、`project_76` 等本地编号概念。
4. 当前任务描述缺少统一、幂等的最终收尾区块。
5. 当前回顾指导能写一般性 taskReview，但没有统一定义讨论时间、AI 自动执行时间、等待时间、返工时间、证据可信度和避免重做的分析方法。
6. 当前 Project Context 已具备 `project_snapshot.yaml`、`project_rules.yaml`、活跃里程碑 description 和归档 completionSummary，但尚未形成从单任务回顾中“筛选并晋升”长期信息的统一 entry contract。

### 2.2 本次必须落地的结果

- 公开任务生命周期统一为：
  - Task Analysis；
  - Task Plan；
  - Task Delivery；
  - Task Review。
- Task Delivery 回答“最终实际交付了什么，与 Analysis/Plan 有何差异”。
- Task Review 回答“过程是否高效、哪里返工、浪费多少、以后如何避免，以及哪些知识值得保存”。
- Task 完成与 Task Review 默认解耦。
- 第一版不增加 `reviewedAt` 或 review status 字段；结构化回顾通过 `<!-- granoflow-task-review:v1 -->` marker 识别，已有非空无 marker 内容视为用户/历史内容，不得静默覆盖。
- 用户显式要求“完成并回顾”时允许同一会话连续执行两阶段，但 workflow 仍必须先完成 Delivery，再进入独立 Review gate。
- Review Card 搜索、过滤、预览、确认、写入和 readback 全部委托 `granoflow-review-card-draft`。
- 项目长期上下文只晋升经过验证且可复用的信息，不把每个任务流水账追加进 YAML。

### 2.3 成功判定标准

- 四阶段均有语义清晰、可独立消费的模板。
- general 直接使用基础模板；learning 与 software development 是可组合的薄 Profile，同一任务可以同时加载两者。
- `granoflow_task_finish` 的默认指导不再要求自动 taskReview 或 Review Card。
- 旧调用者显式传入 `taskReview` / `reviewCardDrafts` 时保持兼容，但被标记为 explicit inline review compatibility，不再由默认 workflow 自动推断。
- Delivery 附件具有版本、状态、上游 Analysis/Plan 引用、差异、证据、手工验收和残余项。
- Review 具有互斥时间分类、返工子集、可信度、证据、改进建议、卡片结果和上下文晋升结果。
- 公开 bundled skill、README、安装演示和工具描述中不再把本地数字编号作为用户需理解的文档类型。

### 2.4 不可违背的不变量

- App/Local HTTP API 继续拥有任务、附件、卡片和 Project Context 的业务写入规则；MCP 保持薄封装。
- Delivery 和 Review 均以 Granoflow 最新状态为 SSOT，写入前读取，写入后 readback。
- 每次 material write 前重新读取任务、节点和目标资源；支持时传入 `expectedUpdatedAt`，冲突时基于最新状态重算差异，不得覆盖其他设备的更新。
- Delivery 不评价效率、情绪或动机；Review 不伪造交付事实。
- `rework_time` 是 discussion/AI execution 的子集，不得再次计入总时长。
- 无证据的时间必须标记 `estimated` 或 `unknown`，不得制造精确值。
- Delivery、Review、Review Card 与 Project Context 只保存必要的派生区间和简短证据摘要，不复制原始对话、tool logs 或秘密材料。
- Analysis 只代表任务开始前的分析，不是项目当前实际情况；与后续确认文档冲突时，以更晚且更接近实际交付/当前状态的文档为准，并记录差异。
- Plan 只代表任务执行前的意图，不是实际完成结果；与 Delivery 冲突时，以 Delivery 记录的实际交付为准。
- Delivery 只证明该任务在 `delivered_at` 时点的交付，不保证后续任务没有修改；判断当前状态时优先读取最新项目/里程碑上下文并核对实际代码与运行态。
- Project/Milestone 文档是 living context，可能更新不及时；与实际代码、运行态或外部可验证状态冲突时必须显式报告，并提出更新文档或修正实现的建议。
- “当前事实”和“目标规范”必须分开：实际代码/运行态证明当前事实，Project Rules/Specification/Decision Record 证明应遵守的规则；两者冲突时不得静默覆盖任一方。
- 用户手工验收节点只能由用户或可验证的外部回读完成。
- Review Card 写入必须经过 similarity、AI filtering、preview、明确批准、apply 和 `practiceReady` readback。
- 公开名称使用语义名；本地编号最多作为非公开适配来源，不进入公开 enum、标题或用户指令。

### 2.5 执行授权

- 当前：`no`。
- 用户当前只授权写本计划；在用户确认 final 并明确要求实施前，不修改代码、skills 或公开文档。

## 3. 范围与边界

### In Scope

- 新增 Task Delivery 基础模板、learning Profile、software-development Profile。
- 新增 Task Review 基础模板、learning Profile、software-development Profile。
- 新增任务描述 closeout 模板。
- 新增 Project Context promotion entry YAML 模板。
- 新增 Task Delivery workflow 和独立 Task Review workflow。
- 修改 Task Plan 模板，删除公开 `project_73` / `project_76` 类型。
- 修改完成任务 workflow，使默认路径为 Delivery → acceptance/completion，而非 completion → automatic review/cards。
- 修改 `granoflow_task_finish` 描述、guidance 和测试，保留显式 inline compatibility。
- 同步 bundled workflow、共享 copilot、共享 runner、README、安装演示、目录文案和测试。
- 增加静态契约检查，防止本地数字编号重新泄漏到公开模板。

### Out of Scope

- 修改任务数据库 schema 或新增 `reviewedAt` / `reviewStatus`。
- 新增 App Review Queue UI。
- 新增 Task Delivery 或 Task Review 专用 Local HTTP API。
- 新增重复的 Review Card skill。
- 自动判断用户情绪、人格、动机或主观效率分数。
- 自动把每个任务回顾写入 Project Context YAML。
- 自动发布新版本。
- 改名或删除本地 `70-analysis-writer`、`73-plan-writer` 等本地治理 skill。

### 非目标但需避免退化

- 快速插入任务仍不生成任何文档。
- Analysis 仍需用户确认 final 后才能规划。
- Plan 仍需版本化附件、节点交付和下游启动 contract。
- 节点全部完成后父任务自动完成的 App 业务逻辑不得改写到 MCP。
- 已发布调用者显式使用 `granoflow_task_finish` review 参数的兼容性不得静默破坏。
- 已归档里程碑仍不得通过普通 MCP workflow 修改 description。

## 4. 前置条件与冻结项

### 4.1 前置条件

- 进入实施前重新核对当前分支与工作区，避免覆盖用户未提交改动。
- 核对 running App capabilities 至少包含：
  - task read/update；
  - Markdown attachment add/list/delete；
  - task node list/update；
  - review-card similarity and controlled authoring；
  - project-context-attachment ensure/read/write/reconcile；
  - project/milestone context stewardship。
- 用测试或本地 API fixture 确认 completed task 可以更新 `taskReview` 和 description。
- 若上述已有能力缺失，停止“无 App 改动”路线，回到计划修订；不得在 MCP 中模拟业务写入。

### 4.2 公开命名冻结清单

| 概念     | 公开名称                      | 文件名                          | 禁止公开名称                             |
| -------- | ----------------------------- | ------------------------------- | ---------------------------------------- |
| 任务分析 | Task Analysis                 | `task-analysis-template.md`     | 70 Analysis                              |
| 任务计划 | Task Plan                     | `task-plan-template.md`         | 73 Plan、76 Plan、project_73、project_76 |
| 任务交付 | Task Delivery                 | `task-delivery-template.md`     | 75 Delivery                              |
| 任务回顾 | Task Review                   | `task-review-template.md`       | 74 Review                                |
| 当前事实 | Current Snapshot              | canonical project snapshot YAML | 71 Snapshot（公开要求）                  |
| 长期规则 | Project Rules / Specification | canonical project rules YAML    | 72 Spec（公开要求）                      |
| 决策记录 | Decision Record               | decision entry                  | 74 Decision（公开要求）                  |

- 本地编号文档可作为 source evidence，但公开 workflow 只识别其语义能力是否满足 contract。
- 不新增 `source_convention: project_73` 一类公开 schema；需要追溯时使用普通 `source_document`、attachment id/name 或 URI。

### 4.3 状态冻结

- Delivery 状态：
  - `draft`；
  - `delivered`；
  - `delivered_with_residuals`；
  - `awaiting_manual_acceptance`；
  - `superseded`。
- Review 状态：
  - 未回顾：completed task 且 `taskReview` 为空；
  - 已结构化回顾：completed task 且 `taskReview` 包含 `<!-- granoflow-task-review:v1 -->` marker；
  - 已有未标记内容：`taskReview` 非空但没有 marker，视为用户或旧 workflow 内容；Review 必须先展示 merge/replace proposal 并取得确认，不得静默覆盖；
  - 第一版不创建独立数据库状态。
- inline review：只有用户明确要求“完成并回顾”或同义表达时启用；仍按 Delivery、Completion、Review 三个 gate 顺序执行。

### 4.4 文档作用域、时效与冲突优先级

所有 Task Analysis、Task Plan、Task Delivery、Task Review 和 Project/Milestone Context 模板都必须在标题和 metadata 后的开头位置显示作用域声明。声明不能只存在于 skill 隐藏规则中。

#### 判断当前实际情况

默认证据顺序：

1. 当前实际代码、可重复测试、运行态和外部可验证状态；
2. 已检查 freshness 的 Project/Milestone living context；
3. 最新未被 supersede 的 Task Delivery；
4. Task Plan；
5. Task Analysis。

后写文档并不天然正确。若后写文档缺少 evidence、已 stale 或与实际状态冲突，执行者必须报告冲突，不能只按时间覆盖。

#### 判断应遵守的规则

- 已确认且仍 active 的 Project Rules、Specification 和 Decision Record 是规范性依据。
- 实际代码与规范不一致时，代码只证明“现在实际如此”，不自动证明规范已经失效。
- 冲突报告必须判断推荐动作是：
  - 修正代码以恢复规范；
  - 更新已过时的项目/里程碑文档；
  - 先请求用户确认边界或决策变化。
- 每次 substantial project write 收尾必须做 context upkeep decision，确保 living context 尽可能保持最新。

#### 固定声明文字

- Task Analysis：
  - `Scope notice: This document is pre-task analysis for this task only, not a statement of the project's current actual state. If it conflicts with later confirmed documents, use the later evidence-backed document and record the difference.`
- Task Plan：
  - `Scope notice: This document is the pre-execution plan for this task, not a record of actual completion. If it conflicts with Task Delivery, Task Delivery governs what was actually delivered.`
- Task Delivery：
  - `Scope notice: This document records this task's delivery as of delivered_at. Later tasks may change the result. For current state, use the freshest Project/Milestone Context and verify it against actual code and runtime evidence.`
- Task Review：
  - `Scope notice: This document is a retrospective of this task's process, not the source of truth for current project state. Use Task Delivery for this task's result and current Project/Milestone Context plus verified implementation for current state.`
- Project/Milestone Context：
  - `Freshness notice: This is living context and may lag behind actual implementation. If it conflicts with code, runtime, or externally verified state, report the conflict explicitly and propose the required document or implementation update.`

公开模板可提供与用户语言一致的显示文本，但语义和优先级不得变化。

## 5. 自动化执行策略

- 优先使用：
  - `rg` / `rg --files` 盘点公开数字术语和 workflow 引用；
  - repository-local `npm run check` 验证 MCP；
  - 现有 MCP/App fixture 测试验证工具请求与兼容行为；
  - 现有 skill validation/format 入口；若仓库没有统一入口，使用 `git diff --check`、定向结构检查和相关测试，不发明新全局命令。
- 不新增临时 runtime 脚本；模板和 contract 检查优先进入现有 Vitest 或 repo validation。
- AI 负责：模板生成、引用同步、contract 测试、公开文案修订和只读 capability 审计。
- 用户负责：计划 final 确认、实施授权、Review Card preview 后的具体 operation approval，以及主观回顾信息确认。

## 6. 影响面与改动清单

### 6.1 Granoflow MCP Server

#### MCP 预计新增

- `skills/granoflow-agent-workflow/references/task-delivery-template.md`
- `skills/granoflow-agent-workflow/references/task-delivery-profile-learning.md`
- `skills/granoflow-agent-workflow/references/task-delivery-profile-software-development.md`
- `skills/granoflow-agent-workflow/references/task-delivery-workflow.md`
- `skills/granoflow-agent-workflow/references/task-review-template.md`
- `skills/granoflow-agent-workflow/references/task-review-profile-learning.md`
- `skills/granoflow-agent-workflow/references/task-review-profile-software-development.md`
- `skills/granoflow-agent-workflow/references/task-review-workflow.md`
- `skills/granoflow-agent-workflow/references/task-description-closeout-template.md`
- `skills/granoflow-agent-workflow/references/project-context-promotion-entry.yaml`

#### MCP 预计修改

- `skills/granoflow-agent-workflow/SKILL.md`
- `skills/granoflow-agent-workflow/references/task-plan-template.md`
- `skills/granoflow-agent-workflow/references/task-plan-workflow.md`
- `skills/granoflow-agent-workflow/references/review-drafting.md`
- `skills/granoflow-agent-workflow/references/review-card-authoring.md`
- `skills/granoflow-agent-workflow/references/project-context-attachments.md`
- `skills/granoflow-agent-workflow/references/daily-pending-task-triage.md`
- `src/tools.ts`
- `tests/tools.test.ts`
- `README.md`
- `docs/user-install-demo.md`
- `docs/directory-listings.md`
- 仅在当前文案确实声明旧完成语义时修改 `docs/release-checklist.md`。

#### 明确不新增

- 新的 Task Delivery/Review MCP primitive tool；第一版由 workflow 编排现有安全工具。
- 第二套 Review Card authoring 实现。
- MCP 侧本地数据库、时间追踪器或会话日志数据库。

### 6.2 Shared Skills

#### Shared 预计修改

- `/Users/will/code/skills/granoflow-task-copilot/SKILL.md`
- `/Users/will/code/skills/granoflow-task-copilot/references/intent-routing.md`
- `/Users/will/code/skills/granoflow-task-copilot/references/finish-task-workflow.md`
- `/Users/will/code/skills/granoflow-task-copilot/references/review-writing.md`
- `/Users/will/code/skills/granoflow-task-copilot/references/card-memory-rules.md`
- `/Users/will/code/skills/granoflow-task-copilot/references/safety-and-fallbacks.md`
- `/Users/will/code/skills/granoflow-task-runner/SKILL.md`
- `/Users/will/code/skills/granoflow-task-runner/references/workflow.md`
- `/Users/will/code/skills/granoflow-task-runner/references/task-plan-workflow.md`

#### Shared 预计新增

- 与 bundled workflow 同语义的 Delivery/Review workflow、模板或委托指针；优先复用 canonical bundled references，避免复制后漂移。

#### 明确不修改

- `/Users/will/code/skills/70-analysis-writer`
- `/Users/will/code/skills/71-snapshot-writer`
- `/Users/will/code/skills/72-spec-writer`
- `/Users/will/code/skills/73-plan-writer`
- `/Users/will/code/skills/74-decision-log-writer`
- `/Users/will/code/skills/project-doc-system`

这些仍是本地项目治理能力，不进入公开 MCP 用户词汇。

### 6.3 Granoflow App / Local HTTP API

- 预计代码改动：无。
- 需只读核对：
  - completed task details update 是否允许 description/taskReview；
  - attachment 写入和 readback 是否支持 Delivery；
  - Project Context YAML 和 milestone context 工具是否满足晋升 contract；
  - Review Card authoring 是否保持 controlled preview/apply。
- 若核对失败：修订本计划，单独定义 App-owned API 扩展；不得把缺口塞进 MCP workaround。

### 6.4 数据库表结构判断

- 结论：无变化。
- 判断依据：
  - Task 已有 `description`、`taskReview`、`startedAt`、`endedAt`；
  - 未回顾、结构化已回顾和已有未标记内容可由 taskReview 空值/marker 规则区分；
  - Delivery 使用既有 Markdown attachment；
  - Project Context 使用既有 canonical YAML attachment；
  - milestone 使用既有 description/completionSummary；
  - Review Card 使用既有 note/card/link 结构。
- 不涉及：表、字段、索引、触发器、migration、schemaVersion、RLS、回填和旧数据迁移。
- 用户确认要求：无需额外 schema 图确认；本计划明确冻结“第一版不新增 review 状态字段”。

### 6.5 UI 判断

- 结论：无变化。
- 判断依据：
  - 所有新增行为位于 MCP workflow、Markdown attachment、taskReview 文本和 existing Project Context 写入；
  - 不新增 Review Queue 页面、Delivery 页面或卡片 UI；
  - 用户仍通过现有任务详情、附件、节点、回顾字段和卡片练习界面查看结果。
- 不涉及：布局、组件、位置、显隐、空态、错误态和 App 用户可见文案。
- 用户确认要求：无需 UI 草图确认。

### 6.6 对外契约

- `granoflow_task_finish`：
  - 默认语义改为在 Delivery 和完成 gate 满足后结束任务；
  - 不再指导 Agent 自动产生深度 taskReview 或 Review Cards；
  - 本次迭代不删除或改型旧 `taskReview` / `reviewCardDrafts` 参数，只在用户显式要求 inline review 时使用；
  - patch 版本不得移除这些参数；未来移除必须按 breaking change 处理，并先完成调用方审计、迁移说明和兼容期；
  - dry-run guidance 必须说明 deferred review 是默认路径。
- `granoflow_agent_workflow_skill`：
  - 能路由 analyze、plan、deliver、finish、review、card 和 context promotion；
  - 对外只使用语义名称。
- 不增加新 endpoint，不改变既有 wire field 的类型。

### 6.7 文件与方法预算

- 新增 Markdown template/profile：每个文件单一职责，目标有效行数 `< 160`；Profile 目标 `< 80`。
- 新增 workflow reference：每个文件目标有效行数 `< 220`；若超过，按 Delivery/Review/Promotion 的真实职责拆分。
- `SKILL.md`：只增加路由和 references，不复制模板全文。
- `src/tools.ts`：只修改现有工具描述、schema description 和 guidance；不新增大型 helper，新增逻辑目标单方法 `< 50` 行。
- `tests/tools.test.ts`：按 contract 场景增加小型测试；若现有 describe 过大，按公开完成语义与模板资源发现的真实边界拆测试文件。
- 禁止：机械按行数拆分、创建 helper/misc 垃圾桶、复制 bundled/shared 两套完整规则、为了通过门禁而隐藏逻辑。

## 7. 模板 Contract

### 7.1 Task Analysis

- 继续使用现有基础模板和两个 Profile。
- 修订点仅限消除公开本地编号引用；不改变已确认的交互、Grill 和 final gate。
- 在标题与 metadata 后固定加入 Task Analysis scope notice，明确它是任务开始前的分析，不是 Project Snapshot。
- 与 Plan/Delivery/Current Context 冲突时必须保留 delta，不得把旧分析重新写成“从一开始就知道”。

### 7.2 Task Plan

- 基础模板始终完整，使用可组合的 `profiles`：
  - `[]`：general/base-only；
  - `[learning]`；
  - `[software_development]`；
  - `[learning, software_development]`：学习型开发、教学代码或以能力变化和软件交付为双重目标的任务。
- Analysis、Plan、Delivery 和 Review 使用相同的 Profile 组合语义；Profile 只能追加领域要求，不能削弱基础 contract。
- 删除 `project_73`、`project_76`。
- 本地计划文档只通过 `source_analysis`、`source_document`、attachment id/name 或普通引用接入，不创造公开编号枚举。
- Plan 的最终执行节点必须包含 Task Delivery 生成、上传和 readback；手工验收可保持 pending，但不能阻塞其他安全节点。
- 在标题与 metadata 后固定加入 Task Plan scope notice，明确计划不是实际交付；实际结果以 Delivery 为准。

### 7.3 Task Delivery 基础模板

固定字段：

```yaml
document_type: task_delivery
schema_version: 1
task_id: <id>
profiles: [] | [learning] | [software_development] | [learning, software_development]
delivery_version: <positive integer>
delivery_status: draft | delivered | delivered_with_residuals | awaiting_manual_acceptance | superseded
source_analysis: <attachment reference>
source_plan: <attachment reference>
supersedes: null | <prior delivery attachment>
delivered_at: <timestamp>
based_on_task_updated_at: <timestamp>
content_sha256: <sha256>
acceptance_status_as_of: accepted | partially_accepted | awaiting_manual_acceptance | not_required
```

固定章节：

1. Final Outcome；
2. Deliverables；
3. Differences From Analysis；
4. Differences From Plan；
5. Actual Change Surface；
6. Verification Evidence；
7. Manual Acceptance；
8. Residuals And Deferred Work；
9. Handoff And Usage；
10. Traceability。

规则：

- 在标题与 metadata 后固定加入 Task Delivery scope notice。
- Delivery 只写实际事实，不复制 Plan 未来时态。
- 每个 Deliverable 必须有位置/标识、状态、证据和使用方式。
- Analysis/Plan 差异必须区分 assumption invalidation、scope change、execution deviation 和 evidence change。
- `awaiting_manual_acceptance` 是有效交付状态，不代表手工验收已完成。
- 附件名固定为 `task-delivery-vNN.md`；版本号单调递增，不能复用已有版本表达不同内容。
- 上传前按 task id、delivery version 和 `content_sha256` 查重；相同版本和内容重试不得产生重复附件。
- `acceptance_status_as_of` 只描述 `delivered_at` 时点。交付后仅手工验收状态变化时，更新节点和 closeout，不生成新 Delivery。
- 实际交付事实发生材料变化时生成新版本并 `supersedes`；单纯状态回读且事实不变不重写附件。
- 已进入 Plan 或 Execution 的完成任务必须有 Delivery；仅 capture 后取消、放弃或从未进入执行的任务不强制补写 Delivery。

### 7.4 Learning Delivery Profile

追加：baseline、changed capability、independent evidence、corrected mistakes、remaining gaps、delayed review trigger。

通过条件：交付证明学习者能力变化；阅读、观看和记笔记只能作为 supporting evidence。

### 7.5 Software Development Delivery Profile

追加：actual behavior、code/API/schema/UI delta、compatibility/migration、static gates、tests/build/runtime surface、release state、rollback entry、file/method budget delta。

通过条件：真实用户表面或运行态证据满足 Analysis Final；零退出码不能替代高层结果。

### 7.6 Task Review 基础模板

在标题与 metadata 后固定加入 Task Review scope notice。

正文首行固定包含：

```html
<!-- granoflow-task-review:v1 -->
```

该 marker 是结构化 Review 的识别依据，不是可选装饰。对非空且无 marker 的既有 `taskReview`，必须先生成保留原文的 merge proposal 或明确的 replace proposal，并取得用户确认。

固定章节：

1. Outcome Assessment；
2. Time Analysis；
3. Time Evidence And Confidence；
4. Rework And Waste；
5. What Worked；
6. Efficiency Problems；
7. Next-Time Adjustments；
8. Knowledge And Experience；
9. Review Card Results；
10. Project/Milestone Context Promotion；
11. Residual Risks And Follow-ups。

时间字段：

```yaml
elapsed_time:
discussion_time:
ai_execution_time:
waiting_time:
manual_acceptance_time:
rework_time:
```

每项必须具有：

```yaml
value: <duration | unknown>
confidence: exact | estimated | unknown
evidence: []
```

整体还必须记录：

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
  closeout: completed | deferred | confirmation_required | failed | unchanged
```

时间规则：

- discussion、AI execution、waiting、manual acceptance 在同一时间轴上不得重叠计入；
- rework 是对 discussion 或 AI execution 片段的标签和子集；
- elapsed wall-clock 与 active-work 不得混为一谈；
- 仅依赖 startedAt/endedAt 时只能得到 elapsed_time；
- `exact` 只允许来自实际 telemetry/session events；transcript 推算只能是 `estimated`，并记录方法与覆盖率；
- transcript 估算默认不跨越超过 5 分钟的无活动间隔；剩余时间归为 unclassified/unknown，不自动算 waiting；
- 并行 tool intervals 先合并为 wall-clock union；分类重叠时按更具体、更强的证据切成互斥区间；用户对区间的明确修正优先；
- Agent transcript、tool calls、focus sessions、commits、tests 和用户反馈可以提高可信度，但只保存必要的派生区间和简短摘要；
- 证据不足保留 unknown，不强行凑总数。

效率建议必须可执行，每项至少包含：

```yaml
trigger: <when the problem recurs>
action: <specific change>
owner: user | ai | project | shared_workflow
expected_benefit: <time, quality, or risk improvement>
validation: <how the next task proves improvement>
```

隐私与最小化规则：

- 不把原始聊天记录、完整 tool logs、屏幕内容或无关个人信息写入 Delivery、Review、Review Card 或 Project Context。
- API token、OTP、恢复码、auth URL、环境秘密和其他凭据不得进入任何上述产物。
- 未获授权读取的历史一律记为 evidence gap，不依据猜测补全。

Review 是可恢复的多步写入，按以下顺序执行：

1. draft/preview，并取得 Review 内容确认；
2. 写入 `taskReview` 并 readback；
3. Review Card preview/approval/apply/readback；
4. Project Context promotion；
5. Milestone Context promotion；
6. closeout 更新与最终 readback。

每次运行使用稳定 operation id，并把逐步状态持久化在结构化 `taskReview` 中；每个 material step 后更新并 readback。重试从最新 Granoflow 状态恢复，已完成步骤不得重复创建卡片、附件或 YAML entry。Review 正文确认并写入成功即可视为 Review 内容完成；卡片或 context 因授权延后时，在 closeout/residuals 中显式列出，不把整个任务重新标为未完成。

### 7.7 Learning Review Profile

追加：input/practice/feedback/correction 时间结构、主动回忆、重复错误、答案泄漏、练习难度、复习安排、知识卡和错误模式卡候选。

### 7.8 Software Development Review Profile

追加：requirements/diagnosis/implementation/verification 分布、错误责任层、失败方案、返工根因、静态门禁前移、真实表面验证、架构/流程经验和项目规则候选。

### 7.9 Task Description Closeout

使用幂等标记：

```html
<!-- granoflow-closeout:start -->
## Final Closeout - Final outcome: - Delivery status: - Task Analysis: - Task Plan: - Task Delivery:
- Manual acceptance: - Review status: pending | completed - Residuals: - Next entry point:
<!-- granoflow-closeout:end -->
```

- 写入时替换旧 closeout block，不连续追加。
- 不复制 Delivery 或 Review 全文。
- Task 完成时默认 `Review status: pending`。
- 带 marker 的 Review 正文写回成功后更新为 `completed` 并 readback；cards/context 的 deferred 或 confirmation_required 状态另列在 Residuals，不伪装成已完成。

### 7.10 Project Context Promotion Entry

统一字段：

```yaml
- id: <stable-id>
  kind: snapshot | rule | decision | lesson | anti_pattern
  scope: project | milestone
  milestone_id: null | <id>
  summary: <short factual summary>
  rationale: <why it matters later>
  future_trigger: <when a future agent should recall it>
  recommended_action: <what to do>
  evidence:
    task_ids: []
    delivery_attachments: []
    review_cards: []
  first_observed_at: <timestamp>
  last_verified_at: <timestamp>
  status: active | superseded | retired
  supersedes: null | <stable-id>
```

晋升规则：

- factual current state → `project_snapshot.yaml`；
- durable rule/boundary/preference → `project_rules.yaml`；
- durable decision → project rules 中的 decision entry；
- active-stage context → active milestone description；
- archived-stage final summary → milestone completionSummary；
- active recall knowledge → Review Card；
- one-off activity log → only taskReview。

禁止每任务机械追加；必须先查重、合并、更新或判定不晋升。

- stable id 和来源 task id 共同作为幂等键；重试不得创建语义相同的第二条 entry。
- 写入前重新读取 canonical YAML，并基于最新内容生成 patch；若 `expectedUpdatedAt` 冲突，重新计算，不覆盖其他设备的变更。

### 7.11 Project/Milestone Context Freshness Header

Project Context 只有两个 canonical YAML：`project_snapshot.yaml` 与 `project_rules.yaml`。它们必须暴露：

```yaml
freshness_status: current | stale | partial | source_gap | reconcile_failed
last_verified_at: <timestamp | null>
source_watermarks:
  latest_task_updated_at: <timestamp | null>
  latest_delivery_at: <timestamp | null>
  implementation_revision: <commit/version | null>
```

- 不发明 Milestone YAML。`scope: milestone` 的 promotion entry 仍写入相应 Project canonical YAML，并带 `milestone_id`。
- active milestone 的上下文写入 `description` 中的有界、幂等 managed block；archived milestone 只更新 `completionSummary`，遵守现有确认与只读边界。
- Milestone freshness 通过 steward metadata 或 description/completionSummary 的有界 managed block表达，不强制套用 Project YAML header。
- Project YAML 和 Milestone managed context 开头固定加入对应 freshness notice。
- freshness 非 `current` 时不得作为完整当前事实直接消费。
- 与实际代码或运行态冲突时返回 conflict report，至少包含：
  - conflicting statement；
  - document evidence；
  - implementation/runtime evidence；
  - recommended action；
  - update target；
  - whether confirmation is required。
- factual low-risk staleness 可以通过现有 reconcile/update gate 修正文档。
- rules、public wording、positioning 或 decision 冲突必须先 proposal/confirmation；不得因为代码已偏离就自动改写规范。

### 7.12 跨设备并发与幂等

- 桌面长连接通知只能作为“状态可能变化”的信号，不能替代写前 read。
- 每次 attachment、taskReview、description、node、card、Project Context 或 Milestone Context 的 material write 前，重新读取任务、节点和目标资源。
- API 支持时必须传入 `expectedUpdatedAt` 或等价 revision。收到 `409`/revision conflict 后读取最新状态，仅重算受影响的 diff，并重新经过必要确认；禁止 last-write-wins 覆盖。
- Delivery 以 task id + delivery version + content hash 去重；Review 及 promotion 以稳定 operation id/entry id 去重；closeout 与 milestone block 使用 marker 替换。
- readback 必须验证写入后的语义结果，而不只检查 HTTP success；发现用户在其他设备已完成、验收或修改节点时，以最新状态调整剩余步骤。

## 8. 分阶段实施步骤

### 阶段 1：Capability 与公开词汇基线

- 目标：确认无 App 扩展即可实施，并冻结需清理的数字术语。
- 动作：
  1. 检查 completed task 的 description/taskReview update contract。
  2. 检查附件、节点、Review Card、Project Context 和 milestone context capabilities。
  3. 用 `rg` 生成 bundled/public/shared workflow 中本地数字术语清单。
  4. 将数字术语分为 public leak、local-only legitimate reference、历史 trash/docs-temp 三类。
- 产物：capability evidence、术语迁移清单。
- 完成判定：无 MCP 侧业务逻辑 workaround；公开迁移范围明确。
- 失败回退点：任一必要 App capability 缺失时暂停并修订计划。

### 阶段 2：建立 Delivery/Review 模板族

- 目标：补齐任务生命周期后半段。
- 动作：
  1. 新增 Delivery base + learning/software profiles。
  2. 新增 Review base + learning/software profiles。
  3. 新增 closeout 和 Project Context promotion entry 模板。
  4. 修改 Task Plan template，删除公开本地编号类型并增加 Delivery 节点要求。
  5. 在 Analysis、Plan、Delivery、Review 和 Project/Milestone Context 开头加入固定 scope/freshness notice。
  6. 验证模板章节、枚举、优先级、Profile 组合和互相引用。
- 产物：10 个新增 references 和修订后的 Plan 模板。
- 完成判定：general 使用 base 即完整；Profile 可组合且只追加领域差异。

### 阶段 3：重写完成、交付和回顾 workflow

- 目标：默认完成与回顾解耦。
- 动作：
  1. 新增 Task Delivery workflow：读取最新状态、对比 Analysis/Plan、生成版本化附件、上传、list/readback、更新 closeout。
  2. 修改 Finish workflow：Delivery 和节点 gate 满足后完成，默认不写深度 taskReview/cards。
  3. 新增 Task Review workflow：只在用户主动发起时运行；读取最新 Task/Delivery/Plan/evidence，按保守时间归因算法分析时间和返工，出草稿并请求确认。
  4. Review 确认后按可恢复状态顺序写 taskReview、调用 card owner、处理 Project/Milestone promotion、更新 closeout并逐步 readback。
  5. 定义 explicit inline review 路径，但不与默认 deferred review 混淆。
  6. 更新 daily/weekly review routing，使 completed + empty taskReview 可作为候选，不自动开始或写回。
  7. 增加文档冲突处理：区分 actual-state conflict 与 normative-rule conflict，显式报告并提出代码或文档修正建议。
  8. 对所有写入增加写前 read、revision conflict 重算和 stable operation id 幂等恢复。
  9. 对 evidence 做最小化与秘密扫描，不把 transcript/tool logs 原文带入持久化产物。
- 产物：Delivery/Review workflow、修订后的 finish/review/context references。
- 完成判定：每条路径的写入、确认和停止条件明确且不互相吞并。

### 阶段 4：MCP 工具契约与兼容迁移

- 目标：让公开工具说明与新 workflow 一致，同时避免破坏旧调用者。
- 动作：
  1. 修改 `granoflow_task_finish` 描述和 dry-run guidance。
  2. 保留 optional review 参数，但标注只有 explicit inline review 使用。
  3. 修改 agent workflow skill tool description，增加 deliver/review 路由。
  4. 不新增重复 primitive；用现有 attachment/task/card/context tools 编排。
  5. 增加测试验证默认 finish payload 不自动生成 review/cards，显式旧参数仍正确转发。
  6. 在兼容说明中冻结生命周期：patch 不移除；未来移除需要 breaking version、caller audit、迁移说明和兼容期。
- 产物：TypeScript contract 与 Vitest。
- 完成判定：默认路径变化可验证，兼容路径仍可验证。

### 阶段 5：同步共享 skills 与公开文档

- 目标：bundled、shared 与用户文档无冲突。
- 动作：
  1. 更新 copilot/runner 的 intent routing、finish、review、card 和 safety references。
  2. 将 runner 的“执行后立即 taskReview”改为“Delivery 后完成，Review 默认另行发起”。
  3. 更新 README、安装演示、目录文案和 release checklist 的旧完成叙述。
  4. 保留本地 project-doc-system 数字编号，不把它复制进公开 package。
- 产物：一致的 public/shared docs。
- 完成判定：同一用户请求在 bundled 和 shared 路由得到同样阶段判断。

### 阶段 6：验证、真实流程 smoke 与收尾

- 目标：证明模板、兼容行为和真实写回链路成立。
- 动作：
  1. 运行 MCP `npm run check`。
  2. 运行共享 skill 可用的 validation、format 与 `git diff --check`。
  3. 用测试任务执行：Plan → Delivery attachment → closeout → finish → deferred Review → taskReview → card preview（不未经确认 apply）→ context promotion decision。
  4. 验证 Delivery attachment readback、task status、taskReview、closeout 和 context result。
  5. 对公开数字术语执行最终扫描。
  6. 根据实际实施生成本次迭代自身的 Task Delivery 文档；若存在对应 Granoflow task，则作为附件上传并回读。
  7. 执行并发、幂等和恢复 smoke：模拟其他设备更新、`409`、Review 中途失败和同 operation 重试，确认不丢更新且不重复创建。
  8. 执行 privacy fixture，确认原始对话、tool logs 和 secrets 不进入 Delivery/Review/cards/context。
- 产物：gate 结果、smoke evidence、最终 Delivery。
- 完成判定：验收表全部通过或只剩明确外部授权 blocker。

## 9. 验收判定表

| 验收项            | 判定类型      | 通过条件                                                                                                                     | 证据                                          |
| ----------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| 公共生命周期      | 文件/内容     | Analysis、Plan、Delivery、Review 四阶段模板存在                                                                              | templates 文件列表与内容检查                  |
| Profile 结构      | 结构          | learning/software 可单独或组合使用，只追加领域内容且不复制 base                                                              | diff/section review + combined fixture        |
| 模板开头声明      | 内容          | Analysis、Plan、Delivery、Review 均在开头声明作用域、时效和冲突规则                                                          | template contract test                        |
| Analysis 时效     | 内容          | 明确不是项目当前状态，冲突时保留后续 evidence-backed delta                                                                   | template/workflow test                        |
| Plan 时效         | 内容          | 明确不是实际结果，与 Delivery 冲突时以 Delivery 为准                                                                         | template/workflow test                        |
| Delivery 时效     | 内容          | 明确只覆盖本任务 `delivered_at` 时点，后续任务可能修改                                                                       | template/workflow test                        |
| Context freshness | 内容/行为     | Project canonical YAML 有 freshness header；Milestone 使用 steward metadata/managed block；两者均有 conflict report contract | YAML parse + workflow test                    |
| 实现冲突处理      | 行为          | 与代码/运行态冲突时显式报告并建议改代码或改文档，不静默覆盖                                                                  | fixture test                                  |
| 数字命名隔离      | 文本          | 公开模板、工具描述和用户文档无 `project_73/project_76` 等公开类型                                                            | 定向 `rg`；local docs-temp/writer family 排除 |
| Delivery contract | 内容          | 包含 actual deliverables、Analysis/Plan delta、evidence、manual acceptance、residuals、handoff                               | template contract test/review                 |
| Delivery 版本幂等 | 行为          | `task-delivery-vNN.md` 具有 hash、上游 revision 和 as-of acceptance；同版本同内容重试不重复                                  | fixture/readback                              |
| Review timing     | 内容          | elapsed/discussion/AI/wait/manual/rework 及 confidence/evidence 完整，rework 明确为子集                                      | template contract test/review                 |
| Review marker     | 行为          | marker 能区分结构化 Review；非空无 marker 内容必须先 merge/replace confirmation                                              | fixture test                                  |
| Review 可恢复性   | 行为          | taskReview 写入后任一步失败可从最新状态继续，已完成步骤不重复                                                                | fault-injection fixture                       |
| 跨设备并发        | 行为          | material write 使用最新状态/revision；`409` 后重算且不覆盖其他设备更新                                                       | conflict fixture                              |
| 数据最小化        | 安全          | 不持久化原始 transcript/tool logs/secrets，缺失授权时明确 evidence gap                                                       | redaction fixture                             |
| Finish 默认行为   | API/tool plan | 默认不自动写 taskReview/cards                                                                                                | Vitest payload/guidance assertion             |
| Inline 兼容       | API/tool plan | 显式 review 参数仍按旧 contract 转发                                                                                         | Vitest                                        |
| Deferred review   | workflow      | completed + empty taskReview 可被用户发起 Review 后写回                                                                      | fixture/smoke readback                        |
| Closeout 幂等     | workflow      | 重跑替换 marker block，不重复追加                                                                                            | unit/fixture test                             |
| Card owner        | workflow      | 所有卡片操作委托 core card skill 并保留 preview/approval/readback                                                            | reference scan + workflow test                |
| Context promotion | workflow      | 有查重、阈值、目标映射和 unchanged 结果；不机械追加                                                                          | fixture/review                                |
| 数据库无变化      | scope         | 无 schema/migration/table diff                                                                                               | git diff + App status                         |
| UI 无变化         | scope         | 无 Flutter presentation/l10n UI diff                                                                                         | git diff                                      |
| MCP 总门禁        | 命令          | `npm run check` exit 0                                                                                                       | command output                                |
| 文件/方法预算     | 静态门禁      | 新增 templates/profiles/workflows 低于目标；TS 新逻辑不制造大方法                                                            | line/complexity gate                          |
| 真实 readback     | 运行态        | Delivery、finish、Review 和 context 结果均从 App 最新状态回读                                                                | smoke evidence                                |

## 10. 验证与验收

### 10.1 静态分析 / 自动检查

- MCP：`npm run check`。
- Shared skills：使用仓库已存在的 validation/format 入口；若无统一命令，至少运行相关 skill validation、Markdown/YAML 解析检查和 `git diff --check`。
- 数字术语扫描必须区分：
  - `/Users/will/code/skills/70-*` 等本地合法目录；
  - `docs-temp` 历史计划；
  - public bundled skill/tool/docs 中的不合法泄漏。

### 10.2 自动化测试

- `granoflow_task_finish` 默认 deferred-review guidance。
- 显式 inline compatibility payload。
- workflow skill resource 包含 Delivery/Review references。
- 模板必需章节和枚举。
- learning + software-development Profile 组合路径。
- closeout marker 幂等替换。
- Project Context promotion entry YAML 可解析且字段齐全。
- 四类任务模板的 scope notice 位于开头而非埋在尾部。
- Project Context freshness header 可解析；Milestone steward metadata/managed block 支持 stale/partial/source_gap/reconcile_failed。
- 非空且无 Review marker 的旧 `taskReview` 不被静默覆盖。
- Delivery 后补手工验收只更新节点/closeout，不制造新 Delivery。
- taskReview 已写、card apply 前失败后重试不重复 Review 或卡片。
- Project/Milestone promotion confirmation deferred 时，其他已确认步骤可完成并保留恢复状态。
- `409` 后读取最新 task/node/context 并重算受影响 diff。
- 同 operation 重跑不重复 card、attachment 或 YAML entry。
- secret fixture 和原始 transcript/tool log 不进入持久化产物。
- legacy inline review 参数在兼容路径仍保持原 wire contract。

### 10.3 手工 / 契约验收

- 以一项 general task 检查 base-only 路径。
- 以一项 learning fixture 检查 capability evidence 与 learning review。
- 以一项 software-development fixture 检查 actual change surface、static/runtime evidence 和 rework root cause。
- 以一项同时属于 learning 与 software development 的 fixture 检查双 Profile 合并且不重复章节。
- 确认普通 MCP 用户无需理解任何数字编号。
- 确认用户可在任务完成若干天后单独发起 Review。

### 10.4 高风险回归点

- 旧客户端显式传 taskReview/cards 时被静默丢弃。
- Agent 误把 Delivery 当 Review，提前评价效率。
- Agent 在 finish 时继续自动创建卡片。
- Agent 把每条 taskReview 机械追加进 Project Context。
- Agent 把 Analysis 或 Plan 当作当前实际状态。
- Agent 把旧 Delivery 当作后续任务完成后的最新状态。
- Agent 发现文档与代码冲突后静默选择一边，既不报告也不提出同步建议。
- Agent 因代码已经偏离而自动改写仍然有效的规范性 Project Rules。
- Review 时间段重复计算，导致总时间失真。
- 非空无 marker 的历史 taskReview 被误判为新 Review 并覆盖。
- Review 在 taskReview 写入后失败，重试导致重复卡片或 Project Context entry。
- 其他设备更新任务/节点后，Agent 仍按旧 revision 写回。
- Milestone 被错误实现为新的 YAML attachment，或 active/archived 字段边界混淆。
- 原始 transcript、tool logs 或秘密材料进入持久化 Review/Card/Context。
- completed task 无法通过当前 API 更新 taskReview。
- bundled 与 shared skill 同一意图产生不同默认路径。
- 数字编号从本地 adapter 再次泄漏到公开 enum 或提示。

## 11. 阻塞分流、风险与回滚

### 局部阻塞

- 某个 shared skill validation 不可用：记录具体原因，继续完成 bundled/MCP 非阻塞项，但不得声称 shared 同步已验证。
- running App 不可用：完成静态和 fixture 测试，保留真实 readback 为 blocker。
- Review Card apply 需要用户批准：保留 preview 和 operation ids，不代替用户批准；不阻塞 taskReview 草稿与其他 context decision。
- Project Rules promotion 需要确认：返回 proposal，允许 factual snapshot 及其他安全步骤继续。
- Review 中途写入失败：保存各步骤状态和 stable operation id；下一次从最新 Granoflow 状态恢复，不回滚已成功且 readback 的独立步骤。
- 并发 revision conflict：重新读取并重算受影响 diff；若新状态改变已确认语义，重新请求该部分确认，不阻塞无冲突步骤。

### 全局阻塞

- completed task 无法安全更新 taskReview；
- Delivery attachment 无法在完成前安全写入和回读；
- 新默认行为必须破坏已发布 wire contract 才能实现；
- 无法区分公开数字泄漏与本地合法治理，导致批量误删本地约定。

### 主要风险

- 以文本 marker 代替独立 review 状态字段仍会限制高效查询；第一版用明确 tri-state 规则控制风险，并保留未来 schema 升级触发条件。
- `granoflow_task_finish` 名称仍可能让调用者假定包含 Review；必须用工具描述和 workflow 明确阶段边界。
- Delivery 与 Review 内容重复；模板必须按事实/过程拆分。
- 时间证据在不同 Agent 客户端不一致；必须允许 unknown，不能要求虚假精度。
- Profile 可组合后可能重复字段；基础模板拥有公共字段，Profile 只能追加领域字段并由组合 fixture 防漂移。
- 多步 Review 存在部分成功；必须用稳定 operation id、逐步 readback 和独立状态恢复。

### 回滚方式

- 模板/workflow 回滚：恢复旧 references 与路由，不影响 App 数据结构。
- 工具描述/guidance 回滚：恢复旧 `src/tools.ts` 文案和测试。
- 保留 optional legacy 参数意味着回滚不需要数据迁移。
- 已生成的 Delivery/Review 附件保持历史证据，不删除；错误版本通过新版本 `supersedes`。

### 未来升级触发条件

只有出现以下情况时，另写计划评估 App schema/API：

- 需要高效查询大量 completed-but-unreviewed tasks；
- 需要独立 reviewedAt、reviewer、review version 或 review state；
- 需要 App UI 中显示 review backlog；
- taskReview 文本无法支持可靠迁移、索引或同步冲突处理。

## 12. 收尾动作

- 需要更新的 Current Snapshot：只有实际实现改变 MCP workflow/capability current state 时更新 Project Context snapshot。
- 需要更新的 Project Rules / Specification：记录公开语义名、本地编号隔离、Delivery/Review 边界和 card owner 不变量。
- 需要更新的 Decision Record：记录“完成与回顾默认解耦、保留 explicit inline compatibility、第一版不加 schema”的原因与未来触发条件。
- 需要更新的任务描述：使用 closeout marker 指向 active Analysis、Plan、Delivery，并标记 Review pending/completed。
- 是否需要 git commit：实施完成且门禁通过后，按各仓规则分别提交；本计划写入本身不自动提交。
- 是否需要 git push：否，除非用户另行授权。
- 是否需要发布：否，除非用户另行发起 release；届时从 npm 云端版本计算最小可发布版本。
- context upkeep：实施完成后根据 Project Context 变化执行 done/not-needed/skipped 判定。
- 最终交付物：
  - 新模板族；
  - Delivery/Review workflow；
  - 更新后的 finish 兼容契约；
  - 同步后的 bundled/shared skills；
  - contract tests 和真实 readback evidence；
  - 本次迭代的 Task Delivery 文档。
