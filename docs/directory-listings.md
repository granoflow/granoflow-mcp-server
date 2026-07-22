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

Connect MCP-capable AI agents to Granoflow workflows for local tasks,
task analysis, requirement capture, reviews, review cards, first-run import, and
long-term work memory.

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

Granoflow MCP can support any agent-assisted work, and it is especially useful
for software projects. For people who are not programmers or have not used AI
coding agents before, it makes AI work less of a black box: users can read,
understand, and learn from the experience AI leaves behind, while future agents
can search those records tomorrow, next month, or next year instead of starting
with a fresh plan every time and fragmenting the project into disconnected
attempts.

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

### Initialize Granoflow

After installing Granoflow MCP, ask your agent:

```text
Initialize Granoflow
```

Granoflow checks the connection and offers all recommended AI capability
collections using only their names and plain-language functions. Data import
from Cursor, Codex, Hermes, or other agents remains available afterward.

Directory summary:

```text
First-run setup: after installing Granoflow MCP, ask your agent "Initialize Granoflow". Granoflow checks the connection, offers all recommended AI capability collections, and can then import data from Cursor, Codex, Hermes, or other agents.
```

### Define / Initialize This Project

After Granoflow MCP is connected, ask your agent to define a software project
(distinct from `Initialize Granoflow`):

```text
Initialize this project
```

or:

```text
定义这个项目
```

Project Definition completes Project Work from product sources, locks stack
capability and skill routing, delivers Design Baseline with Design Tokens and
landscape/portrait App Shell, then hands off to
`granoflow-portfolio-orchestrator` (create all milestones, then quality-author
tasks one-by-one).

Directory summary:

```text
Project definition: after Granoflow MCP is ready, ask "Initialize this project" or "定义这个项目" (not "Initialize Granoflow"). Granoflow fills Project Work, locks design routing and stack capability, delivers Design Baseline with tokens and App Shell, then hands off to portfolio orchestration for milestones and tasks.
```

### Plan Project Milestones And Tasks

After Project Definition Done, ask your agent to create the full milestone
portfolio and author tasks (not the same as coordinating execution):

```text
Create all milestones and tasks for this project
```

Directory summary:

```text
Portfolio orchestration: after Project Definition, ask to create all milestones and tasks. Granoflow batch-creates milestones, then quality-authors each task one-by-one (skeleton coverage first), until Portfolio Ready.
```

### Run Integration Test Campaign

When you want AI-driven integration testing until green (not task-local
write-only tests). Works in interactive and unattended project modes:

```text
Run integration test campaign
开始集成测试战役
```

Directory summary:

```text
Integration test campaign: orchestrate a minimal human-path suite, AI auto-drives, triage code vs test failures, fix and re-test until green; optional vision; change report when edits land.
```

### Process Due Tasks

After installing Granoflow MCP, ask your agent:

```text
Process today's tasks
```

Granoflow will analyze and process the matching tasks in Granoflow.

Directory summary:

```text
Due-task workflow: after installing Granoflow MCP, ask your agent "Process today's tasks". Granoflow will analyze and process the matching tasks in Granoflow.
```

### Ask For Approval During A Task

During a task, Granoflow can ask for your approval or missing information by
adding a request to the task and notifying you when available.

Directory summary:

```text
Ask-for-approval workflow: when an agent needs your approval or more information, Granoflow records the request in the task and notifies you when available.
```

### Create A Task From A Requirement

Ask your agent:

```text
Create a task from this requirement
```

Granoflow will capture the requirement as a task and place it in the right
project, milestone, or inbox.

Directory summary:

```text
Requirement-capture workflow: ask your agent "Create a task from this requirement". Granoflow will capture the requirement as a task and place it in the right project, milestone, or inbox.
```

### Analyze Or Start A Task

Ask your agent:

```text
Analyze the first task
```

Granoflow will prefill the selected task analysis, show unresolved decisions
with AI recommendations, and write a grilled analysis only after your
confirmation. Planning remains a separate confirmed step.

Directory summary:

```text
Task-analysis workflow: ask your agent "Analyze the first task". Granoflow will prefill the analysis, show unresolved decisions with AI recommendations, and create a grilled final analysis before any separate planning step. A confirmed planning-ready analysis can then produce a versioned Plan attachment and deliverable task nodes; manual acceptance can happen later on any synced Granoflow device without blocking other safe execution.
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
- Analyze or start a selected task with planning and user confirmation.
- List, create, update, resolve, and delete projects and milestones.
- Show daily, weekly, and monthly review context.
- Expose a bundled `granoflow_agent_workflow_skill` so agents know when to use
  task reviews, review cards, long-term memory, and fallback card fields.
- Expose a bundled `granoflow_first_run_import_skill` for initializing
  Granoflow and importing data from Cursor, Codex, Hermes, or other agents.
- Record verified Task Delivery, complete through one owner, and review tasks later without blocking completion.
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
Granoflow connects MCP-capable AI agents to local workflows for tasks, approval requests, reviews, review cards, first-run import, due-task processing, requirement capture, task analysis, and long-term work memory. It supports many agent-assisted work scenarios and is especially useful for software projects: users can inspect and learn from AI's recorded experience, while future agents can search that experience tomorrow, next month, or next year instead of inventing a fresh plan every session and fragmenting the project into disconnected attempts. After installing, ask your agent "Initialize Granoflow" to check the connection, install recommended AI capabilities, and optionally import agent data; ask "Process today's tasks" to analyze and process matching Granoflow tasks, "Create a task from this requirement" to capture a discussed requirement as a Granoflow task, or "Analyze the first task" to confirm and grill a task analysis before planning.
```

### Glama

```text
Granoflow MCP connects AI agents to a local-first workflow layer for tasks, task analysis, requirement capture, approval requests, due-task processing, reviews, durable lesson cards, long-term work memory, and first-run import from Cursor, Codex, Hermes, or other agents. Especially useful for software projects: AI experience becomes readable, learnable, and searchable by future agents.
```

### mcp.so

```text
Granoflow helps MCP-capable agents keep work outside chat history: task state, task analysis, requirement capture, approval requests, due-task processing, completion reviews, durable review cards, first-run data import, and local work-memory context. For AI coding agents, it turns one-off chat output into experience future agents can reuse.
```

### mcpservers.org

```text
Local-first productivity MCP server for Granoflow. It helps agents manage task workflows, task analysis, requirement capture, approval requests, due-task processing, reviews, review cards, first-run import, and long-term work memory. Especially useful for software projects where future agents should continue from past experience, not start over and fragment the project.
```

### Awesome MCP Servers

```text
- [Granoflow](https://github.com/granoflow/granoflow-mcp-server) - Local-first task, task analysis, requirement capture, approval request, due-task processing, review, first-run import, review-card, and work-memory workflows for MCP-capable agents; especially useful for software projects where future agents should continue from past experience instead of fragmenting the project.
```

### Smithery / MCPB

```text
Connect AI agents to Granoflow for local task workflows, task analysis, requirement capture, approval requests, due-task processing, first-run data import, reviews, review cards, and work-memory context. AI experience becomes readable, learnable, and reusable by future agents.
```

## Directory Publication Status

Verified on 2026-07-19 after publishing `@granoflow/mcp-server@0.1.16`:

| Surface               | Prepared in repo | Publication status        | Notes                                                                                                |
| --------------------- | ---------------- | ------------------------- | ---------------------------------------------------------------------------------------------------- |
| GitHub README         | yes              | published                 | Release commit `787c2cf` is present on `main` and `develop`.                                         |
| npm package page      | yes              | published                 | npm `latest` and package version both resolve to `0.1.17`.                                           |
| Official MCP Registry | yes              | published                 | `com.granoflow/mcp-server@0.1.17` is expected to be current; manual confirmation pending.            |
| Glama                 | yes              | listed_auto_sync          | Listing resolves to the canonical GitHub repository; derived copy and schemas may lag.               |
| mcp.so                | yes              | listed_auto_sync          | Listing exposes the canonical repository, npm command, and local-first privacy positioning.          |
| mcpservers.org        | yes              | listed_auto_sync          | Listing resolves to the canonical repository and exposes the current npm install command.            |
| Awesome MCP Servers   | yes              | listed_via_mcpservers_org | The current Awesome MCP Servers site exposes the Granoflow repository listing.                       |
| Smithery / MCPB       | yes              | published_manual_only     | Published manually due platform approval latency; verification is deferred because review is manual. |

Third-party directory entries are discovery mirrors, not release truth. npm
and the Official MCP Registry are authoritative for the published version;
existing directory copy must still be checked for stale commands, repository
links, positioning, and privacy claims.
