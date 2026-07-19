import { describe, expect, it } from "vitest";
import { tempConfigPath } from "./config-test-harness.js";
import { readFile, stat, writeFile } from "node:fs/promises";
import { resolveMcpRuntime, writeMcpConfig } from "../src/config.js";

describe("config-secrets-and-permissions", () => {
  it("preserves an explicitly supplied remote URL and labels its data boundary", async () => {
    const configPath = await tempConfigPath("remote-endpoint");
    const result = await writeMcpConfig(
      { apiBaseUrl: "https://granoflow.example.test:8443", dryRun: true },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    expect(result).toMatchObject({
      written: false,
      proposedApiBaseUrl: "https://granoflow.example.test:8443",
      targetScope: "remote",
    });
  });

  it("does not treat config token fields as usable API tokens", async () => {
    const configPath = await tempConfigPath("token");
    await writeMcpConfig(
      {
        apiBaseUrl: "http://127.0.0.1:56789",
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    const configWithToken = JSON.parse(await readFile(configPath, "utf8")) as Record<
      string,
      unknown
    >;
    configWithToken.apiToken = "should-not-be-used";
    await writeFile(configPath, JSON.stringify(configWithToken, null, 2));

    const runtime = await resolveMcpRuntime({ GRANOFLOW_MCP_CONFIG_PATH: configPath });

    expect(runtime.hasApiToken).toBe(false);
    expect(runtime.apiToken).toBeUndefined();
  });

  it("redacts secret-looking config keys in write results", async () => {
    const configPath = await tempConfigPath("redact");
    await writeMcpConfig(
      {
        apiBaseUrl: "http://127.0.0.1:56789",
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );
    const raw = JSON.parse(await readFile(configPath, "utf8")) as Record<string, unknown>;
    raw.refreshToken = "secret-value";
    await writeFile(configPath, JSON.stringify(raw, null, 2));

    const result = await writeMcpConfig(
      {
        apiBaseUrl: "http://127.0.0.1:60000",
        dryRun: true,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    expect(result.previousConfig.refreshToken).toBe("[REDACTED]");
    expect(JSON.stringify(result)).not.toContain("secret-value");
  });

  it("writes real config files with owner-only permissions", async () => {
    const configPath = await tempConfigPath("write");
    const result = await writeMcpConfig(
      {
        apiBaseUrl: "http://127.0.0.1:56789",
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    const mode = (await stat(configPath)).mode & 0o777;
    expect(result.written).toBe(true);
    expect(mode).toBe(0o600);
  });
});
