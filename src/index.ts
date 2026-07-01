#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { SERVER_NAME, SERVER_VERSION } from "./metadata.js";
import { registerGranoflowTools } from "./tools.js";

function printHelp() {
  process.stdout.write(`${SERVER_NAME} ${SERVER_VERSION}

Usage:
  granoflow-mcp-server
  granoflow-mcp-server --help
  granoflow-mcp-server --version

Starts the Granoflow MCP server over stdio.

Environment:
  GRANOFLOW_CLI_PATH       Optional absolute path to the granoflow CLI.
  GRANOFLOW_API_BASE_URL   Optional Granoflow Local HTTP API base URL.
  GRANOFLOW_API_TOKEN      Optional Granoflow Local HTTP API token.
  GRANOFLOW_MCP_CONFIG_PATH Optional path for MCP-owned non-secret config.
`);
}

if (process.argv.includes("--version") || process.argv.includes("-v")) {
  process.stdout.write(`${SERVER_VERSION}\n`);
  process.exit(0);
}

if (process.argv.includes("--help") || process.argv.includes("-h")) {
  printHelp();
  process.exit(0);
}

const server = new McpServer({
  name: SERVER_NAME,
  version: SERVER_VERSION,
});

registerGranoflowTools(server);

const transport = new StdioServerTransport();
await server.connect(transport);
