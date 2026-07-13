# 76 final：交互式任务分析工作流

Status: superseded by v02 after grill-finalizer review

Date: 2026-07-13

## 用户目标

Granoflow 任务分析不应是 Agent 读取任务后一次性生成长文，也不应在问题尚未定义清楚时直接进入计划。分析应先通过一次完整、带 AI 推荐的确认批次建立共同理解，再在用户同意后写入初稿，以初稿为稳定对象进行 Grill Me 式追问和修订，最终形成可复用的分析终稿并判断是否可以进入计划。

快速插入任务仍遵守 `76-final-fast-task-capture-minimal-interruption-v02.md`：插入阶段不生成分析文档、计划文档、节点、附件、回顾或卡片。

## 核心决策

任务分析采用以下状态机：

```text
unanalysed
→ discovery_ready
→ awaiting_analysis_confirmation
→ analysis_draft
→ grill_in_progress
→ analysis_finalized
→ planning_ready | needs_input | user_action | split | redefine |
  defer | abandon | completion_audit
```

用户请求“分析任务”时：

1. Agent 读取任务、项目/里程碑上下文、已有材料和当前对话。
2. Agent 自行预填能从证据确认的内容，不把模板当成空白问卷。
3. Agent 一次性提出全部会影响目标、范围、责任、验收或方向的关键问题，并为每项提供当前理解、推荐答案、理由、备选方案和采用推荐的影响。
4. 用户可以“全部按推荐”、只修改部分编号，或补充遗漏信息。
5. 用户明确同意“写入初稿”后，Agent 才创建分析初稿；“全部按推荐，写入初稿并开始 Grill Me”同时授权初稿写入和 Grill 阶段。
6. 初稿形成后，Agent 运行内置对抗式 Grill；若宿主已经安装兼容的 `grill-me`，可以使用它增强追问，但不得把第三方 skill 作为完成分析的依赖。
7. Grill 追问根据回答渐进进行，每轮只处理仍可能改变目标、范围、责任、验收或最终 Decision 的高价值问题。
8. 每轮 Grill 结论必须修订正文，不能只在文末追加问答。
9. 方向性问题关闭后，形成分析终稿并设置明确 Decision 与 Planning Readiness。
10. 只有 `Planning Readiness: yes` 时，才询问用户是否进入计划文档阶段。

## 分析与计划边界

分析回答：

- 为什么现在出现这个任务；
- 真正期望的结果是什么；
- 怎样证明成功；
- 当前有哪些事实、证据、推断和未知信息；
- 范围、责任和限制是什么；
- 哪些风险或假设会推翻当前判断；
- 现在应该继续、补信息、由用户操作、拆分、重定义、延期、放弃还是完成审计。

计划回答：

- 具体怎样实施；
- 节点如何拆分和排序；
- 使用哪些文件、工具和操作；
- 怎样验证、回滚和停止。

分析阶段不得为了显得完整而提前写具体实施步骤。`How` 在分析 Decision 允许后进入计划。

## 一次性分析确认

Agent 应先预填全部可确认内容，再展示一个批次。每个未关闭决策使用：

```text
问题:
当前理解:
AI 推荐:
推荐理由:
其他选择:
采用推荐的影响:
需要你确认:
```

确认批次必须覆盖七个普适维度，但不要求每个维度都制造问题。证据已经充分的部分应直接列为“AI 已确认”，避免让用户重复提供本地可读取的信息。

### 七维分析框架

1. `Trigger`：为什么现在出现，原始问题来自哪里。
2. `Outcome`：最终希望发生什么变化，谁受益，为什么值得做。
3. `Evidence`：哪些可观察证据证明成功，哪些只能作为辅助信号。
4. `Context`：已确认事实、已有材料、AI 推断和未知信息。
5. `Boundaries`：In scope、Out of scope、AI/用户责任、权限和资源限制。
6. `Risks`：关键假设、阻塞、失败方式和恢复边界。
7. `Decision`：明确选择下一状态及理由。

推荐的用户回复入口：

```text
全部按推荐，写入初稿并开始 Grill Me
```

或者：

```text
除第 3、5 项外，其余按推荐。第 3 项……；第 5 项……。
```

用户只补充信息但没有授权写初稿时，Agent 继续在对话中整理，不创建文件或附件。

## 分析文档模板

分析文档使用一个普适 base template，并按需叠加 profile；不得复制维护三份完整模板。

### 元数据

```yaml
status: draft | grill_in_progress | finalized
task_id: <Granoflow task id>
task_type: general | learning | software_development
purpose: general | learning
created_at: <local timestamp>
updated_at: <local timestamp>
decision: proceed | needs_input | user_action | split | redefine | defer | abandon | completion_audit
planning_readiness: yes | no
```

### Base template

```markdown
# Task Analysis: <任务标题>

## 1. Trigger：触发与问题

## 2. Outcome：期望结果

## 3. Evidence：成功证据

## 4. Context：事实、材料、推断与未知信息

## 5. Boundaries：范围、责任与限制

## 6. Risks：风险、假设与阻塞

## 7. Decision：分析结论

## 8. Profile 补充分析

## 9. Grill Review

## 10. Planning Readiness
```

七个主体章节固定存在。没有适用内容时写“当前无”或“待确认”并说明原因，不能默默省略关键分析维度。

### 事实与证据规则

- `Context` 必须分开“已确认事实”“已有材料与证据”“AI 推断”“未知信息”。
- 每个高风险推断写明依据及推断错误的影响。
- `Evidence` 区分最终完成证据、辅助证据和不足以证明完成的信号。
- `Decision` 必须给出明确出口、推荐理由、真正考虑过的替代方向及未采用原因。
- 分析文档只保存结论、依据和用户确认，不复制聊天流水账或隐藏推理。

## Profile 规则

### General

不增加独立模板，直接使用 base。重点保留交付物、责任人、材料、时间/顺序依赖和可观察结果。

### Learning

在 `Profile 补充分析` 中增加：

- 能力目标：记忆、理解、应用、分析或创作；
- 当前基础、困难和前置知识；
- 学习材料是否足够；
- 练习、反馈和错题修正方式；
- 不看答案时的独立掌握证据；
- 下一次复习或再验证触发。

### Software development

在 `Profile 补充分析` 中增加：

- 当前行为、预期行为和复现证据；
- 技术影响面与明确非目标；
- 数据库表结构判断及依据；
- UI 判断及依据；
- API、兼容性、迁移和外部授权影响；
- lint、format、type/static analysis、tests、build 和 runtime smoke；
- 必须回查的用户真实表面；
- 发布、回滚和停止条件。

混合任务允许：

```yaml
task_type: software_development
purpose: learning
```

此时分析同时检查交付物是否正确和用户是否能独立理解或修改关键部分。

当前不预先增加 research、creative、operations 等完整 profile。新增 profile 必须由频繁真实任务证明，并且至少改变三个分析维度或验收证据类型。

## Grill 工作流

### 内置 Grill 是必需能力

Granoflow bundled workflow 必须具备最小对抗式分析能力，不能依赖第三方 skill 才能完成：

- 目标是否只是表面问题；
- Evidence 是否会产生假成功；
- Out of scope 是否排除了必要内容；
- 责任划分是否把 AI 能做的工作错误交给用户；
- 哪个推断错误会推翻整个分析；
- 推荐结论产生了什么二阶问题；
- 是否应拆分、重定义、延期或放弃；
- 学习任务能否证明独立掌握；
- 开发任务是否验证真实用户表面和项目门禁。

每个 Grill 项目包含：

```text
Grill 问题:
攻击的原结论:
AI 推荐:
推荐依据:
如果判断错误的后果:
需要用户确认:
```

### 第三方增强边界

- 已安装兼容 `grill-me` 时可以优先用于互动追问。
- 已安装 gstack 时，只按任务风险选择少量相关 lens，例如 `#needs`、`#engineer`、`#qa`、`#debug`、`#careful`；不得无差别运行完整工程工作流。
- 学习和通用任务默认使用 bundled Grill；可以借用适合的思考镜头，但不得询问无关的 Git、CI、部署或回滚问题。
- MCP 安装不得自动安装、克隆或强依赖 `grill-me` / gstack。
- 第三方能力缺失或失败时立即使用 bundled fallback，不得阻塞分析终稿。

### Grill 停止条件

- 没有未解决的方向性问题；
- 目标、范围、责任和 Evidence 相互一致；
- 关键假设已有证据或明确标记；
- 用户已接受主要取舍；
- 剩余问题只影响具体实施方式，不再改变分析 Decision。

## 附件与 description 分工

### 单一事实源

- 完整分析文档：任务分析的详细事实源。
- Task description：原始捕获信息、当前分析摘要、附件/引用状态和下一步。
- Plan attachment：后续具体实施事实源。
- `taskReview`：最终实际结果、验证、偏差、经验和残余风险。

不得把完整分析长期塞进 description，也不得用分析文档覆盖用户最初的触发和目标。

### Description 管理区块

分析初稿或终稿写入后，只更新受控区块：

```text
[ANALYSIS_SUMMARY]
- 类型: general | learning | software_development
- 目的: general | learning
- 状态: draft | grill_in_progress | finalized
- 结论: <Decision>
- 核心判断: <1-3 句>
- 验收方向: <最重要完成证据>
- 责任: AI | 用户 | 双方
- 当前阻塞: 无 | <具体阻塞>
- 分析文档: <附件名、app-owned 引用或安全本地路径>
- 附件状态: attached | local_reference | attachment_api_unavailable
- 下一步: <明确动作>
[/ANALYSIS_SUMMARY]
```

后续更新必须替换该区块，不得重复追加多个分析摘要，也不得删除区块外的原始任务信息。

### 附件优先级与能力现实

1. 优先通过 Granoflow app-owned task attachment capability 上传 Markdown，并按任务 id 回读附件状态。
2. 当前 MCP 尚未暴露通用任务附件一等工具；只有项目上下文附件工具。因此实施前必须调用 capability discovery，不能假设项目附件工具可用于任务附件。
3. 若运行中的 App 或 generic API 已公开受支持的 task attachment 字段/端点，可以通过 MCP 薄适配器使用；不得在 MCP 中重写存储逻辑。
4. 若任务附件能力不存在，保存安全本地 Markdown 文件，在 description 写 `local_reference` 和路径，并明确 `attachment_api_unavailable`；不得声称已经附加或同步。
5. 若附件和安全本地文件都不可用，只在 description 保存压缩后的分析摘要、关键决策、风险和未解决 Grill 问题，不粘贴完整对话。

建议命名：

```text
task-analysis-<safe-task-id>-v01.md
```

同一阶段只有一个明确 active 分析文档。需要保留旧版本时将旧文件标记为 `superseded`，description 始终引用当前 active/final 版本。

## 分析终稿与计划门禁

终稿状态必须与 Decision 一致：

```text
Status: analysis finalized — ready for planning
Status: analysis finalized — blocked on user input
Status: analysis finalized — user action required
Status: analysis finalized — recommend split
Status: analysis finalized — recommend redefine
Status: analysis finalized — recommend defer
Status: analysis finalized — recommend abandon
Status: analysis finalized — completion audit required
```

只有以下条件全部成立时设置 `Planning Readiness: yes`：

- 任务事实与 AI 推断已经分开；
- Outcome、范围和非目标清楚；
- 有可观察的 Evidence 方向；
- 已判断任务类型和责任归属；
- 关键缺失信息、风险和假设已公开；
- Grill 中会改变方向的问题已关闭；
- Decision 为 `proceed`；
- 用户接受主要取舍。

分析终稿完成后，Agent 询问：

```text
分析已经收敛，建议进入计划阶段。是否开始编写计划文档？
```

不得因为分析文档已完成就自动开始执行。

## 与完成任务的关系

本 76 不整体重构完成流程，但冻结以下消费规则：

- 后续计划必须引用当前 analysis final，并继承 Outcome、Evidence、Boundaries、Risks 和用户确认。
- 任务完成时，`taskReview` 应引用分析/计划或完成审计中的验证证据。
- 已经完成但没有事前分析的任务，应写事实性的事后分析和 completion audit，不得补写并冒充事前计划。

## 修改范围

### In scope

- `skills/granoflow-agent-workflow/SKILL.md`
  - 单任务分析入口改为交互式七维确认、初稿授权、Grill 和 Planning Readiness 状态机。
- `skills/granoflow-agent-workflow/references/task-analysis-execution.md`
  - 重写单任务分析阶段，保留执行/等待/节点安全规则。
- 新增 bundled template/profile references：
  - `references/task-analysis-template.md`
  - `references/task-analysis-profile-learning.md`
  - `references/task-analysis-profile-software-development.md`
- `/Users/will/code/skills/granoflow-task-copilot/SKILL.md` 及相关 reference
  - `plan_task` 路由先消费 analysis final，不再从原始任务直接生成计划。
- `/Users/will/code/skills/granoflow-task-runner/SKILL.md` 及 `references/workflow.md`
  - 执行前检查 analysis final；缺失时进入分析流程，而不是只创建计划/审计文件。
- MCP bundled skill contract tests
  - 覆盖状态机、七维框架、一次性 AI 推荐确认、初稿授权、Grill fallback、profile、附件 fallback、description 受控区块和计划门禁。
- README / directory docs
  - 仅同步与 `Analyze the first task` 行为直接冲突的公开事实。

### Out of scope

- Granoflow App 数据库、任务表、schema 或 migration；
- Granoflow App UI、布局、组件或 App 内文案；
- 在本轮新增 App 通用任务附件 API；
- 自动安装或再分发 `grill-me` / gstack；
- 研究、创作、运营等额外 profile；
- 批量 due-task 分析流程的整体重写；
- 任务完成、卡片、first-run import 或 GFMCP 的整体重构；
- npm 或 MCP Registry 发布。

## 数据库表结构判断

无变化。

依据：本修改只调整 MCP bundled/shared skills、Markdown 模板、description 管理区块和契约测试；不新增表、字段、索引、触发器、migration、schemaVersion、RLS、回填或序列化格式。任务附件不可用时使用明确 fallback，不在 MCP 中引入替代存储。

## UI 判断

无变化。

依据：本修改改变 Agent 的分析对话、文档和写回行为，不修改 Granoflow App 页面、组件、布局、显隐、空态、错误态或 App 内文案。聊天中的一次性确认批次由 Agent 输出，不是 App UI。

## 实施步骤

1. 新增 base analysis template 与 learning/software-development profile references。
2. 将 bundled 单任务分析入口改为七维预填和一次性推荐确认；用户授权后才写初稿。
3. 增加 bundled Grill fallback、可选第三方增强和停止条件。
4. 实现 analysis draft/final、Decision 和 Planning Readiness 的文档状态约定。
5. 实现 description `[ANALYSIS_SUMMARY]` 受控替换规则，保留原始捕获信息。
6. 接入 task attachment capability discovery；能力缺失时写安全本地引用和明确 gap code，不声称已附件化。
7. 更新 task-copilot 和 task-runner，使计划/执行消费 analysis final；保留已有授权、节点、完成和安全规则。
8. 更新 contract tests 和必要公开文档。
9. 运行当前仓库与 shared skill 的适用门禁，并做 source-vs-final 审计。

## 验收标准

- 快速插入路径仍不生成分析或计划资料。
- 用户请求分析时，Agent 一次性展示所有未关闭关键问题和每项 AI 推荐，而不是逐轮零散询问或空白问卷。
- 用户未授权写入时，不创建分析文件、附件或 description 分析区块。
- 用户可用“全部按推荐，写入初稿并开始 Grill Me”一次性授权初稿和 Grill。
- 初稿包含七维 base、匹配 profile、事实/推断分离、Evidence 分级、明确 Decision 和 Planning Readiness。
- Grill 问题攻击初稿结论，产生的决定实际修订正文。
- 未安装 `grill-me` / gstack 时 bundled Grill 可以独立完成流程。
- 学习、编程开发和通用 fixture 分别得到合适 profile，不出现无关工程或学习问题。
- 完整分析优先成为真实任务附件；能力不可用时明确记录 `attachment_api_unavailable` 和安全本地引用，不误报附件或同步。
- description 保留原始任务信息，只维护一个 `[ANALYSIS_SUMMARY]` 区块。
- 非 `proceed` Decision 不会错误进入普通计划。
- `Planning Readiness: yes` 前不会创建执行计划或开始执行。
- 分析终稿后仍需用户确认才进入计划阶段。
- `npm run check` 通过。
- 所有新增或修改 Markdown 文件通过 Prettier 或项目适用 Markdown lint。

## 回滚

若交互式分析导致流程过重、用户无法完成确认或附件写回不稳定：

1. 回退 bundled/shared skill 和 contract tests 到当前单任务分析规则。
2. 保留已创建的分析 Markdown 作为本地文档，不删除用户任务数据。
3. 移除或更新 description 中受控 `[ANALYSIS_SUMMARY]` 区块，不覆盖原始描述。
4. 不需要数据库或 UI 回滚。

## 残余风险

- 一次性确认批次可能较长；实现时必须只展示真正未关闭的决策，并把已确认事实压缩列出。
- 用户“全部按推荐”会提高效率，也可能让错误假设快速进入初稿；Grill 必须优先攻击高风险推断。
- 当前缺少通用 task attachment 一等工具，第一版很可能只能使用安全本地引用；真实附件能力需要 App/API 后续提供后再做薄适配。
- `grill-me` / gstack 在不同宿主中的可用性和调用名称不稳定，不能写成强依赖或成功条件。
- analysis template 与 profile 若重复维护完整结构会漂移；实现必须保持一个 base 加薄 profile。
