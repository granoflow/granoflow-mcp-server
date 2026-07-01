import { mkdir, readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

import { describe, expect, it } from "vitest";

import { readMcpConfig, resolveMcpRuntime, writeMcpConfig } from "../src/config.js";

async function tempConfigPath(name: string) {
  const dir = join(tmpdir(), `granoflow-mcp-${name}-${process.pid}-${Date.now()}`);
  await mkdir(dir, { recursive: true });
  return join(dir, "config.json");
}

describe("MCP config", () => {
  it("uses GRANOFLOW_MCP_CONFIG_PATH as the config location", async () => {
    const configPath = await tempConfigPath("path");
    const result = await readMcpConfig({ GRANOFLOW_MCP_CONFIG_PATH: configPath });

    expect(result.configPath).toBe(configPath);
    expect(result.exists).toBe(false);
  });

  it("resolves environment variables before config values", async () => {
    const configPath = await tempConfigPath("precedence");
    await writeMcpConfig(
      {
        apiBaseUrl: "http://127.0.0.1:56789",
        cliPath: "/config/granoflow",
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    const runtime = await resolveMcpRuntime({
      GRANOFLOW_MCP_CONFIG_PATH: configPath,
      GRANOFLOW_API_BASE_URL: "http://127.0.0.1:60000",
      GRANOFLOW_API_TOKEN: "secret-token",
      GRANOFLOW_CLI_PATH: "/env/granoflow",
    });

    expect(runtime.apiBaseUrl).toBe("http://127.0.0.1:60000");
    expect(runtime.apiBaseUrlSource).toBe("env");
    expect(runtime.cliPath).toBe("/env/granoflow");
    expect(runtime.cliPathSource).toBe("env");
    expect(runtime.hasApiToken).toBe(true);
    expect(runtime.apiTokenSource).toBe("env");
  });

  it("does not treat config token fields as usable API tokens", async () => {
    const configPath = await tempConfigPath("token");
    await mkdir(join(configPath, ".."), { recursive: true });
    await writeMcpConfig(
      {
        apiBaseUrl: "http://127.0.0.1:56789",
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    const text = await readFile(configPath, "utf8");
    await writeMcpConfig(
      {
        cliPath: "granoflow",
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );
    const configWithToken = JSON.parse(text) as Record<string, unknown>;
    configWithToken.apiToken = "should-not-be-used";
    await import("node:fs/promises").then(({ writeFile }) =>
      writeFile(configPath, JSON.stringify(configWithToken, null, 2)),
    );

    const runtime = await resolveMcpRuntime({ GRANOFLOW_MCP_CONFIG_PATH: configPath });

    expect(runtime.hasApiToken).toBe(false);
    expect(runtime.env.GRANOFLOW_API_TOKEN).toBeUndefined();
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
    await import("node:fs/promises").then(({ writeFile }) =>
      writeFile(configPath, JSON.stringify(raw, null, 2)),
    );

    const result = await writeMcpConfig(
      {
        cliPath: "granoflow",
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
