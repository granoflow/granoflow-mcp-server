# Granoflow MCP User Install And Demo Guide

This guide helps you connect Codex or Cursor to the Granoflow desktop app
through the Granoflow Local HTTP API.

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

## 6. Dry-Run Write Demo

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
