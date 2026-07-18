# 73 执行计划：Grill Finalizer 完整能力安装建议与显式降级

Status: superseded_by_v02_final

Date: 2026-07-15

## 0. 文档角色

- 上游输入：
  - `docs-temp/analysis/70-granoflow-three-layer-governance-20260715.md`
  - `docs-temp/73-final-granoflow-mcp-control-plane-analysis-plan-finalization-v02.md`
  - `docs-temp/73-final-external-skill-routing-and-model-fallback-v02.md`
  - 用户 2026-07-15 最新决定：触发 Grill 且完整外部能力缺失时，先建议安装
    `grill-finalizer` 及当前任务真正需要的 Grill/gstack 辅助能力；用户拒绝、安装
    失败或调用失败后，才使用 Granoflow 内置 Grill。
- 本文角色：在已实施的通用外部 Skill 路由上增加 `grill-finalizer` 的增量实施计划。
- 完成定义：计划内契约、文档、测试、冲突回写和完整质量门禁全部完成；不能只改一处
  文案后宣称实施完毕。
- 执行授权：尚未获得。本文写入不授权修改 workflow、测试、commit、push、发布或
  安装第三方 Skill。

## 1. 适用性裁剪说明

- 必须写正式 73：本次改变跨越外部 Skill 路由 owner、Task Work Grill 路径、公开
  README、长期治理解释和契约测试，并替换已实施 73 中的一项可靠性决定。
- 实施类型：bundled Skill 工作流、文档治理、契约测试。
- 数据库表结构：无变化。现行实现只通过 Markdown reference 指挥宿主 Agent，计划
  不增加表、字段、索引、migration、schema version、回填或同步序列化。
- UI：无变化。安装建议仍由宿主 Agent 在对话中展示，不建设 Granoflow App Skill
  管理页面，不改布局、组件、显隐、空态或错误态。
- Local HTTP API / MCP TypeScript 工具：无变化。MCP 不扫描宿主 Skill，不执行安装，
  不新增 endpoint、tool schema、runtime module 或配置项。
- 文件与方法长度预算：不涉及 Dart/Flutter 或新增运行时代码。Markdown owner 保持
  单一职责；契约测试只增加本次状态分支断言，不复制整段工作流正文。

## 2. 上游结论与本次目标

### 2.1 必须落地的结果

当 Task Work 命中 Grill 条件时，宿主必须区分完整外部能力和内置兜底能力：

```text
Grill 被触发
  |
  +-- 完整且相关的外部能力可用
  |     -> 调用 grill-finalizer
  |     -> Provider Registry 只选择当前任务相关的 Grill/gstack/provider
  |
  +-- 外部能力缺失或不完整
        -> 展示一次可验证的安装建议
        -> 用户同意
        |     -> 宿主安装 -> 重新发现/必要时重载 -> 验证可调用
        |          +-- 成功 -> 调用 grill-finalizer
        |          `-- 失败 -> 明示原因 -> 内置 Grill
        |
        `-- 用户拒绝 -> 记录 declined -> 内置 Grill
```

### 2.2 能力分层

- `external_enhanced`：已安装且允许模型调用的 `grill-finalizer` 本体可运行；它执行
  原生领域问题、意图置信度、问题空间扩展、72/74 冲突门、Decision Review、确认、
  重写与审计，并按 Provider Registry 使用当前环境中适配的辅助 Provider。
- `external_enhanced_with_selected_providers`：除本体外，当前 Review Plan 需要的
  Grill Me 或 gstack provider 已实际发现并可调用。只有这些相关 provider 缺失时才
  建议补装，不把整个系列当成每次评审的强制依赖。
- `bundled_fallback`：用户拒绝、来源/命令不可验证、宿主不支持安装、安装后不可发现、
  重载失败或调用失败时使用的自包含最低能力。它不能冒充完整
  `grill-finalizer`，但必须继续完成最小对抗检查、意图确认、72/74 冲突判断、写入确认
  和审计记录。

“完整能力”不等于机械调用所有 Grill Me 和 gstack Skill，也不等于只安装辅助 Skill
而没有 `grill-finalizer` 本体。Provider Registry 负责按目标、阶段、风险和证据需求
选择 provider；宿主只建议安装会改变本次评审结论或证据质量的缺失能力。

### 2.3 不变量

- Granoflow MCP 仍是控制面，不成为宿主 Skill 安装器或 Provider orchestrator。
- 安装由宿主执行，必须先展示已验证来源、许可、真实安装范围、准确命令及网络、账号、
  费用、数据外发、重载影响，再获得明确授权。
- 用户同意安装只授权展示过的安装动作，不授权 Task Work 写入、Planning、执行、
  commit、push、发布、登录、付费、删除或外发。
- 不复制 `grill-finalizer`、Grill Me 或 gstack 正文，不在 Granoflow 维护动态全量名单。
- 自动 reviewer 只提供证据与建议，不能代替用户做产品、审美或高风险授权决定。
- 同一任务、同一缺失能力和同一原因只提示一次；新任务或能力需求实质变化后可重新建议。

## 3. 范围与边界

### In Scope

- 删除 `grill-finalizer` “缺失时不提供安装建议并立即兜底”的特殊规则。
- 让它继承通用外部 Skill 的安装建议、授权、验证、去重和失败降级状态机。
- 增加完整能力、选择性 Provider 增强和内置兜底的清晰命名与用户报告。
- 让 Task Work Grill 路径在缺失时先暂停于一次安装决定，拒绝或失败后继续内置 Grill。
- 更新旧 73 的设计补充，明确此前“立即兜底”已被本计划替换，其他通用路由决定仍有效。
- 增加契约测试，防止未来恢复静默降级、静默安装或“全系列强制安装”。

### Out of Scope

- 在 MCP TypeScript 中检测宿主目录、运行 shell、下载仓库或安装 Skill。
- 为 Codex、Claude Code、Cursor 等宿主分别实现安装器。
- 把 gstack 全部 Skill 或 Grill Me 系列设为每次 finalization 的硬依赖。
- 修改外部 `/Users/will/code/skills/grill-finalizer`、`docs-grill-finalizer` 或 gstack 源码。
- 新增 Granoflow App UI、数据库字段、Local HTTP API、遥测或跨任务永久拒绝配置。
- commit、push、npm publish 或实际安装任何第三方 Skill。

### 非目标但需避免退化

- `no_review`、light/focused/full 深度选择和最终写入确认仍由完整 finalizer 自己治理。
- 小任务不会仅因 Grill 能力缺失就收到安装提示；只有实际触发 Grill 且缺失能力会触发。
- 宿主无法验证规范来源或安装命令时不得猜测；可展示手工安装来源，但随后应明确进入
  内置兜底，不把任务永久卡住。
- 已有 `external_skills` 通用记录继续作为能力选择 SSOT，不新增平行状态格式。

## 4. 现有能力复用

| 已有能力                                | 本计划如何复用                                                              |
| --------------------------------------- | --------------------------------------------------------------------------- |
| `references/external-skill-routing.md`  | 继续作为发现、安装授权、重发现、去重和 fallback 的唯一 owner                |
| Task Work Document 的 `external_skills` | 分别记录本体及实际相关 provider 的 availability、decision、result、evidence |
| `grill-finalizer` Provider Registry     | 外部完整能力内部负责选择 reviewer，Granoflow 不复制名单和路由算法           |
| bundled Grill                           | 保持离线/拒绝/失败时可继续，不冒充完整外部能力                              |
| `tests/task-workflow-contracts.test.ts` | 增加纯文本契约分支测试，不引入新的测试框架                                  |
| `npm run check`                         | 继续作为 Prettier、ESLint、Ruff、Pyright、build、Vitest 的完整门禁          |

## 5. 状态与用户报告契约

### 5.1 记录方式

继续使用现有记录，不增加新 Schema：

```yaml
external_skills:
  - skill: grill-finalizer
    phase: analysis | planning | review
    purpose: adversarial finalization
    availability: available | missing | unknown
    decision: selected | install_approved | declined | fallback
    result: used | unavailable | install_failed | invocation_failed | model_fallback
    evidence: <host discovery, invocation artifact, or fallback reason>
  - skill: <one actually relevant Grill/gstack provider>
    phase: <actual review phase>
    purpose: <evidence this provider can materially add>
    availability: available | missing | unknown
    decision: selected | install_approved | declined | not_required
    result: used | unavailable | install_failed | invocation_failed | model_fallback
    evidence: <host observation or produced review evidence>
```

不相关 provider 不写入候选清单。若 `grill-finalizer` 本体已可完成任务，缺少可选
provider 不得自动把整次评审降级为 bundled fallback；只在该 provider 对本次证据有
实质价值时建议安装，否则记录 `not_required` 或不记录。

### 5.2 安装建议

提示至少包含：

```text
当前任务需要强化文档评审，但宿主没有发现 <missing capability>。
安装后可获得 <task-specific benefit>。
来源：<verified canonical source>；许可：<known license or unknown>；
安装范围：<one Skill / collection / plugin / repository configuration>；
拟执行命令：<verified command>；影响：<network/account/cost/data/reload>。
是否允许宿主按上述范围安装并验证？如果拒绝或安装失败，我会明确使用 Granoflow
内置 Grill 继续，不会取消任务。
```

若来源、许可或命令无法验证，不提供猜测命令；说明只能建议手工安装，并进入
`bundled_fallback`。用户已明确拒绝时不换一种措辞重复追问。

### 5.3 降级报告

降级时必须一次说明：

- 未使用完整外部能力的原因；
- 当前实际使用 `bundled_fallback`；
- 仍保留哪些最低门禁；
- 缺少哪些增强能力或证据；
- 本次任务会继续，除非用户此前明确把外部能力设为硬依赖。

禁止使用“完整 Grill 已完成”“与 `grill-finalizer` 等价”或其他混淆能力层级的表述。

## 6. 影响面与改动清单

| 文件                                                                               | 计划改动                                                                      | 结构预算                         |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------- |
| `skills/granoflow-agent-workflow/references/external-skill-routing.md`             | 删除立即兜底特例，增加 finalizer 能力层级、一次安装建议和选择性 provider 规则 | 仍是唯一 owner；净增不超过 55 行 |
| `skills/granoflow-agent-workflow/references/task-work-document-workflow.md`        | Grill 路径改为可用、同意安装、拒绝/失败三分支                                 | 净增不超过 30 行                 |
| `skills/granoflow-agent-workflow/SKILL.md`                                         | 高层 contract 与 success criteria 同步，不复制状态机                          | 净增不超过 15 行                 |
| `README.md`                                                                        | 公共说明从“缺失立即兜底”改为“先建议、后显式兜底”                              | 净增不超过 12 行                 |
| `tests/task-workflow-contracts.test.ts`                                            | 覆盖触发、安装建议、授权隔离、重发现、选择性 provider、拒绝和失败降级         | 复用现有 helper，不新增测试模块  |
| `docs-temp/73-final-external-skill-routing-and-model-fallback-v02.md`              | 追加设计替换说明，不篡改历史实施记录                                          | 只增加补充说明                   |
| `docs-temp/73-final-granoflow-mcp-control-plane-analysis-plan-finalization-v02.md` | 追加外部增强优先、内置兜底不等价的补充                                        | 只增加补充说明                   |

预计修改 7 个文件，但全部属于同一 bundled workflow/治理契约链；不新增 class、service、
runtime code 或 artifact 类型。共享语义只写在 `external-skill-routing.md`，其余文件引用
或保留高层摘要，避免 DRY 退化。

## 7. 分阶段实施步骤

### 阶段 1：替换长期路由决定

- 修改唯一 owner，删除“不暂停 fallback 来建议安装”的 `grill-finalizer` 特例。
- 定义 `external_enhanced`、选择性 provider 增强和 `bundled_fallback`。
- 明确只有 Grill 已触发且缺失的相关能力会进入一次安装建议。
- 明确外部本体与辅助 provider 分别记录；不维护系列全量名单。
- 完成判定：唯一 owner 能独立回答可用、缺失、同意、拒绝、安装失败、重发现失败和
  调用失败的下一状态。
- 失败回退点：若必须让 MCP runtime 扫描或安装，停止实施并回到 Analysis。

### 阶段 2：接入 Task Work 与公共说明

- 更新 Task Work Grill 分支和 Agent Workflow 高层 contract。
- 更新 README，向用户真实说明完整外部能力与内置兜底的区别。
- 保持 Analysis/Planning/执行授权彼此隔离；安装完成不得自动写入或实施任务文档。
- 完成判定：三个入口没有“缺失立即兜底且不建议安装”的旧语义，也没有“安装所有
  gstack 才能评审”的新误导。

### 阶段 3：回写旧决定并建立防回归测试

- 给两个已实施 73 添加 dated design replacement note，保留历史实施事实。
- 在 `tests/task-workflow-contracts.test.ts` 增加下列 CRITICAL 回归契约：
  1. Grill 未触发时不建议安装；
  2. 已安装且允许调用时直接使用 `grill-finalizer`；
  3. 缺失时先展示一次来源、范围、命令和影响明确的安装建议；
  4. 用户同意后必须重发现，不能只凭命令 exit code 认定可用；
  5. 用户拒绝后明确使用 bundled fallback 并继续；
  6. 安装、重载、重发现或调用失败后明确 fallback 并继续；
  7. 来源或命令未知时不猜测，也不会永久阻塞；
  8. 只选择当前任务相关 provider，不强制安装或调用完整系列；
  9. 安装授权不等于 Task Work 写入、Planning、执行或高风险授权；
  10. MCP 不承担扫描、安装或调用外部 Skill。
- 对 README、Agent Workflow、Task Work workflow 和唯一 owner 组成的活动契约集合增加
  反向断言，禁止继续出现“缺失时不建议安装并立即 bundled Grill”及“bundled Grill
  与完整 finalizer 等价”的旧语义；不能只验证新句子存在。
- 完成判定：定向 Vitest 与完整 `npm run check` 都通过。

### 阶段 4：一致性审计与收尾

- 全仓搜索 `grill-finalizer`、`immediately use bundled Grill`、`complete bundled Grill`
  等旧语义，逐项分类为应更新的活动契约或保留的历史记录。
- 检查 package 内 reference manifest/read smoke 仍可读取更新后的 owner。
- 回写本计划实施记录，列出实际文件、计划差异、测试数量和质量门禁结果。
- 不自动 commit、push、publish 或安装第三方 Skill。

实施顺序为串行。所有步骤修改同一 workflow 契约，拆分 worktree 会增加同文件冲突，
没有有价值的并行化机会。

## 8. 验收判定表

| #   | 验收项             | 通过条件                                                      | 证据           | 对用户的非技术说明               |
| --- | ------------------ | ------------------------------------------------------------- | -------------- | -------------------------------- |
| A1  | 只在实际需要时提示 | Grill 未触发时无安装建议                                      | 契约测试       | 小任务不会被无关安装打断         |
| A2  | 完整能力优先       | 可用时调用 `grill-finalizer`                                  | 契约文本与测试 | 已安装的优质能力会真正使用       |
| A3  | 缺失先建议         | fallback 前存在一次可验证安装选择                             | 契约文本与测试 | 用户先获得改善体验的机会         |
| A4  | 安装必须授权       | 来源、许可、范围、命令、影响完整且需确认                      | 契约测试       | 不会静默修改用户环境             |
| A5  | 安装后验证         | 必须重发现/重载验证，不只检查 exit code                       | 契约测试       | “装过”不会被误报成“能用”         |
| A6  | 拒绝后继续         | `declined -> bundled_fallback`                                | 契约测试       | 拒绝安装不会取消任务             |
| A7  | 失败后继续         | install/reload/discovery/invocation failure 均有显式 fallback | 契约测试       | 环境故障不会让流程假死           |
| A8  | 不强装全系列       | 只建议当前 Review Plan 相关 provider                          | 契约文本与测试 | 不为一个问题安装一整套无关工具   |
| A9  | 能力层级诚实       | bundled fallback 不宣称等价于完整 finalizer                   | README 与测试  | 用户知道本次评审实际用了什么     |
| A10 | 授权隔离           | 安装不授权文档写入、执行或高风险操作                          | 契约测试       | 一次“同意安装”不会被扩大解释     |
| A11 | MCP 保持薄控制面   | 无 runtime 扫描、shell、下载或安装代码                        | diff 审计      | MCP 不侵入宿主环境               |
| A12 | 长期规则闭环       | 两份旧 73 标记被替换的具体决定                                | 文档 diff      | 后续 Agent 不会重新实现旧语义    |
| A13 | 完整门禁           | `npm run check` exit code 0                                   | 命令输出       | 文档、代码和测试整体保持健康     |
| A14 | 宿主行为验收       | 五个场景的回答符合状态机且无授权扩大                          | 场景验收记录   | 规则不只在文本测试中“看起来存在” |

## 9. 验证与验收

### 9.1 静态与自动化检查

实施时先运行定向测试：

```bash
npx vitest run tests/task-workflow-contracts.test.ts tests/workflow-resources.test.ts
```

通过条件：所有相关契约和 package reference 测试通过。

随后运行：

```bash
npm run check
```

通过条件：Prettier、ESLint、Ruff、Ruff format、Pyright、TypeScript build、Python
tests 和全部 Vitest 均退出 0。

### 9.2 契约路径覆盖图

```text
Grill trigger
  +-- false -> no provider discovery/install suggestion [contract test]
  `-- true
       +-- finalizer available/model_allowed -> invoke -> used [contract test]
       `-- missing/unknown
            +-- verified source + command -> ask once [contract test]
            |    +-- approved -> install -> rediscover
            |    |    +-- available -> invoke -> used [contract test]
            |    |    `-- failed -> report -> bundled fallback [contract test]
            |    `-- declined -> report -> bundled fallback [contract test]
            `-- unverified source/command -> no guessed command -> bundled fallback [contract test]

Provider Registry
  +-- relevant provider available -> use and record evidence [contract test]
  +-- relevant provider missing -> optional bounded install suggestion [contract test]
  `-- unrelated provider -> no install and no invocation [contract test]
```

这是一条 Markdown/prompt contract 路径，没有真实 MCP runtime 分支、页面或外部网络
调用，因此使用 Vitest 文本契约测试而不是浏览器 E2E。实施时不得通过真实安装第三方
Skill 来完成自动测试。

仓库当前没有专用 prompt-eval suite。本次不新建评测框架，但必须用一个能够读取打包
reference 的宿主 Agent 对以下固定场景做行为验收，并保存简短输入/决策/结果记录：

1. Grill 未触发：不建议安装；
2. `grill-finalizer` 已可用：直接调用，不再次建议安装；
3. 本体缺失、来源和命令已验证：先请求精确安装授权，不提前运行兜底；
4. 用户拒绝：只报告一次 `bundled_fallback` 后继续；
5. 用户同意但重发现失败：不误报安装成功，明确降级并继续。

验收基线是本计划第 2 节状态图和第 5 节用户报告契约。若宿主无法在隔离环境模拟
availability，不执行真实安装，改用明确声明的能力 fixture；不得接触用户全局 Skill
环境来制造测试状态。

### 9.3 手工一致性检查

- 搜索活动文档中互相矛盾的 “immediately use bundled Grill” 表述。
- 确认 README 公开描述、Agent Workflow 摘要、Task Work 细则和唯一 owner 语义一致。
- 确认历史实施记录仍保留，只通过 dated note 标识具体决定被替换。
- 确认 npm package manifest 仍暴露 `external-skill-routing` reference。

### 9.4 失败模式

| 失败模式                          | 防线                                   | 用户可见结果                    |
| --------------------------------- | -------------------------------------- | ------------------------------- |
| 宿主误判 Skill 已安装             | 安装后重发现与调用证据                 | 明确安装未验证并进入兜底        |
| 安装命令或来源过期                | 禁止猜测，要求 verified source/command | 建议手工安装并使用兜底          |
| 用户拒绝后被重复追问              | task+skill+reason 去重                 | 只说明一次降级后继续            |
| 可选 provider 缺失被当成整套失败  | 本体与 provider 分开记录               | 可继续完整本体评审或选择性增强  |
| bundled fallback 被宣传成等价能力 | 固定能力层级和禁止文案测试             | 用户看到真实降级范围            |
| 安装授权被扩大为实施授权          | 独立授权矩阵和契约测试                 | 安装后仍等待 Task Work/执行确认 |

不存在无测试、无错误处理且对用户静默的关键分支。

## 10. 风险、停止条件与回滚

### 10.1 主要风险

- 安装建议会新增一次交互等待。该等待是用户明确选择的产品行为，只在 Grill 已触发且
  外部能力确实缺失时出现，并通过去重避免反复打断。
- “完整能力”可能被误解为安装全部 gstack。计划通过“本体完整 + 按需 provider 增强”
  分层避免这种误导。
- 宿主安装能力差异很大。无法验证安装路径时必须诚实降级，不能由 MCP 填补宿主能力。

### 10.2 停止条件

- 实施要求 MCP runtime 扫描宿主目录、执行 shell、联网下载或保存宿主安装状态；
- 必须复制或 vendor 外部 Skill 正文才能工作；
- 无法把安装授权与文档确认、执行和高风险授权分开；
- 需要修改 App Schema、Local HTTP API 或 UI；
- 自动测试必须真实联网或真实安装第三方 Skill。

命中任一条件时停止，回到 Analysis，不在调用方增加隐式安装逻辑。

### 10.3 回滚

若新流程造成无法接受的提示噪声或宿主不兼容：

1. 回退 Task Work 和 README 的安装建议分支；
2. 恢复 `grill-finalizer` 缺失时直接 bundled fallback；
3. 保留通用外部 Skill 路由、授权隔离和 bundled Grill 本身；
4. 回退旧 73 的 design replacement note；
5. 重新运行定向测试与 `npm run check`。

不涉及数据库、API、App 或发布版本回滚。

## 11. 72/74 与旧规则冲突

未发现独立 72 或 74 文件要求保留“缺失立即兜底且不得建议安装”。冲突来自两份已
实施 73 及其活动 workflow 文案：

- 旧决定：`grill-finalizer` 缺失或失败时立即运行 bundled Grill，不暂停提出安装建议。
- 新决定：缺失时先给用户一次可验证的安装选择；拒绝、不可安装或失败后才显式兜底。

分类：`auto_resolved_as_design_change`。用户最新意图明确替换旧特例，但不替换以下长期
边界：MCP 只做控制面、宿主负责安装、外部 Skill 非硬依赖、失败后必须可继续、用户
授权不可扩大。实施时通过 dated note 更新旧 73，而不是删除历史记录。

## 12. 收尾与回写

- `71 snapshot`：无。当前没有独立 snapshot 需要更新。
- `72 spec`：无。未发现相关 72；长期规则仍由 Agent Workflow 与唯一 owner 承载。
- `74 decision log`：无现存文件。本计划第 11 节及旧 73 dated note 记录设计替换。
- findings：无独立 findings 文档。
- `git commit`：本计划不授权；实施完成后由用户另行决定。
- `git push`：不授权。
- npm publish：不授权。
- 第三方 Skill 安装：不授权；本文只规划未来宿主在真实任务中的用户确认门。
- 最终交付：更新后的路由 owner、Task Work/Agent Workflow/README、两份旧 73 的
  design replacement note、契约测试和通过的 `npm run check` 证据。

用户后续明确说“实施这个 73”时，授权执行本文全部非外部副作用步骤和质量门禁；不
授权 commit、push、publish 或实际安装第三方 Skill。

## GSTACK REVIEW REPORT

| Review        | Trigger                      | Why                        | Runs | Status | Findings                                        |
| ------------- | ---------------------------- | -------------------------- | ---- | ------ | ----------------------------------------------- |
| CEO Review    | `/gstack-plan-ceo-review`    | Scope & strategy           | 0    | —      | —                                               |
| Codex Review  | `/codex review`              | Independent second opinion | 0    | —      | —                                               |
| Eng Review    | `/gstack-plan-eng-review`    | Architecture & tests       | 1    | CLEAR  | 1 test gap found and incorporated; 0 unresolved |
| Design Review | `/gstack-plan-design-review` | UI/UX gaps                 | 0    | N/A    | No UI change                                    |

**UNRESOLVED:** 0

**VERDICT:** ENG CLEARED. The plan reuses the existing routing owner, adds no runtime
installer or schema, covers negative-contract assertions and five host-behavior scenarios,
and is ready for Grill Finalizer review before implementation.

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
