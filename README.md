# Granoflow MCP Server

Granoflow is a local-first app for planning work, reviewing completed tasks, and
turning durable lessons into review cards. Granoflow MCP connects MCP-capable AI
agents to a local task, review, and long-term work memory layer.

Granoflow's local features are free to use forever. If privacy is your concern,
do not subscribe: without membership, your data never leaves your device or gets
uploaded to the cloud.

Learn more at [granoflow.com](https://granoflow.com).

MCP server for Granoflow: exposes the Granoflow Local HTTP API as tools for AI
agents and IDEs that need to track task work, finish tasks with meaningful
reviews, and preserve reusable lessons as memory cards.

This is not a code analyzer, CI fixer, or repository automation framework. If
your only goal is to make an AI coding agent write better code, use tests,
linters, CI, prompts, and code-analysis tools directly. Granoflow MCP is for the
surrounding agent workflow: what task the agent is doing, what happened, what
should be remembered, and what deserves review later.

This server is intentionally thin. It does not own Granoflow business logic,
database access, app orchestration, or release workflows. It resolves a local API
endpoint, forwards structured requests to the running Granoflow app, and returns
predictable MCP tool results.

## Requirements

- Node.js 20 or newer.
- A running Granoflow app with the Local HTTP API enabled.

The default Granoflow API URL is:

```text
http://127.0.0.1:56789
```

You can override it with:

```bash
export GRANOFLOW_API_BASE_URL="http://127.0.0.1:56789"
export GRANOFLOW_API_TOKEN="..."
```

The MCP server can keep non-secret local connection defaults in:

```text
~/.config/granoflow-mcp/config.json
```

Set `GRANOFLOW_MCP_CONFIG_PATH` to use a different config path for tests,
temporary setups, or advanced local installs. API tokens are not stored in this
file; keep `GRANOFLOW_API_TOKEN` in the MCP client environment.

## Install

```bash
npm install -g @granoflow/mcp-server
```

For a user-facing setup walkthrough, see
[Granoflow MCP User Install And Demo Guide](docs/user-install-demo.md).

For maintainers, see
[Granoflow MCP Release Checklist](docs/release-checklist.md).

Agents can also reuse the bundled
[Granoflow Agent Workflow skill](skills/granoflow-agent-workflow/SKILL.md) for
task completion, daily review drafting, mood and efficiency note suggestions,
review-card drafting, long-term work memory retrieval, and user-feedback
handling conventions.

## Long-Term Work Memory

Granoflow MCP starts with tasks and reviews, but its workflow value is broader
than task CRUD. It helps agents use existing Granoflow records as local work
memory: task reviews, review cards, projects, milestones, and daily, weekly, or
monthly review context.

Try prompts such as:

- "What did we decide last time about the release plan?"
- "Find similar completed tasks about MCP publishing."
- "Why did we reject the CLI-wrapper approach?"
- "Summarize my recent lessons about Flutter desktop bugs."

Current memory-style lookup is evidence-bound and depends on what is already in
Granoflow. It does not imply semantic search across all historical discussion.
Dedicated memory search tools can come later when the Granoflow app and Local
HTTP API expose real memory search.

Good fit:

- You already use MCP-capable AI agents or IDEs such as Codex, Cursor, Claude
  Code, OpenCode, or OpenClaw for real work and want those sessions tied to
  tasks, completion records, lessons, and historical work context.
- You want task completion to capture useful review notes and one memory card
  per durable knowledge point instead of leaving everything in chat history.
- You prefer a local-first workflow where the MCP server talks to your running
  Granoflow app rather than uploading tasks to a hosted MCP service.

Poor fit:

- You want an MCP server that reads repositories, finds bugs, fixes CI, or opens
  pull requests by itself.
- You do not want to install or run the Granoflow desktop app.
- You only need a generic todo list with no review or memory-card workflow.

## Release Branch Policy

- `develop` is the active integration branch. It may contain unverified or
  unreleased changes.
- `main` is the npm release branch. Publish `@granoflow/mcp-server` latest only
  from `main`.
- Merge or fast-forward `develop` into `main` only after release preflight passes.

For local development:

```bash
npm install
npm run build
node dist/index.js
```

Verify an installed package without starting an MCP stdio session:

```bash
npx -y @granoflow/mcp-server --version
npx -y @granoflow/mcp-server --help
```

Before publishing a release, verify the package contents:

```bash
npm run release:preflight
```

## Tools

Initial tools:

- `granoflow_setup_status`
- `granoflow_setup_detect_local_api`
- `granoflow_setup_write_config`
- `granoflow_setup_open_config`
- `granoflow_setup_open_app`
- `granoflow_health`
- `granoflow_version`
- `granoflow_capabilities`
- `granoflow_ai_agent_tools`
- `granoflow_task_list`
- `granoflow_task_export`
- `granoflow_task_validate`
- `granoflow_task_import`
- `granoflow_task_create`
- `granoflow_task_create_structured`
- `granoflow_task_update`
- `granoflow_task_update_structured`
- `granoflow_task_complete`
- `granoflow_task_finish`
- `granoflow_task_resolve`
- `granoflow_project_list`
- `granoflow_project_resolve`
- `granoflow_project_create`
- `granoflow_project_update`
- `granoflow_project_delete`
- `granoflow_milestone_list`
- `granoflow_milestone_resolve`
- `granoflow_milestone_create`
- `granoflow_milestone_update`
- `granoflow_milestone_delete`
- `granoflow_review_day_show`
- `granoflow_api_request`

Prefer the structured task, project, and milestone tools for common resource
operations. The JSON payload tools remain available as escape hatches when the
running app exposes newer fields before this package has first-class schemas.

For historical, decision, lesson, or similar-work questions, use the bundled
workflow skill first. It explains how to treat tasks, task reviews, review cards,
projects, milestones, and periodic reviews as bounded long-term work memory
without pretending there is a dedicated semantic search endpoint.

Write tools default to dry-run behavior. Ask the tool to write only after you
have reviewed the preview or the user has explicitly requested a write.
Delete tools also require the current resource title before writing, and refuse
linked tasks unless the caller explicitly accepts that impact.

When a user asks to complete, finish, close, mark done, wrap up, or otherwise
end a task, prefer `granoflow_task_finish` over the low-level
`granoflow_task_complete` endpoint. Before writing, infer `startedAt` and
`endedAt` from the current agent conversation when evidence is available. Write
`taskReview` only when there is a meaningful decision, lesson, failure mode, or
reusable process detail; leave it empty when it would only say what happened.
Create one `reviewCardDrafts` item per durable knowledge point worth long-term
memory, and omit cards when there is nothing worth remembering.

After 16:30 local time, tool results may include a `dailyReviewSuggestion`. It is
stored in the non-secret MCP config and appears at most once per local day. When
present, agents should mention it only after the user's current request has been
handled.

On Friday, Saturday, Sunday, and Monday, that suggestion may also include a
`weeklyReviewSuggestion`. The MCP server checks the Granoflow weekly review log:
Friday through Sunday check the current week, and Monday checks the previous
week. If the weekly log has no written content or values yet, agents should add
the weekly-review nudge after the daily-review nudge.

On the last day of a month, the same suggestion may include a
`monthlyReviewSuggestion` for the current month. On the first day of a month, it
checks the previous month. If the monthly review has no visible written content
or values yet, agents should add the monthly-review nudge too.

The bundled Granoflow Agent Workflow skill also defines how agents should help
with reviews. For daily reviews, agents may draft concise mood and efficiency
notes from the day's tasks, timing, reviews, project context, flow time,
interruptions, and user-confirmed signals, but save scores and notes only after
user confirmation. Saved `moodNote` and `efficiencyNote` content should be short
personal review notes, not scoring explanations, interaction text, or fixed
templates. For weekly reviews, agents should focus on patterns across the week
and user-confirmed value scores/notes. For monthly reviews, agents may draft and
write confirmed `content`, while monthly aggregate metrics remain read-only.

## Setup Diagnostics

Use the setup tools when an agent or MCP client needs to connect to a local
Granoflow app without hand-editing every setting first:

- `granoflow_setup_status` reports config path, env/config precedence, token
  presence, MCP server version, Local HTTP API health, version metadata,
  capability summary, and local Granoflow process evidence without printing
  secrets.
- `granoflow_setup_detect_local_api` probes a small bounded localhost port list
  only.
- `granoflow_setup_write_config` previews or writes non-secret config. It
  defaults to dry-run.
- `granoflow_setup_open_config` creates and optionally opens the config file for
  manual editing.
- `granoflow_setup_open_app` previews or opens the installed Granoflow app after
  user approval. On macOS it tries the formal `/Applications/granoflow.app`
  path before app-name fallbacks. It defaults to dry-run.

When setup status sees a configured localhost API URL that is unreachable, it
checks whether a local Granoflow process appears to be running. If not, it
returns a warning and asks the agent to confirm before opening the app.

## Client Support

This package implements a standard MCP stdio server. The primary compatibility
contract is the MCP protocol plus the npm executable:

```bash
npx -y @granoflow/mcp-server
```

Cursor and Codex are the verified client targets for this repository. Other
MCP-compatible clients can use the same stdio command shape, but are not part of
the routine verification matrix.

## Cursor

Add this to `.cursor/mcp.json` in a project or `~/.cursor/mcp.json` globally:

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

## Codex

Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.granoflow]
command = "npx"
args = ["-y", "@granoflow/mcp-server"]

[mcp_servers.granoflow.env]
GRANOFLOW_API_BASE_URL = "http://127.0.0.1:56789"
```

Restart Codex after changing MCP configuration.

## Other MCP-Compatible Clients

For clients that support local stdio MCP servers, configure the server with:

```jsonc
{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@granoflow/mcp-server"],
  "env": {
    "GRANOFLOW_API_BASE_URL": "http://127.0.0.1:56789",
  },
}
```

## Development

```bash
npm install
npm run check
```

`npm run check` runs Prettier, ESLint, TypeScript, and Vitest.

## Security

- This server does not read or write Granoflow's SQLite/Drift database.
- This server does not run Granoflow app builds, screenshots, release jobs, or
  scenario orchestration.
- Core operations go through the running app's Local HTTP API.
- API tokens are passed through environment variables and must not be logged.
