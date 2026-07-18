# Archived draft：73 任务 Plan 文档与节点执行回写 V01

Status: draft for review and confirmation

Date: 2026-07-13

Depends on:

- `76-final-fast-task-capture-minimal-interruption-v02.md`
- `76-final-interactive-task-analysis-workflow-v02.md`

## 用户目标

当一个 Granoflow 任务已经完成交互式分析，并且判断为 AI 可以执行或 AI/用户共同执行时，执行前必须形成一份可确认、可验证、可停止和可回滚的 Plan 文档。即使是编程开发任务，也不能从 analysis final 直接开始修改代码。

Plan 使用一个普适 base template，加 learning 和 software-development 薄 profile。项目已有 73/76 等更严格计划规则时，项目 73/76 直接充当该任务唯一 Plan，不再额外生成一份内容重复的通用任务计划。

本计划同时覆盖 `/Users/will/code/granoflow` 与 `/Users/will/code/granoflow-mcp-server`：Granoflow App 负责提供任务节点 Local HTTP API 和既有附件能力，MCP Server 保持薄封装并负责面向 Agent 的一等工具与 bundled workflow。Plan Final 必须作为任务附件上传并回读确认；执行过程中，每个节点只有在 Evidence 满足、状态写回并回读成功后才算完成。

## 核心边界

### Analysis

回答：

- 做什么；
- 为什么做；
- 怎样证明成功；
- 范围、责任和风险是什么；
- 是否应该继续。

### Plan

回答：

- 具体怎样做；
- 由谁做；
- 节点怎样排序和依赖；
- 需要哪些信息和授权；
- 每一步怎样验证；
- 失败时何时停止、怎样恢复。

### Task review

回答：

- 实际做了什么；
- 哪些 Evidence 已满足；
- 与分析和计划有什么偏差；
- 留下了什么经验和风险。

Plan 不得重新定义 analysis final 的 Outcome、Evidence、Boundaries 或用户确认。若这些内容需要改变，应回到 analysis amendment，而不是在计划中静默改写。

## 适用范围

### 必须有 Plan

- 用户要求 AI 执行、推进或完成尚未执行的任务；
- `execution_readiness=ready`；
- `execution_readiness=mixed_user_ai` 且存在 AI 或用户行动节点；
- 编程开发、发布、部署、数据、设计、学习或通用任务进入执行阶段；
- task-runner 或 GFMCP 准备执行任务。

### 不写事前 Plan

- 快速插入任务；
- analysis 尚未 final 或 `planning_readiness=no`；
- 用户只要求分析；
- 工作已经真实完成，只需要记录完成。

已经完成但没有事前 Plan 时，写 `completion audit`，不得补写并冒充事前计划。

## Plan 状态

```yaml
plan_status: draft | grill_in_progress | awaiting_confirmation | confirmed | executing | awaiting_manual_acceptance | completed | blocked | superseded
```

状态约束：

- `draft`：尚未 Grill 或确认，不得执行。
- `grill_in_progress`：正在攻击节点、授权、验证和回滚。
- `awaiting_confirmation`：正文已修订，等待用户确认。
- `confirmed`：用户确认 Plan，但只授权 Authorization Matrix 明确包含的操作。
- `executing`：正在按确认 Plan 执行。
- `awaiting_manual_acceptance`：AI 可执行节点已完成，仍有用户手工验收节点待处理；不阻塞其他可安全执行节点，但任务尚未结束。
- `blocked`：信息、授权、依赖或验证阻塞。
- `completed`：所有必需节点、最终验证、task review 和 task completion gate 均已完成，且任务状态已回读为结束。仅节点全部 `finished` 时仍保持 `executing`，直到任务收尾成功。
- `superseded`：分析或范围发生实质变化，旧 Plan 不再是活动真相源。

## Plan metadata

```yaml
task_id: <Granoflow task id>
plan_kind: general | learning | software_development | project_73 | project_76
plan_status: draft
source_analysis: <active analysis final reference>
source_analysis_version: <version>
created_at: <local timestamp>
updated_at: <local timestamp>
confirmed_at: null
confirmed_by: null
execution_readiness: ready | needs_information | needs_authorization | mixed_user_ai | user_action | already_complete | blocked
```

## 创建 Plan 的前置门禁

只有以下条件全部成立时才创建普通 Plan：

```yaml
analysis_status: finalized
decision: proceed
planning_readiness: yes
```

同时必须完成 execution preflight：

- 判断 AI、用户或双方分别执行哪些内容；
- 汇总缺失信息；
- 汇总需要单独授权的操作；
- 识别已经完成、用户必须执行或被阻塞的情况；
- 判断计划所依赖的文件、材料、系统和外部状态是否存在。

若不满足：

- 无 analysis final：进入交互式分析流程；
- analysis final 已过期：写 analysis amendment 并重新确认；
- `needs_information`：一次性请求必要信息；
- `needs_authorization`：列出授权矩阵并等待；
- `user_action`：生成用户行动 Plan，任务保持未完成；
- `already_complete`：写 completion audit；
- `blocked`：记录 blocker，不创建可执行 Plan。

## 唯一 Base Plan Template

```markdown
# Task Plan: <任务标题>

task_id: <id>
plan_kind: general | learning | software_development | project_73 | project_76
plan_status: draft
source_analysis: <analysis final>
source_analysis_version: <version>
created_at: <time>
updated_at: <time>
execution_readiness: <state>

## 1. Analysis Inheritance

### Outcome

### Evidence

#### Final evidence

#### Supporting evidence

#### Insufficient signals

### Boundaries

#### In scope

#### Out of scope

### Risks inherited from analysis

### User-confirmed decisions

## 2. Recommended Approach

### Recommended solution

### Why this approach

### Alternatives considered

### Assumptions

## 3. Execution Nodes

## 4. Dependencies And Order

## 5. Information Readiness

## 6. Authorization Matrix

## 7. Verification Plan

## 8. Failure, Rollback And Stop Conditions

## 9. Granoflow Writeback Plan

## 10. Plan Grill

## 11. Confirmation And Execution Readiness
```

所有主体章节固定存在。简单任务可以很短，但不能省略 Analysis Inheritance、节点完成条件、授权、Verification、停止条件和确认门禁。

## Analysis Inheritance

Plan 必须引用当前 active analysis final，并原样继承：

- Outcome；
- Final / supporting / insufficient Evidence；
- In scope 和 Out of scope；
- Risks；
- 用户已确认的方向性决定。

如果 Plan 推荐方案无法满足任一 Final Evidence，Plan 不合格。若需要修改继承内容，必须回到 analysis amendment。

## Recommended Approach

记录：

- 唯一推荐方案；
- 为什么该方案最符合 analysis final；
- 真正考虑过的替代方案和未采用原因；
- 方案成立依赖的假设；
- 假设错误时影响哪些节点。

不得为了“安全”缩小用户已经确认的目标，也不得把多个互斥方案都留给执行阶段再决定。

## Execution Node Contract

每个主要节点使用：

```markdown
### Node <N>: <具体动作>

- 负责人: AI | 用户 | 双方
- 前置条件:
- 具体动作:
- 可交付物:
- 交付标准:
- 完成条件:
- 验证证据:
- 验收方式: automated | ai_review | user_manual
- 手工验收说明: 无 | <用户需要检查什么、在哪里检查、怎样判定>
- 下游启动需求:
- 交接判定:
- 阻塞条件:
- 停止条件:
- AI 可以提供的帮助:
```

节点必须产生可观察、可验证、可被下游消费的交付物。`可交付物` 说明具体交出什么；`交付标准` 使用可判定条件定义质量、完整性、格式、位置或状态；`下游启动需求` 明确直接后继节点开始前必须获得什么；`交接判定` 证明当前交付已经足以满足这些需求。以下不合格：

- 研究一下；
- 开始处理；
- 完善细节；
- 继续执行。

以下同样不合格：

- 只写“代码完成”“文档完成”“测试通过”，但没有指出 artifact、范围和可判定标准；
- 当前节点达到自身局部完成条件，却没有提供下一节点所需的输入、权限、标识符、文件、决策或 Evidence；
- 把“由下一节点自行补齐缺口”当作交付完成；
- 仅凭执行者声明完成，无法由系统、用户或后继节点独立验证。

通常保持 3–7 个主要节点。超过 7 个主要节点时，Plan Grill 必须判断是否应拆分任务；子步骤可以位于节点内部，不机械升级为主要节点。

用户节点不得被 AI 标记完成。AI 可以准备材料、检查结果或提供提醒，但最终 Evidence 必须来自用户实际行动或外部回读。

### 延后用户手工验收

若某项只能由用户手工验收，Plan 应建立独立的 `user_manual` 验收节点，明确验收对象、入口、步骤和通过标准。该节点保持 `pending`，并在 description 标记“待手工验收”；AI 不得代替用户标记 `finished`。

手工验收默认不是执行依赖，不得阻塞后续节点。后续节点的启动判断使用已经完成的交付 Evidence、自动验证和安全条件，不把“用户尚未点击确认”当作 blocker。Plan 的依赖边必须将手工验收标为 `non_blocking_acceptance`，不得误写为后续执行节点的必需上游。

AI 应继续完成其余所有可安全执行节点。全部 AI 工作结束但仍有手工验收节点时，将 Plan 设为 `awaiting_manual_acceptance`，写入截至当前的 task review，并把待验收对象、入口和标准留在任务中；任务保持未结束。用户之后可以完成验收并把相应节点标记为 `finished`。最后一个必需验收节点完成时，必须复用 Granoflow 既有节点到父任务的状态传播，使用户仅完成并标记该节点即可结束任务；不得要求用户重新召唤 Agent 或再下达“完成任务”指令。

若用户拒绝验收，节点保持 `pending`，任务保持未结束，并记录拒绝原因或需返工项。后续 Agent 重新进入时，从该验收 Evidence 和返工需求继续，而不是把先前 AI 节点全部重做。

如果后续动作本身不可逆，或缺少用户授权而不能合法执行，这属于 Authorization Matrix 或安全门禁，不得伪装成“手工验收阻塞”；仍按授权规则停在该动作前。

### Granoflow 最新状态为运行时 SSOT

用户可能在其他设备验收节点、修改任务描述、调整节点、添加附件或直接结束任务。执行阶段以 Granoflow 当前可回读状态为唯一运行时事实来源；对话记录、本地 Plan、description 摘要和 Agent 上一次读取结果都是可能过期的缓存，不得单独作为继续执行或写回依据。

Granoflow App 已有跨设备实时同步触发链：桌面端通过 `DesktopSyncSignalSocket` 接收轻量 `sync_changed`，交给统一后台同步协调器更新本地状态。该能力直接复用，不在 MCP Server 新建 WebSocket、同步协议、heartbeat 或周期轮询。实时信号是“本地状态可能变化”的失效通知；同步完成后的 Granoflow Local HTTP API 回读结果才是 Agent 的判断依据。

当前同步信号由 App 接收，并不等于 MCP 进程获得业务数据事件。运行中的 Agent 在节点和 mutation 边界主动回读 Local HTTP API；等待用户手工验收期间无需保持 Agent 常驻，用户在任一设备完成节点后由正常 Granoflow 同步和既有父任务状态传播完成任务。

Agent 必须在以下时点重新读取 task、完整 node 列表、相关 attachments 和 description marker：

- 开始或恢复一次任务执行时；
- 每个节点启动前；
- 等待用户、外部系统或跨设备操作之后；
- 更新节点、description、附件或 task review 之前；
- 判断全部节点完成和结束任务之前；
- 任一写入之后，用于确认持久化结果。

每次回读后执行状态对账：

- 节点已被用户标记 `finished`：接受最新状态和 Evidence，不重复执行或覆盖；
- 用户新增、改名、重排或删除节点：保留用户修改，判断是否仍与 active Plan 一致；影响范围、依赖、交付标准或最终 Evidence 时暂停相关节点并进入 Plan amendment；
- description 或附件变化：只修改合法受控 marker，保留 marker 外内容和用户新增附件；
- 任务已结束：立即停止执行，不再次调用完成能力，并回查是否存在需要记录的状态偏差；
- 新状态与本地 Plan 兼容：更新本地执行视图后从最新未完成节点继续；
- 无法判定修改意图或存在相互冲突的同时编辑：fail closed，记录 `task_state_conflict`，不得用旧快照覆盖。

任务和节点写入应携带刚回读的 `updatedAt` 或等价 revision 作为条件更新依据。服务端发现版本已变化时返回结构化冲突（推荐 HTTP `409` 和 `task_state_conflict`），MCP 必须重新读取、重新对账，不得盲目重试旧 payload。若第一版接口尚未提供条件更新，至少执行紧邻写入前回读和写入后回读，并把竞态窗口列为残余风险。

### Granoflow 节点映射

Plan 文档保存完整节点契约；Granoflow task node 只保存简短、可执行的标题，并与 Plan 中的 Node 编号一一对应。标题采用“动作 + 对象或结果”，例如“实现任务节点 Local HTTP API”或“回查 Plan 附件与节点状态”，不得把完成条件、授权矩阵和验证细节重复塞入节点标题。

节点状态复用现有 `NodeStatus`：

```yaml
status: pending | finished | deleted
```

第一版不新增 `in_progress` 或 `blocked` 数据状态。当前节点和 blocker 写入 Plan 执行记录及 description 受控摘要；不得为了工作流方便扩张数据库枚举。

### 节点完成写回协议

每完成一个节点，执行者必须按顺序：

1. 执行节点约定的具体动作；
2. 检查可交付物是否满足全部交付标准；
3. 收集并判断该节点的验证 Evidence；
4. 对每个直接后继节点执行交接判定，确认其启动需求已满足；
5. 以上条件全部成立后，把对应 task node 更新为 `finished`；
6. 通过节点查询 API 回读并确认持久化状态为 `finished`；
7. 更新 description 中的当前节点、节点进度和下一步；
8. 只有以上步骤成功，才进入依赖该节点的后续节点。

节点“自身工作做完”不等于“节点可完成”。只要交付标准未满足，或任一直接后继执行节点仍缺少由本节点负责提供的启动输入，本节点就保持 `pending`，Plan 记录具体缺口。独立的 `user_manual` 验收节点不参与后续执行启动判定。若后继节点的需求发生变化，应先修订并重新确认 Plan 中受影响的节点契约，不能在执行时静默降低交付标准。

用户节点只有在用户明确确认已完成，或存在可回读的外部 Evidence 时，才能标记为 `finished`。API 写入或回读失败时，Plan 保持 `executing` 或转为 `blocked`，记录 `task_node_writeback_failed`，不得在对话、description 或 taskReview 中声称 Granoflow 节点已经完成。

### 全部节点完成后的任务收尾

当 active Plan 中所有必需 task node 均已标记 `finished` 并回读确认后，执行者必须立即进入任务收尾，不等待用户再次提出“完成任务”：

1. 回读完整节点列表，确认不存在仍为 `pending` 的必需节点；
2. 检查最终 Verification Plan 和 Analysis Final Evidence 已全部满足；
3. 生成并写入 task review，记录实际交付、Evidence、计划偏差、残余风险和未产生的卡片理由；
4. 若最后一个节点由当前 Agent 完成，调用任务完成能力把任务标记结束，面向 MCP 时优先使用 `granoflow_task_finish`；若最后一个节点是用户之后完成的手工验收节点，允许 Granoflow 既有父任务状态传播直接结束任务；
5. 回读任务并确认其持久化状态为结束；
6. 将 Plan 设为 `completed`，把 description 摘要更新为全部节点完成、任务已结束，且不再保留“下一节点”。

只要存在未完成的必需节点、最终 Evidence 缺失、task review 写入失败、任务完成调用失败或结束状态无法回读，任务就不得标记结束，Plan 保持 `executing` 或转为 `blocked`。`deleted` 节点只有在已确认的 Plan 修订中明确移出范围时才不计入必需节点；不得通过删除节点绕过完成条件。

## Dependencies And Order

Plan 明确：

- 节点依赖；
- 可并行节点；
- 必须顺序执行的节点；
- 外部人员、材料、系统和时间窗口；
- 哪个失败会使后续节点无效；
- 阻塞时是否允许继续其他安全节点。

对每条依赖边，Plan 还必须明确交接契约：

```markdown
| 上游节点 | 下游节点 | 依赖类型                | 上游交付物 | 下游启动需求     | 交接 Evidence | 满足后允许启动 |
| -------- | -------- | ----------------------- | ---------- | ---------------- | ------------- | -------------- |
| Node 1   | Node 2   | execution_required      | ...        | ...              | ...           | yes/no         |
| Node 1   | Node 3   | non_blocking_acceptance | ...        | 用户之后手工验收 | ...           | 不影响 Node 2  |
```

一个节点有多个后继节点时，分别判断每条依赖边；一个节点依赖多个上游时，只有所有 `execution_required` 交接契约都满足才允许启动。`non_blocking_acceptance` 和其他可选依赖必须在 Plan 中明确标记，不得由执行者临时猜测。

## Information Readiness

分开记录：

- 已有信息；
- 仍需补充的信息；
- 为什么需要；
- 缺失时影响哪个节点；
- 可以安全假设的内容；
- AI 不得猜测的业务、身份、偏好或外部状态。

信息缺口应一次性汇总，并附 AI 推荐。补充信息不等于授权操作。

## Authorization Matrix

```markdown
| 操作           | 执行者  | 是否已授权 | 授权证据 | 未授权时行为 |
| -------------- | ------- | ---------- | -------- | ------------ |
| 本地只读检查   | AI      | yes/no     | ...      | ...          |
| 安全本地修改   | AI      | yes/no     | ...      | ...          |
| 删除或覆盖     | AI/用户 | yes/no     | ...      | 停止         |
| 登录或使用凭据 | 用户    | yes/no     | ...      | 等待用户     |
| 发送消息       | AI/用户 | yes/no     | ...      | 停止         |
| 发布或部署     | AI/用户 | yes/no     | ...      | 停在发布前   |
| 付款或账户操作 | 用户    | yes/no     | ...      | 不执行       |
```

Plan 必须列出：

- 用户确认 Plan 后 AI 可以执行的操作；
- 仍需当前轮次单独授权的操作；
- 任何情况下 AI 都不能代替用户完成的操作。

Plan 确认不能隐式授权发布、部署、发送、付款、登录、使用 OTP、删除、账户修改或其他外部/不可逆操作，除非这些具体动作及影响已经在 Authorization Matrix 中明确展示，并获得适用的明确授权。

## Verification Plan

每条 Analysis Final Evidence 必须映射到一个验证节点：

```markdown
| Analysis Evidence | Plan node | 验证方式 | 判断者       |
| ----------------- | --------- | -------- | ------------ |
| ...               | Node 2    | ...      | AI/用户/系统 |
```

同时定义：

- 节点级验证；
- 最终验证；
- 必须回查的用户真实表面；
- 只能作为辅助信号的检查；
- 无法验证时的停止行为。

不得以“文件已修改”“命令退出 0”“Agent 已执行”代替 Analysis 指定的最终 Evidence。

## Failure, Rollback And Stop Conditions

Plan 明确：

- 失败信号；
- 立即停止条件；
- 可逆与不可逆操作；
- 回滚步骤；
- 无法回滚时的处理；
- 新事实推翻 analysis final 时如何暂停并返回 analysis amendment；
- 同一 blocker 重复时如何停止，而不是无限重试。

## Granoflow Writeback Plan

计划阶段必须说明：

- 确认后写入哪些任务节点；
- task node 与 Plan Node 的稳定映射；
- Plan Final 和 analysis final 的任务附件或安全引用；
- 附件上传后的列表回读与 attachment id/name 记录；
- 每次 mutation 前后的最新状态回读、对账和冲突处理；
- description 只更新哪个受控区块；
- taskReview 最终需要记录哪些 Evidence、偏差和风险；
- 全部必需节点完成后如何触发 task finish 并回读任务结束状态；
- 手工验收节点如何标记、延后并由用户之后完成；
- 是否存在真正值得创建的卡片候选。

Plan 文档使用独立受控摘要标记：

```text
<!-- granoflow-plan-summary:start -->
- 状态: <plan_status>
- Plan: <attachment id/name or safe path>
- 文档状态: attached | local_reference | attachment_upload_failed
- 执行就绪: <execution_readiness>
- 当前节点: 无 | <Node N: title>
- 节点进度: <finished>/<total>
- AI 节点: <count>
- 用户节点: <count>
- 待手工验收: 无 | <count and node titles>
- 缺失信息: 无 | <summary>
- 待授权: 无 | <summary>
- 下一步: <state-level action>
<!-- granoflow-plan-summary:end -->
```

Marker 规则与 analysis summary 一致：无标记时追加，正好一对时只替换内部；重复、缺失、反向或嵌套时返回 `plan_summary_markers_invalid` 并停止自动修改；永不覆盖 marker 外内容。

Plan 确认后必须先保存 Plan Final Markdown，再调用 `POST /v1/tasks/{id}/attachments` 上传，并通过 `GET /v1/tasks/{id}/attachments` 回读确认。成功后写入 attachment id/name 和 `attached`。上传或回读失败时保留安全本地文件，写 `local_reference` 和 `attachment_upload_failed`，不得声称已附件化或同步。

description 不保存完整 Analysis 或 Plan，只保留：原始任务描述、analysis 受控摘要和 plan 受控摘要。任务进入执行后，每次节点完成或 blocker 改变时只更新 plan marker 内部，不覆盖 marker 外的用户内容。

## General Profile

General 不增加完整模板，只在 base 中重点明确：

- 交付物；
- 负责人；
- 材料、时间和外部依赖；
- 可观察完成结果；
- 用户必须执行的动作。

## Learning Plan Profile

薄 profile 增加：

```markdown
## Learning Execution Profile

### Capability progression

### Learning stages

1. 建立基础理解
2. 有提示练习
3. 独立练习
4. 反馈和错题修正
5. 无提示自测
6. 延迟复习

### AI responsibilities

### User responsibilities

### Practice and feedback loop

### Independent mastery gate

### Next review trigger
```

学习 Evidence 必须证明能力变化，不能只证明看完、读过、记笔记或感觉理解。学习任务通常是 `execution_readiness=mixed_user_ai`，用户的独立练习和自测不得由 AI 代替。

## Software Development Plan Profile

薄 profile 增加：

```markdown
## Software Development Execution Profile

### Current And Expected Behavior

### Change Surface

### Database Table Structure

### UI

### Development Sequence

### Quality Gates

### Compatibility And Migration

### Release Authorization
```

必须覆盖：

- 当前行为、预期行为和复现；
- 预计修改/新增文件与明确不修改项；
- 数据库表、migration、旧数据、sync、backup、import 和 rollback；
- UI 变化、复用组件、空态、错误态和用户可见状态；
- format、lint、type/static、tests、build、runtime smoke；
- 最终用户真实表面；
- 兼容性、API drift、发布顺序和回滚；
- commit、push、publish/deploy 的独立授权状态。

推荐开发节点顺序：

1. 复现或添加失败 Evidence；
2. 实现最小完整改动；
3. 定向验证；
4. 静态门禁；
5. 完整项目门禁；
6. 真实用户表面回查；
7. 必要且已授权时进入发布流程。

项目有更严格顺序时以项目规则为准。

## 73/76 作为唯一 Plan

项目规则要求 73 或 76 时：

```yaml
plan_kind: project_73 | project_76
source_analysis: <analysis final>
```

该 73/76 必须吸收通用 Plan 契约中适用的内容：

- Analysis Inheritance；
- Execution Nodes；
- Information Readiness；
- Authorization Matrix；
- Verification；
- Rollback 和 Stop Conditions；
- Plan Grill；
- Confirmation And Execution Readiness。

不得同时生成内容重复的 `task-plan-*.md` 和 `73/76-*.md`。项目 73/76 是唯一活动 Plan，Granoflow description 和后续 taskReview 引用它。

项目规则可以增加数据库、UI、文件/方法长度、模块边界、发布和文档回写要求，但不能削弱 Analysis Evidence、授权、验证、回滚或用户确认门禁。

## Plan Grill

Plan 初稿完成后，Grill 攻击执行方案，不重新讨论已经确认的任务定义：

- 节点是否真的能产生 Outcome；
- 每条 Final Evidence 是否有验证节点；
- 是否遗漏依赖、信息或授权；
- 是否把用户操作伪装成 AI 操作；
- 是否存在假成功；
- 节点顺序是否安全；
- 回滚是否真实可行；
- 是否扩大范围或偷偷修改 analysis final；
- 哪个节点失败会让后续全部无效；
- 是否应该拆分任务。

Grill 结论必须修改 Plan 正文。若发现目标、范围或 Evidence 本身错误，应暂停 Plan，返回 analysis amendment。

## Plan 确认

Grill 收敛后展示：

```text
计划结论:
- 推荐方案:
- 主要节点:
- AI 节点:
- 用户节点:
- 仍需信息:
- 仍需授权:
- 最终验证:
- 不可逆操作:
- 残余风险:
- 确认 Plan 后允许执行:
```

用户明确确认后才能设置：

```yaml
plan_status: confirmed
```

若仍缺少信息、关键授权或用户节点，则 `execution_readiness` 维持对应状态；Plan 可以被确认，但不得谎称可以全自动执行。

## Execution Readiness

开始执行前必须满足：

- analysis final 已确认且仍然新鲜；
- Plan Grill 已完成；
- 用户已确认 Plan；
- 每个节点有负责人、产出、完成条件和 Evidence；
- 每个节点有明确可交付物、可判定交付标准、下游启动需求和交接判定；
- 依赖和顺序明确；
- 当前节点的所有必需上游交接契约均已满足；
- 当前要执行的节点信息充分；
- 当前要执行的操作已获适用授权；
- rollback 和 stop conditions 明确。

只有当前节点满足这些条件时才执行。后续高风险节点仍可停在授权门前，不能因为 Plan 已确认就获得无限授权。

## 修改范围

### In scope

- `/Users/will/code/granoflow`：
  - 在现有 Local HTTP API 中新增 task node 的 list/create/update/delete 窄接口；
  - 直接复用 `NodeService`、`NodeRepository`、`Node` 和 `NodeStatus`，不复制节点业务逻辑；
  - 更新 OpenAPI、路由测试、集成测试与 CLI OpenAPI drift 真相源；
  - 保持现有 task attachment API，补足 Plan 附件上传与回读的契约验证。
  - 复用现有桌面 `sync_changed` WebSocket 与后台同步协调器，不新增同步 transport 或轮询。
- `/Users/will/code/granoflow-mcp-server`：
  - 增加 task attachment list/add/delete 一等工具；
  - 增加 task node list/create/update/delete 一等工具；
  - 工具直接调用 Granoflow Local HTTP API，不增加数据库或 CLI 执行依赖；
  - 增加 capability/version fail-closed、结构化返回和 contract tests。

- `skills/granoflow-agent-workflow/SKILL.md`
  - 在 analysis final 后加入独立 Plan 生命周期、确认和执行就绪门禁。
- 新增 bundled references：
  - `references/task-plan-workflow.md`
  - `references/task-plan-template.md`
  - `references/task-plan-profile-learning.md`
  - `references/task-plan-profile-software-development.md`
- `skills/granoflow-agent-workflow/references/task-analysis-execution.md`
  - 从 analysis final 路由至新 Plan owner，不重复维护 Plan 细节。
- `skills/granoflow-agent-workflow/references/daily-pending-task-triage.md`
  - 将旧的内嵌简版 Plan 模板替换为新 owner 引用。
- `/Users/will/code/skills/granoflow-task-copilot/SKILL.md` 及相关 references
  - `plan_task` 复用相同 Plan owner 和状态门禁。
- `/Users/will/code/skills/granoflow-task-runner/SKILL.md` 及 `references/workflow.md`
  - 执行前要求 confirmed Plan 和当前节点授权。
- MCP bundled skill contract fixtures/tests
  - 覆盖 analysis inheritance、节点、信息、授权、Evidence 映射、附件回读、逐节点完成回写、marker、profile、73/76 SSOT、Plan Grill 和 execution readiness。
- README / directory docs
  - 仅同步与任务 Plan 行为直接冲突的事实。

### Out of scope

- Granoflow App 数据库、task/node schema 或 migration；
- Granoflow App UI、组件或 App 内文案；
- 新增附件存储模型或新的附件 API；
- 新增 `in_progress`、`blocked` 等 NodeStatus；
- 在 MCP Server 重写节点排序、父任务联动或状态传播业务逻辑；
- 在 MCP Server 新建同步 WebSocket、heartbeat、业务数据订阅或周期轮询；
- 自动安装或再分发第三方 Grill/gstack；
- research、creative、operations 等额外 profile；
- task completion/taskReview 底层能力的整体重构；本计划只复用既有 `granoflow_task_finish` 并规定触发门禁；
- npm 或 MCP Registry 发布。

## 数据库表结构判断

无变化。

依据：Granoflow App 已有 task attachments、`Node`、`NodeStatus`、`NodeService` 和 `NodeRepository`。本计划只把既有领域能力暴露为 Local HTTP API，并在 MCP 中薄封装；不新增表、字段、索引、触发器、migration、schemaVersion、RLS、回填或持久化枚举。开发任务自身是否修改数据库仍由 Software Development Plan Profile 单独判断。

## UI 判断

无变化。

依据：本修改改变 Local HTTP API、MCP 工具、Agent 的 Plan 对话、文档和任务 description 写回，不修改 Granoflow App 页面、组件、布局、可见状态或 App 内文案。具体开发任务是否影响 UI 由其 Plan profile 单独判断。

## 代码职责与长度预算

- Granoflow App 的 task node 路由应作为现有 resource route 的窄扩展，业务判断继续委托 service/repository；若现有路由文件接近项目软限制，按 resource protocol 或 node route 的真实职责拆分，不按行数机械切片。
- MCP 一等工具只负责参数校验、capability 检查、HTTP 请求和结构化结果；不得实现节点完成传播、排序算法或附件存储。
- 新增核心方法以单一 HTTP 操作为边界，目标保持在项目软限制内；预计超过软限制时先重划 route、schema、client/tool registration 的职责，再实施。
- 两仓均以各自已有 size/static gate 为准；不得以刚低于硬限制作为结构验收。

## 实施步骤

1. 在 Granoflow App 冻结 task node Local HTTP API 路径、请求字段、状态枚举、排序语义、返回结构和 capability/version 契约，并同步 OpenAPI 真相源。
2. 在 Granoflow App 实现 task node list/create/update/delete 路由，复用既有 service/repository，增加路由、领域联动和 OpenAPI drift 测试。
3. 在 MCP Server 新增 task attachment 与 task node 一等工具，保持默认 dry-run、结构化结果、secret-safe、条件更新冲突和 capability fail-closed。
4. 新增唯一 base Plan template 和 learning/software-development 薄 profile。
5. 新增 Plan owner workflow，定义前置门禁、状态、附件上传回读、节点映射、逐节点完成回写、授权、验证、回滚、Grill 和确认。
6. 将 bundled 单任务分析和 due-task 旧 Plan 逻辑路由到新 owner；更新 task-copilot 和 task-runner。
7. 实现 description plan summary 的安全追加、替换和 fail-closed marker 契约，加入当前节点与完成进度。
8. 明确 73/76 作为唯一 Plan 的组合规则，禁止重复计划真相源。
9. 增加两仓 contract fixtures、相关公开文档和 source-vs-final 审计。
10. 分别运行 Granoflow App 项目门禁和 MCP Server `npm run check`，再以真实本地 App + MCP 完成附件上传、节点创建、逐节点完成、全部节点完成后自动结束任务及回读 smoke test。

## 验收标准

- AI 执行任何尚未完成的任务前都有 active Plan；已完成工作使用 completion audit，不伪造事前 Plan。
- Plan 只从 `analysis_status=finalized`、`decision=proceed`、`planning_readiness=yes` 创建。
- Plan 引用 analysis final，继承 Outcome、Evidence、Boundaries、Risks 和用户决定。
- 每个主要节点有负责人、前置条件、可交付物、可判定交付标准、完成条件、验证 Evidence、下游启动需求、交接判定、阻塞和停止条件。
- 每条节点依赖边明确依赖类型、上游交付物、下游启动需求和交接 Evidence；只有 `execution_required` 输入不满足时才阻止下游启动。
- 3–7 节点是默认密度，超过 7 个主要节点时检查拆分。
- 信息缺口与授权请求分开记录并一次性汇总。
- Plan 确认不隐式授权外部、高风险或不可逆操作。
- 每条 Analysis Final Evidence 映射到一个验证节点。
- 学习 Plan 证明独立能力，开发 Plan 覆盖静态门禁和真实用户表面。
- 项目 73/76 是唯一 Plan，不再生成重复 `task-plan`。
- Plan Grill 结论修改正文；发现分析错误时返回 analysis amendment。
- description 最多一个 plan summary 区块，损坏 marker 时返回 `plan_summary_markers_invalid`。
- Plan Final 通过 task attachment API 上传，并通过附件列表回读成功；失败时写 `local_reference` 和 `attachment_upload_failed`，不误报附件或同步。
- description 的 plan summary 包含当前节点和 `finished/total` 进度，且最多存在一个合法 marker 区块。
- Plan Node 与 task node 一一映射，task node 标题保持简短可执行，完整契约只存在于 Plan。
- 每个节点只有在交付标准满足、Evidence 充分、直接后继节点的启动需求已由本节点满足、状态更新为 `finished` 且回读确认后才算完成；依赖节点不得提前开始。
- 用户节点未经用户确认或外部 Evidence 回读不得由 AI 标记完成。
- `user_manual` 验收节点保持 `pending` 并写入待手工验收清单，但不阻塞后续可安全执行节点。
- 全部 AI 工作结束但仍有手工验收节点时，Plan 进入 `awaiting_manual_acceptance`；用户可之后补验收并标记节点完成。
- 用户把最后一个必需手工验收节点标记为 `finished` 后，Granoflow 通过既有父任务状态传播结束任务，不要求再次调用 Agent。
- 每次恢复、节点启动、mutation 和任务结束判断前都重新读取 Granoflow 最新 task、nodes、attachments 和 description；不以对话缓存或本地 Plan 状态覆盖用户跨设备修改。
- 跨设备变化复用 App 既有 `sync_changed` 长连接和后台同步；MCP 不另建同步连接或轮询，Local HTTP API 回读是 Agent 的最新状态入口。
- 用户已经完成、调整或结束的内容被接受并对账；语义冲突进入 Plan amendment 或返回 `task_state_conflict`，不得盲目重试旧写入。
- task/node 条件更新优先使用 `updatedAt` 或等价 revision；服务端版本冲突以结构化 `409` fail closed。
- 全部必需节点完成并回读后，工作流自动写 task review、调用任务完成能力并回读结束状态，不要求用户再次下达完成指令。
- 任一必需节点、Final Evidence、task review 或任务结束回读未完成时，任务保持未结束，Plan 不得设置为 `completed`。
- `deleted` 节点只有在已确认的 Plan 修订中移出范围后才能排除，不能用删除节点规避验收。
- Granoflow Local HTTP API 暴露 task node list/create/update/delete，且复用既有领域服务与 `pending | finished | deleted` 状态。
- MCP 提供附件和节点一等工具，不通过 CLI、不访问数据库、不复制 App 业务逻辑。
- 用户确认 Plan 后才设置 `plan_status=confirmed`。
- 只有当前节点信息、授权、依赖、验证和 rollback 就绪时才开始执行。
- `npm run check` 通过。
- Granoflow App 仓库规定的 format、analyze、test、OpenAPI drift 和 size/static gates 通过。
- 真实本地联调证明 Plan 附件、任务节点、逐节点完成、全部节点后的任务结束和 description 进度均已持久化并可回读。
- 所有新增或修改 Markdown 通过 Prettier 或项目适用 Markdown lint。

## 回滚

若新 Plan 契约导致流程过重、重复计划或 execution readiness 无法稳定判断：

1. 回退 MCP 节点/附件一等工具和 bundled/shared Plan workflow contract tests。
2. 回退 Granoflow App 新增的 node HTTP routes、OpenAPI 和 capability 声明；既有 Node 与附件领域能力保持不动。
3. 保留已经确认的项目 73/76、task Plan 附件和已合法完成的节点，不删除用户文档或历史 Evidence。
4. 只移除或更新合法的 plan summary 受控区块，不覆盖原始 description 或 analysis summary。
5. 不需要数据库或 UI 回滚。

## 残余风险

- 所有执行任务都要求 Plan 会增加交互成本；简单任务应压缩内容，但不能绕过 Evidence、授权和确认。
- 73/76 与通用模板组合需要清晰 owner，否则未来 Agent 仍可能生成两个计划。
- Local HTTP API 已有附件能力，但 MCP 尚缺附件一等工具；实施完成前通用请求仍可能因参数或 capability 漂移产生不稳定体验。
- NodeStatus 没有 `in_progress` 或 `blocked`，执行中与阻塞状态依赖 Plan/description 表达；未来如确需持久化状态，应另写 analysis，不在本计划顺带扩 schema。
- App 与 MCP 必须按兼容顺序落地；MCP 在旧 App 上必须 fail-closed 并返回明确 capability/version 错误。
- App 能实时收到同步失效信号，但 MCP 不直接订阅该信号；执行中仍必须在安全操作边界回读 Local HTTP API，不能把“App 已长连接”误解为 Agent 缓存自动更新。
- Plan 确认与单个高风险操作授权容易被混淆，Authorization Matrix 和执行前检查必须同时存在。
- 学习任务的最终 Evidence 依赖用户真实行动，AI 不能仅凭材料生成完成任务。

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
