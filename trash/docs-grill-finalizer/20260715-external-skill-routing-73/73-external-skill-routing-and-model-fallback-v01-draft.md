# 73 实施计划：外部 Skill 路由、显式安装建议与模型降级

Status: ready for review

Date: 2026-07-15

Source decisions:

- Granoflow MCP 只做控制面，宿主 Agent/runtime 负责发现、调用和安装外部 Skill。
- Analysis 与 Plan 继续使用统一基础模板；不为每一个外部 Skill 创建 Profile。
- Profile 只表达领域不可遗漏的证据、风险和最低质量门禁。
- `mattpocock/skills` 属于软件开发能力集，只在代码、测试、构建或工程仓库任务中路由。
- 外部 Skill 可用时调用；不可用时显式告知并建议安装；用户拒绝后依赖模型能力继续。

## 用户目标

让 Granoflow 用户只需表达任务目标，宿主 Agent 就能在 Analysis、Plan 和实施阶段
稳定选用相关的优质外部 Skill。外部 Skill 缺失时，用户得到一次清晰、可决定的安装
建议；拒绝安装、安装失败或环境离线时，工作流不被强制阻断，而是明确记录模型能力
降级并继续完成任务。

这套规则必须适用于未来不同来源和领域的外部 Skill，不能与某个仓库的 Skill 名单、
安装器或目录结构形成硬耦合。

## 已冻结边界

- Granoflow MCP 不扫描 Codex、Claude Code、Cursor 或其他宿主的 Skill 目录。
- Granoflow MCP 不执行 shell、包管理器、网络下载或全局安装。
- 宿主 Agent 根据自身可见能力报告 Skill 的可用状态，并负责实际调用。
- 外部 Skill 安装是宿主环境和网络的有副作用操作，必须先向用户展示来源、用途、
  安装范围和实际命令，再获得明确授权。
- 已安装且与当前任务相关的 Skill 可以由宿主直接调用，不要求额外安装确认。
- Skill 缺失时只建议，不伪装为已调用；用户拒绝后立即进入模型能力 fallback，
  不重复施压，也不把拒绝解释为任务取消。
- 安装失败、离线、安装后不可发现或 Skill 调用失败时，记录原因并使用模型能力继续；
  只有该能力是用户明确指定的硬依赖且任务客观无法继续时才进入阻塞。
- 发布、登录、密钥、付费、删除、外发和其他高风险操作仍保留独立授权，不因 Plan
  确认、Skill 可用或安装授权而自动放行。
- 不复制第三方 Skill 正文。第三方来源、许可证和署名按其许可要求保留；Granoflow
  不暗示第三方作者背书。

## 适用性裁剪

### 数据库与迁移

结论：无变化。

本计划只修改 bundled workflow Markdown、基础模板、软件开发 Profile、README 和
契约测试。不新增或修改 Granoflow App 表、字段、索引、migration、schema version、
同步序列化或历史数据，因此没有数据迁移、回填和数据库回滚。

### UI

结论：无变化。

不修改 Granoflow App 页面、布局、组件、空态、错误态或可见文案。安装建议由宿主
Agent 在当前会话中展示，不建设 Granoflow 安装界面，因此无需 UI 草图和视觉验收。

### Local HTTP API 与 MCP TypeScript 工具

结论：无变化。

外部 Skill 可用性属于宿主环境事实，不新增 Local HTTP API endpoint，也不让 MCP
进程检测宿主文件系统。现有 `granoflow_agent_workflow_skill` 和
`granoflow_bundled_skill_reference` 已能分发新增的 bundled Markdown reference；
本计划不修改 `src/tools.ts` 或 `src/workflow-resources.ts`。

## 设计结论

### 三层职责

```text
统一 Analysis / Plan 基础模板
  └─ 记录能力需求、推荐 Skill、可用状态、用户决定、实际采用和 fallback

领域 Profile
  └─ 规定该领域无论使用什么 Skill 都不能遗漏的证据、风险和质量门禁

外部 Skill
  └─ 提供诊断、TDD、架构设计、文案、视觉创作等具体工作方法
```

不建立“一 Skill 一 Profile”。新增、删除或重命名第三方 Skill 不应迫使 Granoflow
新增模板。只有某一领域存在跨 Skill、长期稳定且基础模板无法表达的成功证据或风险
时，才允许增加领域 Profile。

### 统一路由状态

Analysis 和 Plan 使用同一组语义，允许按任务复杂度压缩表达：

```yaml
external_skills:
  - skill: <stable skill name>
    source: <repository, plugin, package, or provider>
    purpose: <why this task needs it>
    availability: available | missing | unknown
    decision: selected | install_approved | declined | fallback | not_required
    result: used | unavailable | install_failed | invocation_failed | model_fallback
    evidence: <host-observed evidence or none>
```

规则：

- `available` 只能来自宿主当前环境的实际发现，不能由 MCP 推断。
- `selected/used` 只记录与当前任务相关且实际调用的 Skill。
- `missing/unknown` 不等于阻塞，先进入一次安装建议。
- `declined` 后必须记录 `model_fallback` 并继续，不得重复询问同一任务中的同一 Skill。
- `install_approved` 只授权已展示的来源、范围和命令；来源、命令或范围改变时重新确认。
- 安装完成后，宿主必须验证 Skill 文件或插件确实可发现，并在需要时提示重载宿主；
  仅凭安装命令退出码不能记录 `available`。
- `evidence` 记录可验证的宿主观察或 Skill 产物，不记录隐藏推理。

### 用户提示契约

缺失提示至少包含：

```text
当前没有发现 <skill>。
它可以帮助本任务获得 <specific benefit>。
来源：<source>；安装范围：<scope>；拟执行命令：<command>。
是否允许宿主 Agent 安装并验证？如果不安装，我会依赖当前模型能力继续。
```

宿主不得使用“必须安装”“无法继续”等措辞，除非用户已明确把该 Skill 指定为硬依赖
且模型 fallback 客观无法满足任务。用户拒绝后用一句话确认降级，然后继续当前阶段。

### 软件开发路由

`mattpocock/skills` 只在任务涉及代码、测试、构建或工程仓库时进入候选集合，包括：

- 前端、后端、全栈、MCP 和 Agent 代码开发；
- Bug 诊断与修复；
- TDD、测试设计、架构设计和代码库重构；
- 包、兼容性、迁移、静态门禁和工程发布验证；
- 包含脚本或代码实现的 Skill 开发。

普通文案、漫画设计、动画创意、非代码调研和通用事务不检查该仓库。仅讨论 Skill
定位、提示词或工作流但不涉及代码实现时，也不强制进入软件开发路由。

软件开发 Profile 不维护第三方 Skill 完整名单。它只要求宿主根据任务所需能力选择
相关 Skill，例如根因诊断、TDD 或架构设计；没有相关 Skill 时仍保留 lint、format、
type/static、tests、build、runtime smoke 和真实用户表面复查等最低门禁。

## 文档契约修改

### 1. 新增统一外部 Skill 路由 reference

新增：

`skills/granoflow-agent-workflow/references/external-skill-routing.md`

该文档成为外部 Skill 发现、调用、安装建议、用户拒绝、安装/调用失败和模型 fallback
的唯一 owner。`SKILL.md`、Analysis workflow、Plan workflow 和 Profile 只引用它，
不得复制完整状态机和提示文案。

### 2. 修改 Agent Workflow 路由

修改 `skills/granoflow-agent-workflow/SKILL.md`：

- 在控制面边界中声明 MCP 不检测、安装或调用外部 Skill；
- 在 Analysis/Plan 路径中要求读取 `external-skill-routing.md`；
- 在 reference catalog 中登记该文档；
- 保留 `grill-finalizer` 的现有首选增强和 bundled Grill fallback，但让它遵循同一
  外部 Skill 可用性与失败语义；
- 不在主 Skill 中硬编码 Matt Pocock Skill 全量名单。

### 3. 修改统一 Analysis 基础模板

修改 `task-analysis-template.md`，在 Profile 之前增加通用
`Capability And Skill Routing` 段，至少记录：

- required capabilities；
- recommended external Skills；
- host-reported availability；
- user decision；
- selected fallback；
- evidence of actual use。

后续章节顺延。简单任务或无需外部 Skill 的任务允许写 `当前无需`，但不得删除该段。

同时把 `AI / user responsibility` 改为“执行方式与用户动作边界”，避免与个人用户
所有权规则混淆；Analysis summary 中的“责任”同步改为“执行边界”。任务仍永久属于
当前个人用户。

### 4. 修改统一 Plan 基础模板

修改 `task-plan-template.md`，增加 `Skill Execution Strategy`：

- node or phase；
- required capability；
- selected Skill；
- unavailable/declined fallback；
- Skill-specific output or evidence。

计划不得因为推荐了外部 Skill 就把它写成隐藏前置条件。只有用户明确批准硬依赖时，
Plan 才能将其设为阻塞前置条件；其他情况必须存在 `model_capability` fallback。

### 5. 修改 Analysis、Plan workflow 与软件开发 Profile

- `task-analysis-execution.md`：在预填阶段识别能力需求；宿主报告可用状态；缺失时按
  统一 reference 提示；拒绝后继续 Analysis，不把安装授权解释成草稿、Plan 或执行授权。
- `task-plan-workflow.md`：Plan 继承 Analysis 的能力决定；实施前重新确认实际可用性；
  安装或调用失败时使用已写明 fallback，不修改已确认 Outcome 和 Evidence。
- `task-analysis-profile-software-development.md`：增加软件任务适用判断和相关工程 Skill
  路由要求，但不写 Matt 仓库全量清单，也不复制具体 Skill 方法。
- 若仓库存在 Plan 软件开发 Profile，则同步使用同一规则；若不存在，不为本计划新建。

### 6. README

修改 `README.md`，公开说明：

- Granoflow 提供外部 Skill 路由规则，不承诺第三方 Skill 随包安装；
- 已安装的相关 Skill 由宿主调用；缺失时由宿主在用户确认后安装；
- 用户拒绝、安装失败或调用失败时使用模型能力继续；
- Granoflow MCP 不扫描或修改宿主全局 Skill 环境。

公共 README 只描述稳定行为，不列出会漂移的第三方仓库全量 Skill 名单。

## 文件与结构预算

| 文件                                                       | 单一职责与修改预算                                        |
| ---------------------------------------------------------- | --------------------------------------------------------- |
| `references/external-skill-routing.md`（新）               | 唯一外部 Skill 路由 owner；目标不超过 180 行              |
| `skills/granoflow-agent-workflow/SKILL.md`                 | 增加 owner 引用和入口规则；不复制状态机，净增不超过 25 行 |
| `references/task-analysis-template.md`                     | 增加一个通用能力路由段并改执行边界命名；不复制领域规则    |
| `references/task-plan-template.md`                         | 增加一个 Skill 执行策略段；不复制安装流程                 |
| `references/task-analysis-execution.md`                    | 接入 Analysis 阶段路由与授权隔离；净增不超过 35 行        |
| `references/task-plan-workflow.md`                         | 接入 Plan 继承、实施前检查和 fallback；净增不超过 30 行   |
| `references/task-analysis-profile-software-development.md` | 保持薄 Profile；只增加适用判断与最低路由要求              |
| `README.md`                                                | 增加一段稳定公共说明；不列动态 Skill 清单                 |
| `tests/task-workflow-contracts.test.ts`                    | 增加文档契约和防回归测试；不另建重复 fixture              |

这些文件均为 Markdown 或现有契约测试；不新增运行时模块、API client 或安装器。若
实施发现必须修改 TypeScript MCP 工具才能探测外部 Skill，应停止并回到 Analysis，
因为这将突破已冻结控制面边界。

## 实施步骤

### 阶段 1：建立唯一 owner

1. 新增 `external-skill-routing.md`，写入发现、选择、安装授权、验证、拒绝和 fallback
   状态机。
2. 明确“相关且可用才调用”“一次缺失提示”“拒绝后继续”“MCP 不安装”的强规则。
3. 将 `grill-finalizer` 映射到同一通用规则，同时保留 bundled Grill 的即时 fallback。

完成标准：所有外部 Skill 行为都能从一个 reference 得到答案，其他文档无需复制流程。

### 阶段 2：接入统一 Analysis 与 Plan 模板

1. 给 Analysis 增加通用能力路由段，并将责任字段改为执行边界。
2. 给 Plan 增加 Skill Execution Strategy。
3. 保证 `profiles: []` 的通用任务也能记录任意外部 Skill；Profile 不成为记录 Skill
   的必要条件。

完成标准：任意领域 Skill 都能写入基本模板；模板不依赖 Matt Pocock 仓库结构。

### 阶段 3：接入工作流和软件开发 Profile

1. Analysis workflow 在建议前识别能力需求并读取统一 owner。
2. Plan workflow 继承能力决定，并在实施前处理可用性漂移。
3. 软件开发 Profile 仅负责工程领域最低证据及相关 Skill 路由，不复制 TDD、诊断或
   架构方法。
4. 确认非软件任务不会被要求检查 `mattpocock/skills`。

完成标准：代码任务得到专业能力建议，其他任务不被无关工程 Skill 干扰。

### 阶段 4：公共说明与契约测试

1. 更新 README 的宿主/MCP 边界和 fallback 说明。
2. 扩充 `tests/task-workflow-contracts.test.ts`，验证模板段落、统一 owner 引用、个人
   用户所有权和禁止静默安装等关键措辞。
3. 运行格式、lint、类型检查和完整测试门禁。

完成标准：文档契约可机器回归，npm package 中新增 reference 可被现有 manifest
自动发现并读取。

## 验收判定

| #   | 验收项                             | 通过证据                                                   |
| --- | ---------------------------------- | ---------------------------------------------------------- |
| A1  | 基础 Analysis 能记录任意外部 Skill | 模板存在通用 capability/skill routing 段                   |
| A2  | 基础 Plan 能记录节点级 Skill 策略  | 模板存在 Skill Execution Strategy 及 fallback              |
| A3  | 不建立一 Skill 一 Profile          | 软件 Profile 无第三方全量名单，文档明确 Profile 判定标准   |
| A4  | 软件任务才路由 Matt 工程 Skill     | Profile/owner 明确代码、测试、构建或工程仓库适用条件       |
| A5  | 可用且相关的 Skill 由宿主调用      | owner 记录 host availability 与 actual use 证据            |
| A6  | 缺失 Skill 显式建议安装            | 提示包含用途、来源、范围、命令和拒绝后的继续路径           |
| A7  | 不静默安装                         | owner 明确用户确认门，契约测试防回归                       |
| A8  | 用户拒绝后模型继续                 | `declined -> model_fallback` 明确且不重复提示              |
| A9  | 安装/调用失败可降级                | 状态和 Plan fallback 均覆盖失败，不伪报成功                |
| A10 | MCP 保持控制面                     | 不新增 Skill 扫描、shell、下载、安装或 TypeScript 执行逻辑 |
| A11 | 个人用户所有权不回退               | Analysis 使用执行边界，Plan 不出现 Owner 分配              |
| A12 | 新 reference 可随包分发            | manifest/read test 或现有 package smoke 发现该 reference   |
| A13 | 项目质量门禁通过                   | `npm run check` 退出码为 0                                 |

## 验证计划

实施后运行：

```bash
npm run check
```

重点断言：

- `external-skill-routing` 出现在 `granoflow-agent-workflow` reference manifest；
- 通过 `granoflow_bundled_skill_reference` 能读取其正文和 SHA-256；
- 文档不存在“由 MCP 安装/调用外部 Skill”的语义；
- 缺失提示包含显式用户授权和 `model_fallback`；
- Analysis 不再使用任务 Owner/责任分配语义；
- Plan 仍使用 `Execution Mode`，不恢复 Owner；
- 非软件任务不要求检查 Matt Skills；
- README 与 bundled workflow 契约一致。

本计划不修改 UI，不需要浏览器 E2E；不修改 App/API，不需要数据库或 Local HTTP API
集成测试。npm package smoke 已覆盖 bundled reference 的实际分发路径，必须保持通过。

## 失败、回滚与停止条件

### 停止条件

- 实施需要 MCP 扫描宿主 Skill 目录或执行安装命令；
- 需要新增 Granoflow App 表、字段、endpoint 或 UI；
- 无法把安装授权与 Analysis 草稿、Plan 确认、执行授权分离；
- 必须复制或 vendor 第三方 Skill 正文才能完成路由；
- 现有 reference manifest 无法自动发现新增 Markdown。

命中任一条件时停止实施，回到 Analysis 修订边界，不在调用方堆临时扫描或安装逻辑。

### 回滚

这是文档契约改动。若实施后造成宿主误路由或过度提示：

1. 回退模板中的新增 capability/skill 段和 workflow 引用；
2. 删除新增 bundled reference；
3. 恢复 README；
4. 保留已实施的个人用户 `Execution Mode` 规则和既有 Grill fallback；
5. 重新运行 `npm run check`。

不涉及数据回滚、migration down 或 App 版本回退。

## 回写与收尾

实施完成后：

- 将本计划状态更新为 implemented，并记录实际修改文件和 `npm run check` 结果；
- 若实现与计划出现差异，记录差异及原因，不静默扩大范围；
- 检查 README、Agent Workflow catalog 和模板术语一致；
- 不提交、不推送、不发布，除非用户另行明确授权。

## 实施授权语义

用户后续说“实施这个 73”，表示授权完成本计划全部阶段和验收项，包括文档修改、
契约测试和 `npm run check`。这不授权提交、推送、npm 发布、第三方 Skill 安装或任何
高风险外部操作。

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
