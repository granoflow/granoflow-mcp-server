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

Connect AI agents to Granoflow for tasks, reviews, and spaced-review memory
cards.

## Directory Description

Granoflow helps people plan and review work tasks, capture lessons from
completed work, and turn durable insights into review cards for spaced practice.
This MCP server lets AI agents connect to the local Granoflow app through its
Local HTTP API.

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

## Privacy Boundary

Granoflow is local-first. This MCP server connects to the user's running local
Granoflow app. It does not host user data, store API tokens, or upload local
tasks to a third-party MCP service.
