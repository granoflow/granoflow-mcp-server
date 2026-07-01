import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

import { afterEach, describe, expect, it } from "vitest";

import { detectLocalApi, getSetupStatus, openGranoflowApp } from "../src/setup.js";

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
