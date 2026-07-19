import { describe, expect, it } from "vitest";
import { tempConfigPath } from "./config-test-harness.js";
import { readMcpConfig, resolveMcpRuntime, writeMcpConfig } from "../src/config.js";

describe("config-path-and-runtime", () => {
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
        dryRun: false,
      },
      { GRANOFLOW_MCP_CONFIG_PATH: configPath },
    );

    const runtime = await resolveMcpRuntime({
      GRANOFLOW_MCP_CONFIG_PATH: configPath,
      GRANOFLOW_API_BASE_URL: "http://127.0.0.1:60000",
      GRANOFLOW_API_TOKEN: "secret-token",
    });

    expect(runtime.apiBaseUrl).toBe("http://127.0.0.1:60000");
    expect(runtime.apiBaseUrlSource).toBe("env");
    expect(runtime.hasApiToken).toBe(true);
    expect(runtime.apiTokenSource).toBe("env");
  });

  it("persists a user-selected local port and reports an environment override", async () => {
    const configPath = await tempConfigPath("custom-port");
    const env = { GRANOFLOW_MCP_CONFIG_PATH: configPath };

    const written = await writeMcpConfig({ apiPort: 61_234, dryRun: false }, env);
    expect(written).toMatchObject({
      written: true,
      persistedApiBaseUrl: "http://127.0.0.1:61234",
      effectiveApiBaseUrl: "http://127.0.0.1:61234",
      effectiveSource: "config",
      targetScope: "local",
      shadowedByEnv: false,
    });

    const shadowed = await writeMcpConfig(
      { apiPort: 61_234, dryRun: true },
      { ...env, GRANOFLOW_API_BASE_URL: "http://127.0.0.1:62000" },
    );
    expect(shadowed).toMatchObject({
      code: "configuration_shadowed_by_env",
      persistedApiBaseUrl: "http://127.0.0.1:61234",
      effectiveApiBaseUrl: "http://127.0.0.1:62000",
      effectiveSource: "env",
      shadowedByEnv: true,
    });
  });

  it("rejects ambiguous or unsafe custom endpoint input", async () => {
    const configPath = await tempConfigPath("invalid-endpoint");
    const env = { GRANOFLOW_MCP_CONFIG_PATH: configPath };

    await expect(writeMcpConfig({ apiPort: 0, dryRun: true }, env)).rejects.toThrow(
      "apiPort must be an integer between 1 and 65535",
    );
    await expect(
      writeMcpConfig({ apiPort: 61_234, apiBaseUrl: "http://127.0.0.1:61234", dryRun: true }, env),
    ).rejects.toThrow("Provide apiBaseUrl or apiPort, not both");
    await expect(
      writeMcpConfig({ apiBaseUrl: "http://user:secret@127.0.0.1:61234", dryRun: true }, env),
    ).rejects.toThrow("must not contain credentials");
  });
});
