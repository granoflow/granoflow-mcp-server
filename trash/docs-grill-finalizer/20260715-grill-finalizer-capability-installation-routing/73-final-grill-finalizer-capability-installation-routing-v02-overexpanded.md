# 73 最终计划：Grill Finalizer 可安装能力包与显式降级

Status: superseded_as_overexpanded

Date: 2026-07-15

Supersedes:

- `trash/docs-grill-finalizer/20260715-grill-finalizer-capability-installation-routing/73-grill-finalizer-capability-installation-routing-v01-draft.md`

## 0. 文档角色

- 上游输入：
  - `docs-temp/analysis/70-granoflow-three-layer-governance-20260715.md`
  - `docs-temp/73-final-granoflow-mcp-control-plane-analysis-plan-finalization-v02.md`
  - `docs-temp/73-final-external-skill-routing-and-model-fallback-v02.md`
  - `docs-temp/73-final-unified-adaptive-task-work-document-v02.md`
  - 用户确认：缺少完整 Grill 能力时先建议安装；拒绝或失败后才降级；Grill Bundle
    使用 MIT 许可证。
- 本文角色：同时完成共享 skills 仓库的可安装能力包和 Granoflow MCP 的宿主路由契约。
- 完成定义：能力包可以从全新临时目录安装、发现和 smoke；MCP 工作流可以正确处理
  可用、等待、同意、拒绝和失败；旧治理决定完成回写；两个仓库的适用门禁全部通过。
- 当前授权：只允许写入和确认本计划，不允许实施、安装、commit、push 或发布。

## 1. 适用性与冻结结论

### 1.1 为什么必须写正式 73

本次同时修改两个仓库、多个 Skill/工作流入口、公共分发约定和长期治理文档。仅修改
MCP 提示词会产生“建议用户安装一个实际上没有稳定安装单元的能力”的假完成。

### 1.2 数据、UI 与运行时

- 数据库：无变化。没有表、字段、索引、migration、schema version、回填或同步变更。
- Granoflow UI：无变化。安装建议由宿主 Agent 在对话中展示。
- Local HTTP API：无变化。不新增 endpoint 或 capability。
- MCP TypeScript runtime：无变化。MCP 不扫描宿主目录、不执行 shell、不下载或安装
  Skill，也不保存宿主安装状态。
- 共享 skills 仓库：增加确定性的 Bundle manifest、安装脚本、MIT 许可、测试和文档。

### 1.3 术语冻结

- `Grill Core Bundle`：`grill-finalizer` alias、`docs-grill-finalizer` owner、它们的
  references/metadata、Bundle manifest 和适用 MIT 许可；这是自动完整核心能力的安装单元。
- `selected providers`：Provider Registry 针对当前任务选择的可选外部 reviewer。
- `Grill Me family`：用户主动调用的可选对抗访谈能力；当前 `grill-me` 具有
  `disable-model-invocation: true`，不能计入自动调用的完整核心能力。
- `gstack`：独立的 MIT 第三方能力集合；只按任务选择相关 reviewer，并使用其官方
  安装单元和命令，不复制、再许可或打包进 Grill Core Bundle。
- `bundled_fallback`：Granoflow MCP 随包提供的最低限度 Grill；可继续任务，但不得
  宣称与完整 `grill-finalizer` 等价。

## 2. 用户结果与状态机

```text
Grill 未触发
  -> 不发现、不提示、不安装

Grill 已触发
  -> host discovery
       +-- Grill Core Bundle available + model_allowed
       |     -> invoke grill-finalizer
       |     -> Provider Registry 选择当前相关 provider
       |           +-- available/model_allowed -> invoke + evidence
       |           +-- user_only -> 建议用户主动调用，不自动调用
       |           `-- missing and material -> 可选安装建议或跳过
       |
       `-- Core missing/unknown
             -> install_offered + awaiting_user
                  +-- approved
                  |     -> host installs exact approved bundle
                  |     -> rediscover/reload/smoke
                  |          +-- success -> invoke finalizer
                  |          `-- failure -> report -> bundled_fallback
                  +-- declined -> report once -> bundled_fallback
                  `-- no answer -> persist waiting state; no install and no fallback claim
```

### 2.1 完整能力

`Grill Core Bundle` 成功可调用即代表完整原生 finalizer：适用性分流、原生领域问题、
问题空间扩展、intent-confidence、72/74 冲突门、Decision Review、确认、重写和审计。
外部 Provider 只增加特定证据，不决定核心是否完整。缺少 Grill Me 或某个 gstack Skill
不得把可用的 Core 错误降级。

### 2.2 持久化路由记录

继续复用 Task Work Document 的 `external_skills`，但补齐等待状态：

```yaml
external_skills:
  - skill: grill-finalizer
    source: https://github.com/will-nb/skills
    phase: analysis | planning | review
    purpose: adversarial finalization
    invocation_mode: model_allowed | user_only | unknown
    availability: available | missing | unknown
    decision: selected | install_offered | install_approved | declined | fallback | not_required
    result: pending_user_decision | used | unavailable | install_failed | invocation_failed | model_fallback
    evidence: <host discovery, approved source/scope/command, invocation artifact, or fallback reason>
```

- `install_offered + pending_user_decision` 是唯一等待组合。
- 相同 Task、Skill、source、scope 和 missing reason 不重复提示。
- 恢复会话时先读取该记录；等待中不得重新安装、假定拒绝或宣称已降级。
- 用户拒绝或安装/重发现/调用失败后，记录原因并只报告一次 `bundled_fallback`。
- 新任务、来源或能力需求实质变化后可以重新建议。

## 3. 权限与所有权边界

- Granoflow MCP 只分发控制面规则和读写 Task Work 记录。
- 宿主 Agent 负责发现、展示安装信息、请求授权、安装、重载、验证和调用。
- 安装确认只授权已展示的 source、revision/tag、Bundle、目标目录、命令和影响。
- 任一 source、revision、scope、destination 或 command 改变都要重新确认。
- 安装授权不授权 Task Work 写入、Planning、实施、commit、push、发布、登录、付费、
  删除、消息发送、数据外发或其他高风险操作。
- `grill-me` 为 `user_only` 时，宿主只能说明收益并建议用户主动调用。
- 自动 reviewer 只提供证据与建议，不能代替产品、审美、风险或授权决定。

权限优先级保持：

```text
用户当前明确指令
  > 项目 AGENTS/CLAUDE/仓库规则
  > 已确认 Granoflow Task Work、阶段门和授权矩阵
  > 外部 Skill 工作方法
```

## 4. Grill Core Bundle 分发契约

### 4.1 Bundle 内容

在 `/Users/will/code/skills` 建立一个 machine-readable Bundle owner，例如：

```text
bundles/grill-finalizer/
  bundle.json
  LICENSE
```

`bundle.json` 至少声明：

- stable bundle id 和 version；
- canonical source；
- MIT license path；
- 必需目录：`grill-finalizer/`、`docs-grill-finalizer/`；
- 必需 entrypoints、references 和 agents metadata；
- 可选 integrations：gstack lens index、Grill Me、gstack providers；
- supported install mode：显式 `--dest` 的复制安装；
- smoke/readiness checks；
- 不包含 `.env`、缓存、测试输出、trash 或整个 skills 仓库的其他 Skill。

MIT 许可只覆盖 Grill Core Bundle 明确列出的自有文件，不自动改变整个 shared skills
仓库或第三方 gstack/Grill Me 的许可。Bundle 安装必须同时复制适用许可证。

### 4.2 可移植路径

- `grill-finalizer` alias 不再把 `/Users/will/code/skills/...` 绝对路径作为唯一解析方式。
- 优先按宿主可见 Skill 名解析 `docs-grill-finalizer`；文件型 fallback 使用 Bundle 内相对
  位置，不能依赖开发者用户名或源码仓库固定路径。
- `workflow-modes.md` 和 `provider-registry.md` 保持 owner-relative references。
- `00-gstack-tag-index.mdc` 是开发仓库内的角色索引 SSOT，但不是 Core 启动硬依赖；
  Core 保留内置稳定 lens 语义，索引可用时再刷新角色映射。
- gstack 本体继续由 `https://github.com/garrytan/gstack` 的官方 setup 安装，不被复制
  进 Grill Bundle。

### 4.3 安装器

新增确定性脚本，例如 `scripts/install_skill_bundle.py`：

- 输入：bundle id、source root、明确 `--dest`、可选 `--force`；
- 默认 dry-run/preview，展示将复制的文件、许可、目标和冲突；
- 未显式 `--dest` 不猜测宿主目录；
- 不覆盖真实目录或不同来源安装，除非用户对精确冲突再次确认；
- 只复制 manifest allowlist，拒绝 symlink escape、`..` 和 manifest 外文件；
- 安装后验证 alias、owner、references、metadata 和 license 都存在；
- 输出 machine-readable receipt，不含 token、环境秘密或无关绝对路径；
- 支持临时目录 smoke，测试不接触用户真实全局 Skill 环境。

对用户展示的真实安装命令只能在脚本、canonical source 和目标宿主路径都经过验证后
写入 MCP 工作流示例。未经验证时只展示来源并进入手工安装/兜底分支，不猜命令。

## 5. 范围与影响面

### 5.1 `/Users/will/code/skills`

计划修改或新增：

- `bundles/grill-finalizer/bundle.json`；
- `bundles/grill-finalizer/LICENSE`（MIT）；
- `scripts/install_skill_bundle.py`；
- 对应 installer/manifest tests 和临时目录 fixtures；
- `grill-finalizer/SKILL.md` 的可移植 owner 路由；
- `docs-grill-finalizer/SKILL.md` 与 references 的可选 gstack/Provider 边界；
- `README.md` 的 Bundle 安装、授权、升级、卸载和 smoke 说明；
- `skills_registry.json` 或其生成入口，确保 Bundle metadata 与公开帮助一致；
- `docs/spec/shared-skill-governance.md`：增加共享 Bundle 分发长期规则；
- `docs/snapshot/shared-skill-governance.json`：回写实际安装能力；
- `docs/decision-log/`：记录“核心 Bundle 自包含、第三方 Provider 独立安装”的长期决定。

不得修改或 vendor gstack 上游；不得把 Grill Me 的 `user_only` 约束改成自动调用。

### 5.2 `/Users/will/code/granoflow-mcp-server`

计划修改：

- `skills/granoflow-agent-workflow/references/external-skill-routing.md`：唯一状态机 owner；
- `skills/granoflow-agent-workflow/references/task-work-document-template.md`：等待状态枚举；
- `skills/granoflow-agent-workflow/references/task-work-document-workflow.md`：Grill 分支；
- `skills/granoflow-agent-workflow/SKILL.md`：高层摘要与成功标准；
- `README.md`：完整能力、安装建议和降级公开说明；
- `tests/task-workflow-contracts.test.ts`：正向、反向和授权契约；
- 三份已实施 73 的 dated design replacement note：
  - `73-final-external-skill-routing-and-model-fallback-v02.md`；
  - `73-final-granoflow-mcp-control-plane-analysis-plan-finalization-v02.md`；
  - `73-final-unified-adaptive-task-work-document-v02.md`。

历史 76/73 中仅记录当时实施事实的旧语义保留；仍可能被当成活动规则的文档必须加
superseded note。全仓搜索结果要逐项分类，不能批量替换历史文本。

## 6. 文件和职责预算

- 新 installer：目标不超过 300 行；manifest 解析、路径安全、复制和 receipt 分成真实
  职责函数，单函数目标不超过 50 行。
- installer tests：按 preview、install、conflict、unsafe path、missing dependency、
  receipt 和 smoke 分组，不把所有场景堆进一个测试。
- Bundle manifest：只描述一个 Bundle，不演变成通用包管理器 registry。
- MCP `external-skill-routing.md`：继续是单一状态机 owner；其他入口不复制完整流程。
- 不新增 MCP runtime class、service、API client 或安装器。
- 禁止为了行数门禁机械拆分；拆分必须对应 manifest、path safety、copy、verification 或
  receipt 等真实职责。

## 7. 分阶段实施

### 阶段 0：共享仓库基线和分发边界

1. 在两个 dirty worktree 中先记录用户已有改动，实施只触及计划列出的文件，不覆盖
   无关工作。
2. 为 Grill Core Bundle 写 manifest 和 scoped MIT license。
3. 修正 alias/owner 的绝对路径依赖，明确 gstack index 和第三方 providers 为可选增强。
4. 更新 shared skill governance spec/decision，冻结 Bundle 与第三方许可边界。

完成判定：从 Bundle manifest 能唯一推出文件集合、许可、入口、可选集成和 smoke。

### 阶段 1：确定性 Bundle 安装器

1. 实现 preview-first、显式 destination、allowlist copy 和冲突保护。
2. 增加路径逃逸、symlink、缺文件、不同来源冲突、重复安装和临时目录 smoke 测试。
3. 在临时目录安装 Core Bundle，验证 alias 可解析 owner，owner 可读取全部 required
   references，license 和 receipt 存在。
4. 更新 README 和 registry/generator；不得使用用户真实 `~/.codex/skills` 做自动测试。

完成判定：全新临时目录安装、发现、读取和重复执行均有可判定结果。

### 阶段 2：MCP 路由和等待状态

1. 删除 `grill-finalizer` “不暂停安装建议、立即 fallback”的特殊规则。
2. 接入 `install_offered + pending_user_decision`，写清恢复和去重。
3. 区分 Core、`user_only` Grill Me、model-allowed selected providers 和 fallback。
4. 更新 Task Work template/workflow、Agent Workflow 与 README；安装授权保持独立。

完成判定：唯一 owner 能回答未触发、可用、等待、同意、拒绝、安装失败、重发现失败、
调用失败和恢复会话的下一状态。

### 阶段 3：治理回写与契约测试

1. 给三份活动 73 增加 dated design replacement note，保留历史实施记录。
2. 增加契约测试：
   - Grill 未触发时不提示；
   - Core 可用时直接调用；
   - missing/unknown 时只展示一次精确安装建议；
   - waiting 状态跨恢复不重复提示、不假定拒绝；
   - approved 后必须 rediscover/smoke；
   - declined/install/discovery/invocation failure 后显式 fallback；
   - Grill Me `user_only` 不自动调用；
   - 缺少可选 provider 不降低 Core 完整性；
   - 安装授权不扩大；
   - MCP 不扫描或安装。
3. 对活动契约增加反向断言，禁止旧“立即 fallback 且不建议安装”和“fallback 等价完整
   finalizer”语义。

### 阶段 4：真实表面验收与收尾

1. 使用临时目标目录执行 Bundle preview/install/smoke，不污染全局环境。
2. 用能够读取打包 reference 的宿主 Agent 执行固定行为场景，并写入：
   `docs-temp/reviews/grill-finalizer-install-routing-scenarios.md`。
3. 记录每个场景的输入 fixture、预期 decision/result、实际输出、pass/fail 和证据路径。
4. 运行两个仓库的完整门禁，回写本计划实施记录。
5. 不 commit、push、publish 或安装到用户真实宿主，除非另有明确授权。

两个仓库共享契约顺序依赖明显：先完成 Core Bundle，再接 MCP 路由，最后统一验收。
不使用并行 worktree 实施，避免 MCP 文案先承诺尚不存在的安装单元。

## 8. 验收判定

| #   | 验收项         | 通过条件                                                | 证据                   |
| --- | -------------- | ------------------------------------------------------- | ---------------------- |
| A1  | Bundle 边界    | manifest 只包含 Core 自有文件和 scoped MIT license      | manifest + test        |
| A2  | 可移植性       | 安装后的 alias/owner 不依赖 `/Users/will` 绝对路径      | temp smoke             |
| A3  | 安装安全       | preview、显式 dest、allowlist、冲突和路径逃逸均有测试   | installer tests        |
| A4  | Core 完整      | alias、owner、两份 references、metadata、license 均可读 | receipt + smoke        |
| A5  | 第三方隔离     | gstack/Grill Me 不被复制或再许可                        | manifest audit         |
| A6  | Grill Me 权限  | `user_only` 只建议主动调用                              | MCP contract test      |
| A7  | 未触发不打扰   | Grill 未触发时不提示安装                                | contract test          |
| A8  | 缺失先建议     | fallback 前有一次精确安装选择                           | contract test          |
| A9  | 等待可恢复     | pending 状态不重复询问、不误装、不误降级                | contract test          |
| A10 | 安装后验证     | exit code 不足，必须 rediscover/reload/smoke            | contract test          |
| A11 | 拒绝/失败继续  | 各失败分支显式 `bundled_fallback`                       | contract test          |
| A12 | 能力表述诚实   | fallback 不宣称等价；可选 provider 不决定 Core 完整性   | README + negative test |
| A13 | 授权隔离       | 安装不授权写入、执行或高风险动作                        | contract test          |
| A14 | MCP 保持控制面 | MCP 无扫描、shell、下载或安装 runtime                   | diff audit             |
| A15 | 治理闭环       | 三份活动 73 和 shared governance 完成回写               | doc audit              |
| A16 | 宿主行为       | 固定场景 artifact 全部 pass                             | review artifact        |
| A17 | 双仓门禁       | 两个仓库适用的完整 checks 均退出 0                      | command output         |

## 9. 验证命令与行为场景

### 9.1 共享 skills 仓库

实施前先读取仓库现有规则和测试入口，优先使用其文档化命令。至少执行：

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m pyright
```

若仓库现有门禁入口与上述命令不同，以更严格的现有入口为准。另需在临时目录运行
installer preview/install/reinstall/conflict/unsafe-path/smoke 测试。

### 9.2 Granoflow MCP

```bash
npx vitest run tests/task-workflow-contracts.test.ts tests/workflow-resources.test.ts
npm run check
```

通过条件：Prettier、ESLint、Ruff、Ruff format、Pyright、build、Python tests 和全部
Vitest 均退出 0。

### 9.3 固定宿主场景

验收 artifact 必须覆盖：

1. Grill 未触发；
2. Core 已可用；
3. Core 缺失、安装元数据已验证；
4. 用户未回答并恢复会话；
5. 用户拒绝；
6. 用户同意但安装失败；
7. 安装成功但 rediscovery/smoke 失败；
8. Core 成功但 Grill Me 缺失或 user-only；
9. Core 成功但一个可选 gstack provider 缺失；
10. 同一任务重复进入路由。

任何场景不得真实安装到用户全局目录；使用 fixture 和临时 destination。

## 10. 风险、停止条件与回滚

### 10.1 主要风险

- scoped MIT license 若配置错误，可能误覆盖整个仓库或第三方文件；manifest 和许可路径
  必须共同限定适用文件。
- 通用 installer 容易演变成包管理器；本次只支持 manifest allowlist copy，不做依赖
  求解、在线 registry 或自动升级。
- 安装建议引入等待状态；若没有持久化恢复，用户会被重复追问或错误降级。
- gstack 官方安装方式可能变化；每次展示命令前必须验证 canonical source，MCP 不保存
  一份永久静态第三方命令。

### 10.2 停止条件

- 需要 MCP runtime 扫描或安装宿主 Skill；
- Bundle 无法在不复制第三方文件的情况下自包含 Core；
- scoped MIT license 无法明确限定自有文件；
- alias/owner 仍只能通过开发者绝对路径工作；
- installer 必须覆盖未知真实目录或访问秘密；
- waiting 状态无法与 Task Work 的恢复/去重契约兼容；
- 自动测试必须修改用户真实全局 Skill 环境。

命中任一条件时停止，记录 blocker；继续完成其他非阻塞步骤，但不得宣称 A1-A17 全部
完成。

### 10.3 回滚

1. MCP 回退安装建议和 waiting 枚举，恢复直接 `bundled_fallback`；
2. 删除活动入口对 Bundle 的公开承诺，保留通用外部 Skill 授权隔离；
3. shared skills 新文件移动到其仓库 `trash/`，不永久删除；
4. 恢复 alias/owner 先前解析方式，但保留不影响旧环境的安全修复；
5. 回退治理文档的 design replacement note；
6. 重新运行两个仓库门禁。

不涉及数据库、App、API 或发布版本回滚。

## 11. 72/74 与长期规则冲突结论

- 三份 MCP 已实施 73 的“缺失立即 fallback”被新用户意图替换。
  - 分类：`auto_resolved_as_design_change`。
  - 闭环：添加 dated replacement note，不删除历史实施事实。
- MCP 只做控制面、安装必须显式授权、外部 Skill 不能扩大权限、第三方能力不复制等旧
  规则继续有效。
  - 分类：`auto_resolved_as_old_rule_still_valid`。
- shared skill governance 目前没有 Bundle 分发约定，需要更新 72 spec、71 snapshot 并
  新增/更新 74 decision log，避免 installer 规则只存在于临时 73。
- Grill Me 的 `disable-model-invocation: true` 继续有效，不因安装体验目标而覆盖。

## 12. 不在范围内

- 修改或 vendor gstack 上游；
- 把 Grill Me 改成 model-invocable；
- 建立在线 Skill 商店、registry 服务或自动更新后台；
- 为所有宿主硬编码默认目录；
- Granoflow App UI、数据库、Local HTTP API 或 MCP runtime 安装工具；
- commit、push、GitHub Release、npm publish 或真实用户环境安装。

## 13. 收尾与实施授权

- 实施完成后回写本计划状态、实际文件、计划差异、门禁结果和验收 artifact。
- shared skills 回写：72 spec、71 snapshot、74 decision log、README/registry。
- Granoflow MCP 回写：三份活动 73、README、Agent Workflow 和唯一 routing owner。
- 不创建第二份动态 gstack/Grill Me 全量清单。
- 不把本计划的确认解释为实施授权。

用户后续明确说“实施这个 73”时，授权执行本文两个本地仓库内的全部阶段、测试、治理
回写和临时目录 smoke；不授权 commit、push、publish、远程仓库创建、真实全局 Skill
安装或其他未列明外部副作用。

## 14. Grill Finalizer 审计

- Review depth：`focused`。
- 采用的核心决定：Grill Core Bundle 使用 scoped MIT；Grill Me 保持 user-only；gstack
  独立安装；增加 waiting 状态；三份活动 73 回写；行为验收产物固定路径。
- 问题空间扩展：从“修改 MCP 提示”扩展到“先建立真实可安装单元”，因为后者决定用户
  是否能得到承诺结果。
- 迁移测试：全新电脑没有 `/Users/will/code/skills` 时，Bundle 仍必须可安装和解析。
- 审计结果：所有已确认决定已进入范围、步骤、验收、风险和回写；无待定许可证、TBD
  或未分类旧规则。

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
