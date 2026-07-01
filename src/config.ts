import { mkdir, open, readFile, rename, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";

export interface GranoflowMcpConfig {
  apiBaseUrl?: string;
  cliPath?: string;
  [key: string]: unknown;
}

export interface ConfigReadResult {
  configPath: string;
  exists: boolean;
  config: GranoflowMcpConfig;
  error?: string;
}

export interface RuntimeResolution {
  configPath: string;
  configExists: boolean;
  configError?: string;
  apiBaseUrl?: string;
  apiBaseUrlSource: "env" | "config" | "default";
  cliPath?: string;
  cliPathSource: "env" | "config" | "default";
  hasApiToken: boolean;
  apiTokenSource: "env" | "none";
  env: NodeJS.ProcessEnv;
}

export interface WriteConfigInput {
  apiBaseUrl?: string;
  cliPath?: string;
  dryRun?: boolean;
}

export interface WriteConfigResult {
  configPath: string;
  dryRun: boolean;
  written: boolean;
  backupPath: string | null;
  previousConfig: Record<string, unknown>;
  nextConfig: Record<string, unknown>;
  changedKeys: string[];
  nextActions: string[];
}

const SECRET_KEY_PATTERN = /(token|secret|password|credential|key)/i;

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function validateApiBaseUrl(apiBaseUrl: string): void {
  const url = new URL(apiBaseUrl);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("apiBaseUrl must use http or https.");
  }
}

function stableJson(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

export function getMcpConfigPath(env: NodeJS.ProcessEnv = process.env): string {
  if (env.GRANOFLOW_MCP_CONFIG_PATH) {
    return env.GRANOFLOW_MCP_CONFIG_PATH;
  }
  if (env.XDG_CONFIG_HOME) {
    return join(env.XDG_CONFIG_HOME, "granoflow-mcp", "config.json");
  }
  return join(homedir(), ".config", "granoflow-mcp", "config.json");
}

export function redactConfig(config: GranoflowMcpConfig): Record<string, unknown> {
  const redacted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(config)) {
    redacted[key] = SECRET_KEY_PATTERN.test(key) && value !== undefined ? "[REDACTED]" : value;
  }
  return redacted;
}

export async function readMcpConfig(
  env: NodeJS.ProcessEnv = process.env,
): Promise<ConfigReadResult> {
  const configPath = getMcpConfigPath(env);
  try {
    const text = await readFile(configPath, "utf8");
    const parsed: unknown = JSON.parse(text);
    if (!isObject(parsed)) {
      return {
        configPath,
        exists: true,
        config: {},
        error: "Config file must contain a JSON object.",
      };
    }
    return { configPath, exists: true, config: parsed };
  } catch (error) {
    if (isObject(error) && "code" in error && error.code === "ENOENT") {
      return { configPath, exists: false, config: {} };
    }
    return {
      configPath,
      exists: false,
      config: {},
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export async function resolveMcpRuntime(
  env: NodeJS.ProcessEnv = process.env,
): Promise<RuntimeResolution> {
  const configResult = await readMcpConfig(env);
  const config = configResult.config;
  const apiBaseUrl =
    env.GRANOFLOW_API_BASE_URL ??
    (typeof config.apiBaseUrl === "string" ? config.apiBaseUrl : undefined);
  const cliPath =
    env.GRANOFLOW_CLI_PATH ?? (typeof config.cliPath === "string" ? config.cliPath : undefined);
  const resolvedEnv: NodeJS.ProcessEnv = { ...env };

  if (apiBaseUrl) {
    resolvedEnv.GRANOFLOW_API_BASE_URL = apiBaseUrl;
  }
  if (cliPath) {
    resolvedEnv.GRANOFLOW_CLI_PATH = cliPath;
  }

  return {
    configPath: configResult.configPath,
    configExists: configResult.exists,
    configError: configResult.error,
    apiBaseUrl,
    apiBaseUrlSource: env.GRANOFLOW_API_BASE_URL ? "env" : apiBaseUrl ? "config" : "default",
    cliPath,
    cliPathSource: env.GRANOFLOW_CLI_PATH ? "env" : cliPath ? "config" : "default",
    hasApiToken: Boolean(env.GRANOFLOW_API_TOKEN),
    apiTokenSource: env.GRANOFLOW_API_TOKEN ? "env" : "none",
    env: resolvedEnv,
  };
}

export async function writeMcpConfig(
  input: WriteConfigInput,
  env: NodeJS.ProcessEnv = process.env,
): Promise<WriteConfigResult> {
  if (input.apiBaseUrl !== undefined) {
    validateApiBaseUrl(input.apiBaseUrl);
  }
  const readResult = await readMcpConfig(env);
  const nextConfig: GranoflowMcpConfig = { ...readResult.config };
  if (input.apiBaseUrl !== undefined) {
    nextConfig.apiBaseUrl = input.apiBaseUrl;
  }
  if (input.cliPath !== undefined) {
    nextConfig.cliPath = input.cliPath;
  }

  const previousConfig = redactConfig(readResult.config);
  const redactedNextConfig = redactConfig(nextConfig);
  const changedKeys = Object.keys(redactedNextConfig).filter(
    (key) => previousConfig[key] !== redactedNextConfig[key],
  );
  const dryRun = input.dryRun !== false;

  if (dryRun) {
    return {
      configPath: readResult.configPath,
      dryRun,
      written: false,
      backupPath: null,
      previousConfig,
      nextConfig: redactedNextConfig,
      changedKeys,
      nextActions: [
        "Review the config preview.",
        "Call this tool again with dryRun=false to write.",
      ],
    };
  }

  await mkdir(dirname(readResult.configPath), { recursive: true });
  let backupPath: string | null = null;
  if (readResult.exists) {
    backupPath = `${readResult.configPath}.bak-${new Date().toISOString().replace(/[:.]/g, "-")}`;
    await writeFile(backupPath, stableJson(readResult.config), { mode: 0o600 });
  }

  const tempPath = `${readResult.configPath}.tmp-${process.pid}`;
  await writeFile(tempPath, stableJson(nextConfig), { mode: 0o600 });
  await rename(tempPath, readResult.configPath);
  const handle = await open(readResult.configPath, "r+");
  await handle.chmod(0o600);
  await handle.close();

  return {
    configPath: readResult.configPath,
    dryRun,
    written: true,
    backupPath,
    previousConfig,
    nextConfig: redactedNextConfig,
    changedKeys,
    nextActions: [
      "Restart or reload the MCP client if it keeps a long-running server process.",
      "Call granoflow_setup_status to verify the resolved configuration.",
    ],
  };
}

export async function configFileExists(configPath: string): Promise<boolean> {
  try {
    await stat(configPath);
    return true;
  } catch (error) {
    if (isObject(error) && "code" in error && error.code === "ENOENT") {
      return false;
    }
    throw error;
  }
}
