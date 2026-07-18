# 73 最终计划：Local API 断连报告、非默认端口与一次性持久配置

Status: superseded by v02 after Grill Finalizer review

Date: 2026-07-15

## 用户目标

当 Granoflow 未启动、Local HTTP API 未开启或配置端口不可达时，宿主 Agent 必须
准确说明当前工作只停留在本地 Task Work Document 草稿，尚未写入 Granoflow、尚未
完成附件内容或 SHA-256 回读，也不能宣称存在正式 active Work Document。

Granoflow 使用非默认端口时，工作流应能诊断当前配置、发现受限候选端口或接受用户
明确提供的端口。用户确认采用某个端口后，将完整 `apiBaseUrl` 写入 MCP 自有的非秘密
配置文件；以后优先复用该配置，不再反复询问。恢复连接后必须重新读取任务、附件和
节点并检查冲突，再上传和回读正式版本。

## 当前事实与 SSOT

- 默认地址由 `src/config.ts` 的 `DEFAULT_API_BASE_URL` 定义为
  `http://127.0.0.1:56789`。
- MCP 自有配置文件已经存在：默认路径是
  `~/.config/granoflow-mcp/config.json`；`GRANOFLOW_MCP_CONFIG_PATH` 可改变路径。
- `apiBaseUrl` 已可由 `granoflow_setup_write_config` 预览并写入，文件权限为 `0600`，
  旧配置会备份。
- 当前解析优先级为 `GRANOFLOW_API_BASE_URL > config.apiBaseUrl > default`。
- `granoflow_setup_detect_local_api` 已能探测默认候选端口或调用者提供的最多 20 个端口，
  但不会扫描全部 1–65535 端口。
- `requestGranoflowApi` 已在本地连接失败时返回 `network_error`、当前地址、Granoflow
  产品说明和下一步。
- 当前 Skill 只强制说明“无法读写任务”，尚未拥有本地草稿状态、正式写入禁令、恢复
  重读和冲突处理的完整报告契约。

SSOT 分工：

| 责任                                 | SSOT                                                                      |
| ------------------------------------ | ------------------------------------------------------------------------- |
| 地址校验、配置路径、优先级、持久写入 | `src/config.ts`                                                           |
| 进程诊断、候选端口探测、配置引导     | `src/setup.ts`                                                            |
| 每次 API 请求的结构化网络错误        | `src/api.ts`                                                              |
| MCP 工具输入、描述和输出暴露         | `src/tools.ts`                                                            |
| 草稿、断连报告和恢复续传语义         | `skills/granoflow-agent-workflow/SKILL.md` 与 Task Work Document workflow |
| 用户安装和自定义端口说明             | `README.md`、`docs/user-install-demo.md`                                  |

## 适用性裁剪

### 数据库

无数据库表、字段、索引、migration、schemaVersion、回填或同步格式变化。依据是端口
配置属于 MCP 进程本地 JSON 配置，Task Work Document 草稿属于宿主工作区；本计划不
修改 Granoflow App 数据模型。

### UI

无 Granoflow App 页面、布局、组件或交互变化。所有提示通过 MCP 结构化结果与宿主
Agent 文本报告完成，因此不需要 UI 草图或组件复用确认。

### API 与兼容性

不新增 Granoflow Local HTTP API endpoint。MCP 工具保留现有名称；结构化输出只追加
字段，不删除或改名现有字段。配置优先级保持 `env > config > default`，避免破坏已有
部署。历史配置继续可读。

### 文件与方法预算

| 文件            | 单一职责                           | 预算                                           |
| --------------- | ---------------------------------- | ---------------------------------------------- |
| `src/config.ts` | 校验、解析并持久化 MCP 非秘密配置  | 净增不超过 70 行；新增/修改方法不超过 45 行    |
| `src/setup.ts`  | 诊断进程和端口，生成一次性配置动作 | 净增不超过 120 行；核心方法不超过 60 行        |
| `src/api.ts`    | 返回统一 API 请求和断连事实        | 净增不超过 50 行；网络错误构造方法不超过 45 行 |
| `src/tools.ts`  | 暴露 schema 与工具说明             | 净增不超过 45 行，不复制 setup/config 业务逻辑 |
| 每个测试文件    | 验证一个层级的公开契约             | 单个新增测试块尽量不超过 50 行                 |

若接近预算，按“配置解析”“连接诊断”“工作流报告”真实协议边界拆分；禁止按行号机械
切分或建立无明确职责的 helper。

## 冻结行为契约

### 1. 地址解析与只问一次

地址来源继续按以下顺序解析：

1. `GRANOFLOW_API_BASE_URL`；
2. `config.apiBaseUrl`；
3. `http://127.0.0.1:56789`。

当默认地址不可达时：

- 若 Granoflow 未运行，先报告并建议用户打开应用，不猜端口；
- 若 Granoflow 正在运行，调用受限候选探测；
- 只有一个高置信候选时，展示候选和证据，请用户确认是否持久化；
- 多个候选时不得自动选择；一次性列出候选，请用户选择；
- 没有候选时，只问一次用户是否使用自定义端口，并允许其给出端口或完整本地 URL；
- 用户明确提供端口 `P` 时规范化为 `http://127.0.0.1:P`；提供完整 URL 时按 URL 校验；
- 不进行全端口扫描，不探测非本地主机，不把 401/403 低置信候选自动写入配置。

用户确认后先调用 `granoflow_setup_write_config(dryRun=true)`，展示实际配置路径、旧值、
新值和 `changedKeys`；再以 `dryRun=false` 写入并调用 `granoflow_setup_status` 验证。成功
报告必须包含：配置路径、持久化地址、来源为 `config`、健康检查结果，以及长驻 MCP
进程是否需要重载。

只要该配置仍有效且没有更高优先级环境变量，就直接使用，不再询问端口。若
`GRANOFLOW_API_BASE_URL` 覆盖了已保存配置，必须明确报告
`configuration_shadowed_by_env`，说明配置文件没有生效；不得再次写同一个配置并假装
问题已解决。

### 2. 断连时的统一报告

本地 API 请求因连接拒绝、超时或不可达失败时，结构化结果至少提供：

```yaml
code: network_error
connection_state: unreachable
api_base_url: <resolved URL>
api_base_url_source: env | config | default
granoflow_write_state: not_written
attachment_readback_state: not_verified
active_work_document_state: not_established
config_path: <resolved non-secret config path>
next_actions:
  - diagnose_or_open_app
  - detect_or_confirm_port
  - reconnect_and_reconcile
```

宿主 Agent 根据实际本地草稿补充而不是虚构：

```text
Granoflow 当前不可连接。
Task Work Document 已生成本地草稿：<safe local path>。
该草稿尚未写入 Granoflow，未完成附件内容或 SHA-256 回读，
也不是正式 active Work Document。
请打开 Granoflow并启用 Local HTTP API，或确认当前端口；恢复后我会重新读取任务状态再继续。
```

若本地草稿尚未创建，必须改为“尚未生成本地草稿”，不得输出伪路径。不得在错误结果、
配置或报告中暴露 token、OTP、密码、恢复码或 auth URL。

### 3. 本地草稿状态

Task Work Document workflow 增加明确的草稿状态词汇：

- `local_draft`: 文件存在于宿主可访问的安全工作区，但未上传；
- `upload_blocked_api_unreachable`: 因 API 不可达而无法上传；
- `attachment_readback_pending`: 尚无 App-owned 内容/SHA-256 证据；
- `active_not_established`: 不得写入或宣称 active pointer；
- `reconciliation_required`: 恢复后必须重读远端状态。

MCP server 不接管宿主文件系统，也不保存草稿正文。宿主必须提供真实安全路径后才能
报告 `local_draft`。Task description 无法写入时，状态只存在于本地工作副本和当前宿主
会话，不得声称已经持久化到 Granoflow。

### 4. 恢复与冲突处理

连接恢复后必须执行：

1. 重新解析运行时地址并验证 health；
2. 重新读取目标任务、附件、节点和任务 revision；
3. 检查是否已有新的 active Work Document、同版本附件、任务状态变化或节点变化；
4. 将本地草稿与最新任务事实重新协调；
5. 若 Outcome、Scope、Risk、Decision、授权或 Planning 判断发生实质变化，撤销旧确认并
   回到对应确认阶段；
6. 若事实未变化，允许复用仍有效的内容确认，但上传动作仍需当前 task revision；
7. 生成下一个未占用的不可变 `task-work-vNN.md`，上传并回读内容或 SHA-256；
8. 只有 readback 成功后才更新 active pointer 和正式成功报告。

存在多个 active 候选、同版本不同 hash、任务已完成/删除、revision 冲突或授权已失效时
fail closed，返回明确冲突，不自动覆盖、不删除历史附件。

## 实施步骤

### 阶段一：用测试冻结报告和配置契约

1. 在 `tests/api.test.ts` 增加本地断连结构化字段、配置来源和无秘密输出测试。
2. 在 `tests/config.test.ts` 增加自定义端口持久化、重读、`env > config > default`、非法
   端口/URL和配置保留测试。
3. 在 `tests/setup.test.ts` 增加单候选、多候选、无候选、用户提供端口、配置被环境变量
   覆盖及写后 health 验证测试。
4. 在 `tests/task-workflow-contracts.test.ts` 增加本地草稿报告、禁止 active 声明和恢复
   reconciliation 流程测试。

### 阶段二：统一配置与连接诊断结果

1. 在 `src/config.ts` 提供规范化且严格校验的本地 `apiBaseUrl`/端口输入，保留完整 URL
   高级路径；拒绝缺失端口、越界端口、非 HTTP(S) 和不允许的自动远端探测。
2. 让配置写入结果明确返回最终解析来源；写后重新读取，证明值真实持久化。
3. 在 `src/setup.ts` 生成可判定的候选状态：`none | single_high_confidence |
multiple | auth_required_only`，并输出是否适合请求持久化确认。
4. 检测配置与环境变量冲突，返回 `configuration_shadowed_by_env` 和可执行修复说明。
5. 保持用户确认前 `dryRun=true`；只有明确确认才落盘。

### 阶段三：实现断连和恢复报告契约

1. 抽取 `src/api.ts` 的本地网络错误构造边界，追加 connection/write/readback/active/config
   字段，同时保留现有 `network_error`、产品说明和 next actions。
2. 更新 `src/tools.ts` 的 setup 工具描述与 schema，使宿主知道候选端口不会自动落盘，
   自定义端口确认后可持久化一次。
3. 更新主 Agent Workflow 的 `Connection First`：先判断是否存在真实本地草稿，再按固定
   状态报告，禁止宣称 Granoflow 写入成功。
4. 更新 Task Work Document workflow：加入断连状态、恢复重读、确认失效条件、版本选择、
   upload/readback/active pointer 顺序。
5. 保持 `local_reference` 与历史 `attachment_api_unavailable` 可读；新断连状态用于更精确
   表达，不迁移历史附件。

### 阶段四：文档与真实使用说明

1. 更新 README：说明默认配置路径、一次性写入流程、优先级、非默认端口和重载要求。
2. 更新 `docs/user-install-demo.md`：分别给出默认端口、自动候选、自定义端口和环境变量
   覆盖配置文件的排查示例。
3. 示例只使用本地无秘密 URL，不写真实 token，不鼓励全端口扫描。

### 阶段五：验收与回写

1. 运行聚焦的 config/setup/api/workflow 测试。
2. 运行 `npm run check`。
3. 用临时 `GRANOFLOW_MCP_CONFIG_PATH` 做 package-level smoke：预览写入、确认写入、重启式
   重读、自定义端口解析、环境变量覆盖报告；不得修改用户真实配置。
4. 搜索并消除“断连后已写入/已 active”的错误文案，以及把候选端口自动持久化的路径。
5. 将本计划状态回写为 `implemented`，记录实际文件、测试数量和未执行的真实端口场景。

## 验收判定

| 场景                     | 必须结果                                                          |
| ------------------------ | ----------------------------------------------------------------- |
| 默认端口可达             | 继续使用默认值，不询问、不写配置                                  |
| App 未运行               | 报告 App 未运行并建议打开，不猜测端口                             |
| App 运行、配置端口不可达 | 报告当前 URL/来源并执行受限候选探测                               |
| 单个高置信候选           | 请求一次持久化确认，不自动写入                                    |
| 多个候选                 | 一次列出并请求选择，不擅自选择                                    |
| 用户提供合法自定义端口   | 预览、确认、写入 config、重读并 health 验证                       |
| 配置后再次运行           | 来源为 `config` 且不再询问端口                                    |
| 环境变量覆盖配置         | 返回 `configuration_shadowed_by_env`，不谎称 config 生效          |
| API 断连且有真实草稿     | 报告路径、`not_written`、`not_verified`、`active_not_established` |
| API 断连且无草稿         | 明确“尚未生成草稿”，不虚构路径                                    |
| 恢复连接                 | 先重读任务/附件/节点/revision，再决定确认是否仍有效               |
| 上传成功                 | App-owned 内容或 SHA-256 回读后才建立 active pointer              |
| 安全                     | 所有输出、配置、测试 fixture 均不暴露秘密                         |
| 全量门禁                 | `npm run check` 全绿                                              |

## 失败、停止与回滚

### 停止条件

- 需要修改 Granoflow App schema、数据库或新增 Local HTTP API endpoint；
- 只能通过无界端口扫描找到自定义端口；
- 必须把 token 写进 MCP 配置文件才能连接；
- 无法区分环境变量覆盖与配置文件生效；
- 无法在 readback 前阻止 active Work Document 成功声明；
- 恢复流程必须覆盖或删除历史附件才能继续。

命中时停止实施并回到 Analysis，不以自动选择端口、扩大网络扫描或降低 readback 门禁
作为临时方案。

### 回滚

1. 移除新增的结构化断连字段和 Skill 状态词汇，恢复现有 `network_error` 输出；
2. 保留现有配置文件格式、`apiBaseUrl` 和解析优先级，不删除用户配置；
3. 恢复 setup 候选输出，但不删除安全校验和秘密保护；
4. 保留历史 Task Work Document 和附件，不修改 Granoflow 数据；
5. 重新运行 `npm run check`，并在计划中记录回滚原因。

## 不在本计划授权范围

- 修改 Granoflow App UI、数据库、Local HTTP API endpoint 或默认端口；
- 自动打开应用、自动写配置或修改 MCP 客户端环境变量而不经用户确认；
- 扫描全部端口、探测非本地主机或保存 API token；
- commit、push、publish 或 release。

用户后续说“实施这个 73”，授权完成上述代码、Skill、文档、测试、smoke 和计划回写，
但不授权本节列出的动作。

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
