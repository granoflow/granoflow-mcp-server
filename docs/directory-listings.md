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

Connect MCP-capable AI agents to a local task, review, review cards, and
long-term work memory layer in Granoflow.

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
