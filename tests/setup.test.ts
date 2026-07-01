import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

import { afterEach, describe, expect, it } from "vitest";

import { detectLocalApi, getSetupStatus, installOrUpdateCli } from "../src/setup.js";
import type { CliResult } from "../src/cli.js";

const servers: Array<{ close: () => Promise<void> }> = [];

async function startServer(
  handler: (request: IncomingMessage, response: ServerResponse) => void,
): Promise<number> {
  const server = createServer(handler);
  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });
  servers.push({
    close: () =>
      new Promise((resolve, reject) => {
        server.close((error) => (error ? reject(error) : resolve()));
      }),
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Expected TCP test server address.");
  }
  return address.port;
}

afterEach(async () => {
  while (servers.length > 0) {
    const server = servers.pop();
    if (server) {
      await server.close();
    }
  }
});

describe("setup diagnostics", () => {
  it("detects a Granoflow-shaped localhost health response", async () => {
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ service: "granoflow", status: "ok" }));
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidates).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          apiBaseUrl: `http://127.0.0.1:${port}`,
          confidence: "high",
          authRequired: false,
        }),
      ]),
    );
  });

  it("treats fixed-path 401 responses as auth-required weak evidence", async () => {
    const port = await startServer((_request, response) => {
      response.statusCode = 401;
      response.end("unauthorized");
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidates).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          apiBaseUrl: `http://127.0.0.1:${port}`,
          confidence: "low",
          authRequired: true,
        }),
      ]),
    );
  });

  it("reports setup status without exposing token values", async () => {
    const cliResult: CliResult = {
      exitCode: 0,
      stdout: "{}",
      stderr: "",
      json: {},
    };

    const result = await getSetupStatus({
      env: {
        GRANOFLOW_API_BASE_URL: "http://127.0.0.1:56789",
        GRANOFLOW_API_TOKEN: "secret-token",
      },
      runCli: async () => cliResult,
    });

    expect(result.apiToken).toEqual({ present: true, source: "env" });
    expect(JSON.stringify(result)).not.toContain("secret-token");
    expect(result.health).toMatchObject({ ok: true, exitCode: 0 });
  });

  it("asks for CLI install/update approval when the CLI is missing", async () => {
    const missingCliError = new Error("spawn granoflow ENOENT") as Error & { code: string };
    missingCliError.code = "ENOENT";

    const result = await getSetupStatus({
      env: {},
      runCli: async () => {
        throw missingCliError;
      },
    });

    expect(result.health).toMatchObject({ ok: false, cliMissing: true });
    expect(result.nextActions).toEqual(
      expect.arrayContaining([
        "Ask the user whether they want to install or update granoflow-cli.",
      ]),
    );
  });

  it("requires an explicit install source before installing or updating the CLI", async () => {
    const result = await installOrUpdateCli({}, { env: {} });

    expect(result).toMatchObject({
      ok: false,
      dryRun: true,
      packageSpec: null,
    });
    expect(JSON.stringify(result)).toContain("GRANOFLOW_CLI_INSTALL_SPEC");
  });

  it("previews the CLI install/update command by default", async () => {
    const result = await installOrUpdateCli({
      packageSpec: "https://example.com/granoflow-cli.tgz",
    });

    expect(result).toMatchObject({
      ok: true,
      dryRun: true,
      command: "npm",
      args: ["install", "--global", "https://example.com/granoflow-cli.tgz"],
    });
  });
});
