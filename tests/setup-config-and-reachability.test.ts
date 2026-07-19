import { describe, expect, it } from "vitest";
import { installSetupTestLifecycle, startServer, tempPaths } from "./setup-test-harness.js";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { getSetupStatus, writeSetupConfig } from "../src/setup.js";
import { writeMcpConfig } from "../src/config.js";

installSetupTestLifecycle();

describe("setup-config-and-reachability", () => {
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
});
