# AGENTS

## Project Role

This repository is the public Granoflow MCP server. It exposes Granoflow's
local REST API to AI agents by delegating core operations to `granoflow-cli`.

## Hard Rules

- Keep the MCP server thin. Do not reimplement Granoflow business logic here.
- Prefer `granoflow-cli` for task, project, review, backup, sync, and AI-agent
  operations.
- Do not print API tokens or secrets in logs, tool results, test snapshots, or
  documentation.
- Keep tool results structured and predictable for Cursor, Codex, Claude Code,
  and OpenCode/OpenClaw-compatible MCP clients.
- Do not add direct SQLite, Drift, app build, app run, screenshot, or release
  orchestration logic.

## Quality Gate

Run before handoff after code changes:

```text
npm run check
```

The gate includes Prettier, ESLint, TypeScript, and Vitest.
