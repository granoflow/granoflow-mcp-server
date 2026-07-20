---
name: granoflow-release-all-platforms
description: Use when releasing Granoflow MCP to npm and validating cross-platform MCP directory surfaces.
---

# Granoflow MCP 全平台发布技能

用于维护者的一次性发布流程，目标是：

1. 从 `develop` 合并到 `main`，
2. 提交并推送 `main`，
3. 回到 `develop`，
4. 运行 npm 发布，
5. 输出其他平台发布核对清单。

## 前置条件

- 当前分支建议为 `develop`，且工作区保持干净。
- `.env` 已存在，且至少包含 `NPM_TOKEN`。
- `package.json` 版本已按发布策略递增。

## 常用命令

- `npm run release:platforms`
  - 标准发布：合并 `develop -> main`，执行 `release:preflight`，发布 npm，推送 `main`，再回到原分支。
- `npm run release:platforms -- --dry-run`
  - 只做流程预演，不触发推送和发布。
- `npm run release:platforms -- --skip-publish`
  - 只执行分支合并与推送，不做 npm publish。
- `npm run release:platforms -- --skip-push`
  - 合并后不推送，便于本地核对。
- `npm run release:platforms -- --open-platforms`
  - 预发布后打开主要平台页面以便手工核对。

## `.env` 规范

应在仓库根目录创建 `.env`，并只提交到本地工作区（不入库）：

- `NPM_TOKEN`
- `NPM_PACKAGE_NAME`
- `RELEASE_SOURCE_BRANCH`
- `RELEASE_TARGET_BRANCH`
- `RELEASE_REMOTE`
- `NPM_OTP`（如需每次手工填入时可留空后重放）

## 发布范围

该技能只实现：

- npm 发布主线
- 其余 MCP 平台发布入口提示与核对

除非有对应平台账号脚本，否则其余平台（如 Glama、mcp.so、mcpservers.org、官方 MCP Registry、Awesome MCP Servers / Smithery）仍需在各自界面手动提交与确认。
