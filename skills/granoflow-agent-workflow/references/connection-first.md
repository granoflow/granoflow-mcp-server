# Connection First

Read this reference when the Local HTTP API may be unreachable, the user just
installed the MCP server, or setup/config diagnostics are needed before any
Granoflow read or write.

## When to read

- `granoflow_setup_status` / health / config work
- First-run confusion about what Granoflow MCP is
- Task Work binding when the API is down

## Required behavior

If the Local HTTP API is unreachable, tell the user briefly what Granoflow is,
link to https://granoflow.com, and explain that the local app must be open with
the Local HTTP API enabled before MCP tools can read or write tasks.

Call `granoflow_setup_status` before guessing why it failed. Treat
`reachable_auth_required` as an authentication problem, not a port problem. If
`configuration_shadowed_by_env` is present, explain that the saved config cannot
take effect until the MCP client's `GRANOFLOW_API_BASE_URL` is changed or
removed; never rewrite the same shadowed value and claim success.

Port discovery is bounded to explicit localhost candidates. Never scan all
ports, automatically persist a candidate, or treat generic status JSON as
Granoflow identity. Before asking once for configuration approval, call
`granoflow_setup_write_config` in dry-run mode and show the candidate evidence,
config path, old and new values, `changedKeys`, environment shadow state, and
remote/local data boundary. One confirmation of that complete preview authorizes
only that exact config write. Read the config and health back immediately;
normal writes do not require an MCP restart.

For Task Work, report `bound_local_draft`, `unbound_local_draft`, or
`no_local_draft` from real host evidence. An unreachable API also means
`upload_blocked_api_unreachable`, `attachment_readback_pending`,
`active_not_established`, and `reconciliation_required`. Never invent a local
path, GF task identity, attachment, node, description write, or active pointer.
Use the Task Work Document workflow for the recovery sequence.

If the user seems to have installed the MCP server without knowing Granoflow,
explain that this MCP server is a bridge to the running Granoflow app, not a
standalone task database or a coding-agent capability booster.

## Success criteria

- The user knows Granoflow is the local app behind this MCP bridge.
- The next action is clear: open Granoflow, enable Local HTTP API, or call a
  setup diagnostic tool.

## Checkpoints

- Status tool ran before port/config guesses.
- Dry-run config preview shown before any persist.
- Readback proves config/health after write; env shadow called out when present.
