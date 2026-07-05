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

Connect MCP-capable AI agents to a local task, review, and long-term work
memory layer in Granoflow.

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
- Draft review-card-worthy lessons from completed work.
- Diagnose local app and Local HTTP API connectivity.
- Keep coding-agent sessions connected to task state and post-task learning
  without reading repository contents itself.

## Privacy Boundary

Granoflow is local-first. This MCP server connects to the user's running local
Granoflow app. It does not host user data, store API tokens, or upload local
tasks to a third-party MCP service.
