# Granoflow MCP User Install And Demo Guide

This guide helps you connect an MCP-capable AI agent or IDE to the Granoflow
desktop app through the Granoflow Local HTTP API. The examples below show Codex
and Cursor because they are the verified client targets for this repository;
other stdio MCP clients can use the same command shape.

Granoflow MCP does not make an AI agent better at reading repositories, fixing
CI, or writing code. It connects MCP-capable AI agents to a local task, review,
and long-term work memory layer: they can see planned work, update task state,
record verified Task Delivery, finish through one completion owner, and later
review lessons worth remembering.

Use it when you want agent work to leave a durable trail outside chat history.
Skip it if you only need code analysis or repository automation.

## 1. Start Granoflow

Open the installed Granoflow desktop app. On macOS the production app is usually:

```text
/Applications/granoflow.app
```

In Granoflow, open the local interface service page and turn on the Local HTTP
API. The default local address is:

```text
http://127.0.0.1:56789
```

Verify the app is reachable:

```bash
curl -s http://127.0.0.1:56789/v1/health
```

A healthy response includes `status`, `apiEnabled`, `running`, and `version`.

## 2. Check The MCP Package

Verify the npm package can run:

```bash
npx -y @granoflow/mcp-server --version
```

The command should print the package version.

## 3. Configure Codex

Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.granoflow]
type = "stdio"
command = "npx"
args = ["-y", "@granoflow/mcp-server"]

[mcp_servers.granoflow.env]
GRANOFLOW_API_BASE_URL = "http://127.0.0.1:56789"
```

Restart Codex or reload MCP servers after changing the file.

## 4. Configure Cursor

Add this to `~/.cursor/mcp.json`:

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

Restart Cursor or reload MCP servers after changing the file.

## 5. First Demo

Ask your MCP client to call:

- `granoflow_health`
- `granoflow_version`
- `granoflow_task_list`

Expected result:

- health returns `code: "ok"`
- version returns Granoflow app version metadata
- task list returns your current Granoflow tasks

## 6. First-Run Import Workflow

After the basic connection works, ask your agent:

```text
Initialize Granoflow and import data
```

Granoflow will help import data from Cursor, Codex, Hermes, or other agents into
Granoflow.

## 7. Due Task Workflow

Ask your agent:

```text
Process today's tasks
```

Granoflow will analyze and process the matching tasks in Granoflow.

## 8. Approval Request Workflow

During a task, Granoflow can ask for your approval or missing information by
adding a request to the task and notifying you when available.

## 9. Requirement Capture Workflow

Ask your agent:

```text
Create a task from this requirement
```

Granoflow will capture the requirement as a task and place it in the right
project, milestone, or inbox.

## 10. Task Analysis Workflow

Ask your agent:

```text
Analyze the first task
```

After the analysis is confirmed and planning-ready, the agent creates a grilled,
versioned Plan attachment and concrete task nodes. Each node has a deliverable
standard; manual acceptance can be completed later from any synced Granoflow
device without blocking the agent's remaining safe work.

Granoflow will prefill the selected task analysis, show unresolved decisions
with AI recommendations, and write a grilled analysis only after your
confirmation. Planning remains a separate confirmed step.

## 11. Dry-Run Write Demo

Use a dry-run before any write. For example, ask the MCP client to call
`granoflow_task_create_structured` with:

```json
{
  "title": "MCP dry-run test",
  "description": "This request should preview only.",
  "dryRun": true
}
```

Expected result:

```json
{
  "code": "dry_run"
}
```

The dry-run preview should not create a real task.

## 12. Memory-Style Demo

After the basic connection works, try asking your MCP client:

```text
Search Granoflow for past lessons about release planning.
```

Other useful prompts:

- "Find similar completed tasks about MCP publishing."
- "What historical evidence do we have about this project?"
- "Why did we reject the CLI-wrapper approach?"

The quality of this demo depends on the data already in your local Granoflow
app. Agents can use existing tasks, task reviews, review cards, projects,
milestones, and periodic reviews as evidence, but this phase does not provide
semantic search across all historical discussion.

## 13. Agent Delivery And Deferred Review Demo

Use this demo after you have at least one real or test task in Granoflow. Ask
your MCP client:

```text
Resolve my Granoflow task named "MCP dry-run test", write and verify its Task
Delivery, then complete it through the correct single completion owner. Use
dry-run first.
```

The agent should inspect nodes first. Node-backed tasks finish through
NodeService; only node-less compatibility tasks use `granoflow_task_finish`.
The Task Delivery attachment must pass content or App-owned hash readback.

For real work, the expected agent behavior is:

- record actual deliverables, verification, Analysis/Plan differences,
  residuals, acceptance state, and handoff in Task Delivery;
- use exactly one completion owner and read back `status=done`;
- leave Review pending by default;
- when the user separately requests Review, confirm the review body and any
  card operations before writing them.

When a review card benefits from pronunciation, phonetic spelling, or
translation, ask:

```text
Create the review card with phonetic spelling and click-to-speak pronunciation
if the running Granoflow app supports that card-field capability. Otherwise put
the pronunciation and translation hints directly in the card front/back.
```

The agent should call `granoflow_ai_agent_tools` before sending structured
`noteFields`. If `review_card_draft_note_fields_v1` is advertised, it can send
`noteFields`, `frontLayout`, and `backLayout`. If not, it should fall back to
plain `front` and `back` content and still create a useful card.

## Troubleshooting

### The health check cannot connect

Check that Granoflow is open and that the Local HTTP API is enabled in the app.
If you changed the port in Granoflow, update `GRANOFLOW_API_BASE_URL` in your MCP
client config.

### The MCP client does not show Granoflow tools

Restart Codex or Cursor after editing the MCP config. Also verify:

```bash
npx -y @granoflow/mcp-server --version
```

### The MCP client connects to the wrong app

Call `granoflow_setup_status`. On macOS, the process evidence should point to
the production app when that is what you intended:

```text
/Applications/granoflow.app/Contents/MacOS/granoflow
```

### You enabled an API token

Keep the token in the MCP client environment. Do not paste real tokens into
docs, screenshots, issue reports, or chat transcripts.
