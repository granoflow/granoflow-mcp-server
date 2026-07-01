# Granoflow MCP Server

MCP server for Granoflow: exposes the local REST API and `granoflow` CLI as
tools for AI agents, IDEs, and automation.

This server is intentionally thin. It delegates core operations to
[`granoflow-cli`](https://github.com/granoflow/granoflow-cli), which owns the
Granoflow Local HTTP API contract, JSON envelopes, configuration loading, token
handling, and OpenAPI drift checks.

## Requirements

- Node.js 20 or newer.
- `granoflow-cli` installed and available as `granoflow`.
- A running Granoflow app with the Local HTTP API enabled.

The default Granoflow API URL is owned by `granoflow-cli`. You can override it
with:

```bash
export GRANOFLOW_API_BASE_URL="http://127.0.0.1:56789"
export GRANOFLOW_API_TOKEN="..."
```

If the CLI is not on `PATH`, point the MCP server at it:

```bash
export GRANOFLOW_CLI_PATH="/absolute/path/to/granoflow"
```

The MCP server can also keep non-secret local connection defaults in:

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
npm run check
npm pack --dry-run
```

## Tools

Initial tools:

- `granoflow_setup_status`
- `granoflow_setup_detect_local_api`
- `granoflow_setup_write_config`
- `granoflow_setup_open_config`
- `granoflow_health`
- `granoflow_capabilities`
- `granoflow_ai_agent_tools`
- `granoflow_task_list`
- `granoflow_task_export`
- `granoflow_task_validate`
- `granoflow_task_import`
- `granoflow_task_create`
- `granoflow_task_complete`
- `granoflow_project_list`
- `granoflow_review_day_show`
- `granoflow_cli`

`granoflow_task_import`, `granoflow_task_create`, and
`granoflow_task_complete` default to dry-run behavior. Ask the tool to write
only after you have reviewed the preview.

## Setup Diagnostics

Use the setup tools when an agent or MCP client needs to connect to a local
Granoflow app without hand-editing every setting first:

- `granoflow_setup_status` reports config path, env/config precedence, token
  presence, and CLI health without printing secrets.
- `granoflow_setup_detect_local_api` probes a small bounded localhost port list
  only.
- `granoflow_setup_write_config` previews or writes non-secret config. It
  defaults to dry-run.
- `granoflow_setup_open_config` creates and optionally opens the config file for
  manual editing.

## Client support

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
- Core operations go through `granoflow-cli` and the running app's Local HTTP
  API.
- API tokens are passed through environment variables and must not be logged.
