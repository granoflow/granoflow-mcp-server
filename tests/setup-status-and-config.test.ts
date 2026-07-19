import { describe, expect, it } from "vitest";
import { installSetupTestLifecycle, startServer } from "./setup-test-harness.js";
import { getSetupStatus } from "../src/setup.js";

installSetupTestLifecycle();

describe("setup-status-and-config", () => {
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
        stdout: "123\n",
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
      matches: ["123"],
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
});
