#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { SERVER_NAME, SERVER_VERSION } from "./metadata.js";
import { registerGranoflowTools } from "./tools.js";

function printHelp() {
  process.stdout.write(`${SERVER_NAME} ${SERVER_VERSION}

Usage:
  granoflow-mcp-server
  granoflow-mcp-server gfmcp-runner [runner options]
  granoflow-mcp-server --help
  granoflow-mcp-server --version

Starts the Granoflow MCP server over stdio.

Environment:
  GRANOFLOW_API_BASE_URL    Optional Granoflow Local HTTP API base URL.
  GRANOFLOW_API_TOKEN       Optional Granoflow Local HTTP API token.
  GRANOFLOW_MCP_CONFIG_PATH Optional path for MCP-owned non-secret config.
`);
}

if (process.argv[2] === "gfmcp-runner") {
  process.argv.splice(2, 1);
  await import("./gfmcp-runner-launcher.js");
  process.exit(0);
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
