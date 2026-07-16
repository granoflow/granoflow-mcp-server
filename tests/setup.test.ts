import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { writeMcpConfig } from "../src/config.js";
import {
  detectLocalApi,
  getSetupStatus,
  openGranoflowApp,
  writeSetupConfig,
} from "../src/setup.js";

const servers: Array<{ close: () => Promise<void> }> = [];
const tempPaths: string[] = [];

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
  await Promise.all(tempPaths.splice(0).map((path) => rm(path, { recursive: true, force: true })));
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
    expect(result.candidateState).toBe("single_high_confidence");
  });

  it("does not mistake generic localhost status JSON for Granoflow", async () => {
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ status: "ok", version: "1.0.0" }));
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidates).toEqual([]);
    expect(result.candidateState).toBe("ambiguous_non_granoflow_service");
  });

  it("returns all high-confidence candidates instead of choosing between them", async () => {
    const handler = (_request: IncomingMessage, response: ServerResponse) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ service: "granoflow", status: "ok" }));
    };
    const firstPort = await startServer(handler);
    const secondPort = await startServer(handler);

    const result = await detectLocalApi({ ports: [firstPort, secondPort], timeoutMs: 500 });

    expect(result.candidateState).toBe("multiple_high_confidence");
    expect(result.candidates).toHaveLength(2);
  });

  it("accepts consistent Granoflow envelopes on both fixed v1 endpoints", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/health" || request.url === "/v1/capabilities") {
        response.end(JSON.stringify({ ok: true, code: "ok", data: { path: request.url } }));
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ status: "not_found" }));
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidateState).toBe("single_high_confidence");
    expect(result.candidates[0]).toMatchObject({
      apiBaseUrl: `http://127.0.0.1:${port}`,
      confidence: "high",
    });
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
    expect(result.candidateState).toBe("auth_required_only");
  });

  it("reports setup status from the Local HTTP API without exposing token values", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/health") {
        response.end(JSON.stringify({ ok: true, code: "ok", data: { status: "ready" } }));
        return;
      }
      if (request.url === "/v1/version") {
        response.end(
          JSON.stringify({
            ok: true,
            code: "ok",
            data: { version: "0.1.0+7", releaseDate: "2026-07-01" },
          }),
        );
        return;
      }
      if (request.url === "/v1/capabilities") {
        response.end(
          JSON.stringify({
            ok: true,
            code: "ok",
            data: { tools: ["task.list", "task.finish"], capabilities: ["tasks"] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false, code: "not_found" }));
    });

    const result = await getSetupStatus({
      env: {
        GRANOFLOW_API_BASE_URL: `http://127.0.0.1:${port}`,
        GRANOFLOW_API_TOKEN: "secret-token",
      },
      runCommand: async () => ({
        exitCode: 0,
        stdout: "123 /Applications/granoflow.app/Contents/MacOS/granoflow\n",
        stderr: "",
      }),
    });

    expect(result.apiToken).toEqual({ present: true, source: "env" });
    expect(JSON.stringify(result)).not.toContain("secret-token");
    expect(result.health).toMatchObject({ ok: true, code: "ok" });
    expect(result.version).toMatchObject({ ok: true, code: "ok" });
    expect(result.mcp).toMatchObject({
      serverName: "granoflow-mcp-server",
      serverVersion: expect.stringMatching(/^\d+\.\d+\.\d+/),
    });
    expect(result.capabilities).toMatchObject({
      available: true,
      toolCount: 2,
      capabilityCount: 1,
    });
    expect(result.appProcess).toMatchObject({
      checked: true,
      running: true,
      matches: ["123 /Applications/granoflow.app/Contents/MacOS/granoflow"],
    });
    expect(result.warnings).toEqual([]);
  });

  it("reports authentication failure without suggesting a different port", async () => {
    const port = await startServer((_request, response) => {
      response.statusCode = 401;
      response.end(JSON.stringify({ ok: false, code: "unauthorized" }));
    });

    const result = await getSetupStatus({
      env: { GRANOFLOW_API_BASE_URL: `http://127.0.0.1:${port}` },
      runCommand: async () => ({ exitCode: 0, stdout: "123 Granoflow\n", stderr: "" }),
    });

    expect(result.warnings).toEqual(
      expect.arrayContaining([expect.objectContaining({ code: "reachable_auth_required" })]),
    );
    expect(JSON.stringify(result.nextActions)).not.toContain("detect_local_api");
  });

  it("writes a selected port once and immediately verifies the persisted config", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, code: "ok", data: { path: request.url } }));
    });
    const root = join(tmpdir(), `granoflow-setup-write-${process.pid}-${Date.now()}`);
    tempPaths.push(root);

    const result = await writeSetupConfig(
      { apiPort: port, dryRun: false },
      {
        env: { GRANOFLOW_MCP_CONFIG_PATH: join(root, "config.json") },
        runCommand: async () => ({ exitCode: 0, stdout: "123 Granoflow\n", stderr: "" }),
      },
    );

    expect(result).toMatchObject({
      persistedApiBaseUrl: `http://127.0.0.1:${port}`,
      effectiveSource: "config",
      shadowedByEnv: false,
      verification: {
        apiBaseUrl: `http://127.0.0.1:${port}`,
        apiBaseUrlSource: "config",
        health: { ok: true },
      },
    });
  });

  it("reports when an environment URL shadows the persisted config", async () => {
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, code: "ok", data: {} }));
    });
    const root = join(tmpdir(), `granoflow-setup-shadow-${process.pid}-${Date.now()}`);
    const configPath = join(root, "config.json");
    tempPaths.push(root);
    await writeMcpConfig(
      { apiPort: 61_234, dryRun: false },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    const result = await getSetupStatus({
      env: {
        GRANOFLOW_MCP_CONFIG_PATH: configPath,
        GRANOFLOW_API_BASE_URL: `http://127.0.0.1:${port}`,
      },
      runCommand: async () => ({ exitCode: 0, stdout: "123 Granoflow\n", stderr: "" }),
    });

    expect(result.warnings).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          code: "configuration_shadowed_by_env",
          configuredApiBaseUrl: "http://127.0.0.1:61234",
          effectiveApiBaseUrl: `http://127.0.0.1:${port}`,
        }),
      ]),
    );
    expect(result.nextActions[0]).toContain("GRANOFLOW_API_BASE_URL");
  });

  it("warns when a configured local API is unreachable and Granoflow is not running", async () => {
    const result = await getSetupStatus({
      env: {
        GRANOFLOW_API_BASE_URL: "http://127.0.0.1:9",
      },
      runCommand: async () => ({
        exitCode: 1,
        stdout: "",
        stderr: "",
      }),
    });

    expect(result.health).toMatchObject({
      ok: false,
      appProcess: expect.objectContaining({ checked: true, running: false, count: 0 }),
    });
    expect(result.warnings).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          code: "granoflow_app_not_running",
          granoflow: expect.objectContaining({
            website: "https://granoflow.com",
            description: expect.stringContaining("long-term work memory layer"),
            localPrivacy: expect.stringContaining("do not subscribe"),
          }),
        }),
      ]),
    );
    expect(result.nextActions).toEqual(
      expect.arrayContaining(["Ask the user whether they want to open Granoflow."]),
    );
  });

  it("previews opening the installed Granoflow app by default", async () => {
    const result = await openGranoflowApp({
      appName: "Granoflow",
    });

    expect(result).toMatchObject({
      dryRun: true,
      appName: "Granoflow",
      attempts: expect.arrayContaining([
        expect.objectContaining({ kind: "path", args: ["/Applications/granoflow.app"] }),
        expect.objectContaining({ kind: "appName", args: ["-a", "Granoflow"] }),
      ]),
    });
    expect(JSON.stringify(result)).toContain("Granoflow");
  });

  it("opens the first successful Granoflow app candidate", async () => {
    const calls: string[][] = [];
    const result = await openGranoflowApp(
      { appPath: "/Custom/granoflow.app", dryRun: false },
      {
        runCommand: async (_command, args) => {
          calls.push(args);
          return {
            exitCode: args[0] === "/Applications/granoflow.app" ? 0 : 1,
            stdout: "",
            stderr: args[0] === "/Applications/granoflow.app" ? "" : "not found",
          };
        },
      },
    );

    expect(result).toMatchObject({ ok: true, dryRun: false });
    expect(calls).toEqual([["/Custom/granoflow.app"], ["/Applications/granoflow.app"]]);
  });
});
