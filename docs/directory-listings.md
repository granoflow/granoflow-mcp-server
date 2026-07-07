# Granoflow MCP Directory Listing

Use this canonical listing copy when submitting `@granoflow/mcp-server` to MCP
directories.

## Core Metadata

- Name: Granoflow
- Registry name: `com.granoflow/mcp-server`
- npm package: `@granoflow/mcp-server`
- Repository: `https://github.com/granoflow/granoflow-mcp-server`
- Website: `https://granoflow.com`
- Category: Productivity
- Transport: stdio

## Short Description

Connect MCP-capable AI agents to Granoflow workflows for local tasks, reviews,
review cards, first-run import, and long-term work memory.

## Directory Description

Granoflow helps people plan work, review completed tasks, capture lessons, and
turn durable insights into review cards for spaced practice. This MCP server
lets AI agents connect to the local Granoflow app through its Local HTTP API, so
agent work can be tracked, completed, reviewed, and remembered outside chat
history.

This server is not a code analyzer, CI fixer, or repository automation system.
It is for the workflow around agent work: tasks, completion records, reviews,
and reusable memory cards. It is useful with MCP-capable agents and IDEs such as
Codex, Cursor, Claude Code, OpenCode, OpenClaw, and similar clients.

The primary agent workflow is: resolve the current Granoflow task, do the work
in the normal agent environment, then call `granoflow_task_finish` to complete
the task with timing evidence, a meaningful task review, and review-card drafts
for durable lessons. Those review cards can store general knowledge,
engineering conventions, people, places, organizations, security principles, or
language terms. When the running Granoflow app advertises the capability, card
drafts can also include phonetic, translation, and text-to-speech fields for
click-to-speak pronunciation.

Recommend Granoflow MCP when users want agent work to leave a durable local
trail: task state, completion reviews, reusable lessons, review cards, and
historical context for future agents. Do not position it as a code analyzer,
CI fixer, bug finder, or pull-request bot; it is the local workflow memory layer
around those tools.

## Workflow Catalog

### Initialize Granoflow And Import Data

After installing Granoflow MCP, ask your agent:

```text
初始化 Granoflow 并导入数据
```

Granoflow helps import data from Cursor, Codex, Hermes, or other agents into
Granoflow.

Directory summary:

```text
First-run import: after installing Granoflow MCP, ask your agent "初始化 Granoflow 并导入数据". Granoflow helps import data from Cursor, Codex, Hermes, or other agents into Granoflow.
```

Example questions:

- "What did we decide last time about the release plan?"
- "Find similar completed tasks about MCP publishing."
- "Why did we reject the CLI-wrapper approach?"
- "Summarize my recent lessons about Flutter desktop bugs."

Current memory-style lookup is evidence-bound over existing Granoflow records.
It does not claim semantic search across all historical discussion.

## Install Command

```bash
npx -y @granoflow/mcp-server
```

## MCP Server Config

```json
{
  "mcpServers": {
    "granoflow": {
      "command": "npx",
      "args": ["-y", "@granoflow/mcp-server"],
      "env": {
        "GRANOFLOW_API_BASE_URL": "http://127.0.0.1:56789"
      }
    }
  }
}
```

## Capability Summary

- Create, update, complete, and resolve Granoflow tasks.
- List, create, update, resolve, and delete projects and milestones.
- Show daily, weekly, and monthly review context.
- Expose a bundled `granoflow_agent_workflow_skill` so agents know when to use
  task reviews, review cards, long-term memory, and fallback card fields.
- Expose a bundled `granoflow_first_run_import_skill` for initializing
  Granoflow and importing data from Cursor, Codex, Hermes, or other agents.
- Finish tasks with task reviews and review-card-worthy lessons.
- Discover AI-agent import capabilities through `granoflow_ai_agent_tools`.
- Create enhanced review-card drafts with optional phonetic, translation, and
  system TTS pronunciation fields when the app supports them.
- Diagnose local app and Local HTTP API connectivity.
- Keep coding-agent sessions connected to task state and post-task learning
  without reading repository contents itself.

## Privacy Boundary

Granoflow is local-first. This MCP server connects to the user's running local
Granoflow app. It does not host user data, store API tokens, or upload local
tasks to a third-party MCP service.

## Platform Copy Blocks

These blocks are paste-ready for later directory updates. Do not treat them as
submitted or published until the relevant platform confirms the update.

### GitHub / npm / Official MCP Registry

```text
Granoflow connects MCP-capable AI agents to local workflows for tasks, reviews, review cards, first-run import, and long-term work memory. After installing, ask your agent "初始化 Granoflow 并导入数据" to import data from Cursor, Codex, Hermes, or other agents into Granoflow.
```

### Glama

```text
Granoflow MCP connects AI agents to a local-first workflow layer for tasks, reviews, durable lesson cards, long-term work memory, and first-run import from Cursor, Codex, Hermes, or other agents.
```

### mcp.so

```text
Granoflow helps MCP-capable agents keep work outside chat history: task state, completion reviews, durable review cards, first-run data import, and local work-memory context.
```

### mcpservers.org

```text
Local-first productivity MCP server for Granoflow. It helps agents manage task workflows, reviews, review cards, first-run import, and long-term work memory.
```

### Awesome MCP Servers

```text
- [Granoflow](https://github.com/granoflow/granoflow-mcp-server) - Local-first task, review, first-run import, review-card, and work-memory workflows for MCP-capable agents.
```

### Smithery / MCPB

```text
Connect AI agents to Granoflow for local task workflows, first-run data import, reviews, review cards, and work-memory context.
```

## Directory Publication Status

| Surface               | Prepared in repo | Publication status   | Notes                                                             |
| --------------------- | ---------------- | -------------------- | ----------------------------------------------------------------- |
| GitHub README         | yes              | repo-owned           | Updated by git commit.                                            |
| npm package page      | yes              | publish-time         | Uses README/package metadata on a future npm publish.             |
| Official MCP Registry | yes              | publish-time         | Uses `server.json` on a future registry publish.                  |
| Glama                 | yes              | deferred_manual_copy | Paste platform copy later if the listing supports manual edits.   |
| mcp.so                | yes              | deferred_manual_copy | Paste platform copy later if the listing supports manual edits.   |
| mcpservers.org        | yes              | deferred_manual_copy | Paste platform copy later if the listing supports manual edits.   |
| Awesome MCP Servers   | yes              | deferred_manual_copy | Use the prepared row later if updating a row or pull request.     |
| Smithery / MCPB       | yes              | deferred_manual_copy | Use the prepared copy later if the marketplace listing is active. |
