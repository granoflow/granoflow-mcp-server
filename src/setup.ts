import { spawn } from "node:child_process";
import { lstat, mkdir, rmdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";

import { GRANOFLOW_INTRODUCTION, requestGranoflowApi } from "./api.js";
import {
  configFileExists,
  getMcpConfigPath,
  readMcpConfig,
  resolveMcpRuntime,
  writeMcpConfig,
  type WriteConfigInput,
} from "./config.js";
import { SERVER_NAME, SERVER_VERSION } from "./metadata.js";

type CommandRunResult = {
  exitCode: number;
  stdout: string;
  stderr: string;
};

type CommandRunner = (command: string, args: string[]) => Promise<CommandRunResult>;

export interface SetupOptions {
  env?: NodeJS.ProcessEnv;
  fetch?: typeof fetch;
  runCommand?: CommandRunner;
  launchLockPath?: string;
  now?: () => number;
}

export interface LocalApiDetectionInput {
  ports?: number[];
  timeoutMs?: number;
}

export interface OpenAppInput {
  appPath?: string;
  appName?: string;
  dryRun?: boolean;
}

const APP_LAUNCH_LEASE_MS = 30_000;

function safeError(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isFileSystemError(error: unknown, code: string): boolean {
  return isObject(error) && error.code === code;
}

async function acquireAppLaunchLease(lockPath: string, now: () => number): Promise<boolean> {
  try {
    await mkdir(lockPath);
    return true;
  } catch (error) {
    if (!isFileSystemError(error, "EEXIST")) {
      throw error;
    }
  }

  try {
    const existing = await lstat(lockPath);
    if (now() - existing.mtimeMs < APP_LAUNCH_LEASE_MS) {
      return false;
    }
    await rmdir(lockPath);
  } catch (error) {
    if (!isFileSystemError(error, "ENOENT")) {
      return false;
    }
  }

  try {
    await mkdir(lockPath);
    return true;
  } catch {
    return false;
  }
}

async function releaseAppLaunchLease(lockPath: string): Promise<void> {
  try {
    await rmdir(lockPath);
  } catch {
    // A missing or externally replaced lease must not turn setup reporting into an error.
  }
}

function isLocalApiBaseUrl(apiBaseUrl: string | undefined): boolean {
  if (!apiBaseUrl) {
    return false;
  }
  try {
    const url = new URL(apiBaseUrl);
    return ["localhost", "127.0.0.1", "::1", "[::1]"].includes(url.hostname);
  } catch {
    return false;
  }
}

async function openPath(path: string): Promise<{ attempted: boolean; error?: string }> {
  if (process.platform !== "darwin" && process.platform !== "linux") {
    return { attempted: false, error: "Opening config files is only implemented for macOS/Linux." };
  }
  const command = process.platform === "darwin" ? "open" : "xdg-open";
  return await new Promise((resolve) => {
    const child = spawn(command, [path], { stdio: "ignore", detached: true });
    child.on("error", (error) => resolve({ attempted: true, error: safeError(error) }));
    child.on("spawn", () => {
      child.unref();
      resolve({ attempted: true });
    });
  });
}

async function runCommand(command: string, args: string[]): Promise<CommandRunResult> {
  return await new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk: string) => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", (exitCode) => {
      resolve({ exitCode: exitCode ?? 1, stdout, stderr });
    });
  });
}

async function checkGranoflowProcess(
  runCommandImpl: CommandRunner,
): Promise<Record<string, unknown>> {
  if (process.platform !== "darwin" && process.platform !== "linux") {
    return {
      checked: false,
      running: null,
      reason: "Process check is only implemented for macOS/Linux.",
    };
  }
  try {
    const result = await runCommandImpl("pgrep", ["-ix", "granoflow"]);
    const matches =
      result.exitCode === 0
        ? result.stdout
            .split("\n")
            .filter(Boolean)
            .map((line) => line.trim())
        : [];
    return {
      checked: true,
      running: matches.length > 0,
      count: matches.length,
      matches,
    };
  } catch (error) {
    return {
      checked: false,
      running: null,
      error: safeError(error),
    };
  }
}

function appProcessGuardResult(
  appProcess: Record<string, unknown>,
  input: OpenAppInput,
  dryRun: boolean,
): Record<string, unknown> | null {
  if (appProcess.running === true) {
    return {
      ok: false,
      code: "granoflow_app_already_running",
      dryRun,
      appName: input.appName ?? "Granoflow",
      appPath: input.appPath ?? null,
      appProcess,
      error:
        "Granoflow is already running. The MCP server will not try to open another instance, even when the configured Local HTTP API URL or port is unreachable.",
      nextActions: [
        "Do not open another Granoflow instance.",
        "Ask the user to resolve duplicate Granoflow instances, Local HTTP API availability, or the configured API URL or port.",
        "Call granoflow_setup_status again after the existing Granoflow instance is ready and correctly configured.",
      ],
    };
  }
  if (appProcess.checked !== true || appProcess.running !== false) {
    return {
      ok: false,
      code: "granoflow_process_check_failed",
      dryRun,
      appName: input.appName ?? "Granoflow",
      appPath: input.appPath ?? null,
      appProcess,
      error:
        "The MCP server could not verify whether Granoflow is already running, so it refused to open another instance.",
      nextActions: [
        "Check local process-inspection permissions or open Granoflow manually.",
        "Call granoflow_setup_status again after the process check is available.",
      ],
    };
  }
  return null;
}

async function executeAppOpenAttempts(
  attempts: Array<{ kind: string; args: string[] }>,
  runCommandImpl: CommandRunner,
): Promise<Array<Record<string, unknown>>> {
  const results: Array<Record<string, unknown>> = [];
  for (const attempt of attempts) {
    const result = await runCommandImpl("open", attempt.args);
    results.push({
      kind: attempt.kind,
      args: attempt.args,
      exitCode: result.exitCode,
      stderr: result.stderr.trim() ? "[present]" : "[empty]",
    });
    if (result.exitCode === 0) {
      break;
    }
  }
  return results;
}

async function prepareLaunchLease(
  input: OpenAppInput,
  dryRun: boolean,
  lockPath: string,
  now: () => number,
): Promise<{ acquired: boolean; failure?: Record<string, unknown> }> {
  if (dryRun) return { acquired: false };
  try {
    const acquired = await acquireAppLaunchLease(lockPath, now);
    if (acquired) return { acquired: true };
    return {
      acquired: false,
      failure: {
        ok: false,
        code: "granoflow_app_launch_in_progress",
        dryRun,
        appName: input.appName ?? "Granoflow",
        appPath: input.appPath ?? null,
        error:
          "Another Granoflow MCP launch request is still in progress, so this request will not inspect or open the app again.",
        nextActions: [
          "Do not open another Granoflow instance.",
          "Wait for the existing launch request, then call granoflow_setup_status.",
        ],
      },
    };
  } catch (error) {
    return {
      acquired: false,
      failure: {
        ok: false,
        code: "granoflow_app_launch_guard_failed",
        dryRun,
        appName: input.appName ?? "Granoflow",
        appPath: input.appPath ?? null,
        error: `The MCP server could not establish its single-launch guard: ${safeError(error)}`,
        nextActions: [
          "Check local temporary-directory permissions.",
          "Open Granoflow manually only after confirming that no Granoflow instance is running.",
        ],
      },
    };
  }
}

function summarizeCapabilities(value: unknown): Record<string, unknown> {
  const data = isObject(value) ? value.data : null;
  const payload = isObject(data) && isObject(data.data) ? data.data : data;
  if (!isObject(payload)) {
    return {
      available: false,
    };
  }
  const tools = Array.isArray(payload.tools) ? payload.tools : [];
  const aiAgent = isObject(payload.aiAgent) ? payload.aiAgent : {};
  const aiAgentTools = Array.isArray(aiAgent.tools) ? aiAgent.tools : [];
  const capabilities = Array.isArray(payload.capabilities) ? payload.capabilities : [];
  const resources = isObject(payload.resources) ? Object.keys(payload.resources) : [];
  return {
    available: true,
    apiVersion: payload.apiVersion,
    appVersion: payload.appVersion,
    resourceCount: resources.length,
    resources,
    toolCount: tools.length + aiAgentTools.length,
    capabilityCount: capabilities.length,
    tools: [...tools, ...aiAgentTools].slice(0, 20),
    truncated: tools.length + aiAgentTools.length > 20,
  };
}

function mcpRuntimeSummary() {
  return {
    serverName: SERVER_NAME,
    serverVersion: SERVER_VERSION,
  };
}

function unavailableSetupStatus(
  runtime: Awaited<ReturnType<typeof resolveMcpRuntime>>,
  health: Awaited<ReturnType<typeof requestGranoflowApi>>,
  version: Awaited<ReturnType<typeof requestGranoflowApi>>,
  capabilities: Awaited<ReturnType<typeof requestGranoflowApi>>,
  appProcess: Record<string, unknown>,
  warnings: Array<Record<string, unknown>>,
) {
  return {
    configPath: runtime.configPath,
    configExists: runtime.configExists,
    configError: runtime.configError,
    apiBaseUrl: runtime.apiBaseUrl,
    apiBaseUrlSource: runtime.apiBaseUrlSource,
    configuredApiBaseUrl: runtime.configuredApiBaseUrl,
    apiToken: { present: runtime.hasApiToken, source: runtime.apiTokenSource },
    mcp: mcpRuntimeSummary(),
    health: { ...health, appProcess },
    version,
    capabilities: summarizeCapabilities(capabilities),
    warnings,
    nextActions: runtime.configurationShadowedByEnv
      ? [
          "Update or remove GRANOFLOW_API_BASE_URL in the MCP client, then reload that client process.",
        ]
      : warnings.some((warning) => warning.code === "granoflow_app_not_running")
        ? [
            "Ask the user whether they want to open Granoflow.",
            "Call granoflow_setup_open_app with dryRun=true before opening the app.",
          ]
        : warnings.some((warning) => warning.code === "reachable_auth_required")
          ? ["Check GRANOFLOW_API_TOKEN, then call granoflow_setup_status again."]
          : [
              "Verify the Granoflow Local HTTP API is enabled.",
              "Call granoflow_setup_detect_local_api to check bounded localhost candidates.",
            ],
  };
}

export async function getSetupStatus(options: SetupOptions = {}) {
  const env = options.env ?? process.env;
  const runCommandImpl = options.runCommand ?? runCommand;
  const runtime = await resolveMcpRuntime(env);
  const health = await requestGranoflowApi({ path: "/v1/health" }, env);
  const version = await requestGranoflowApi({ path: "/v1/version" }, env);
  const capabilities = await requestGranoflowApi({ path: "/v1/capabilities" }, env);
  const warnings: Array<Record<string, unknown>> = [];
  const appProcess = isLocalApiBaseUrl(runtime.apiBaseUrl)
    ? await checkGranoflowProcess(runCommandImpl)
    : {
        checked: false,
        running: null,
        reason: "Process check is only run for local API base URLs.",
      };
  if (runtime.configurationShadowedByEnv) {
    warnings.push({
      code: "configuration_shadowed_by_env",
      message: "GRANOFLOW_API_BASE_URL overrides the saved MCP config value.",
      configuredApiBaseUrl: runtime.configuredApiBaseUrl,
      effectiveApiBaseUrl: runtime.apiBaseUrl,
      effectiveSource: runtime.apiBaseUrlSource,
      configPath: runtime.configPath,
      nextActions: [
        "Update or remove GRANOFLOW_API_BASE_URL in the MCP client, then reload that client process.",
      ],
    });
  }

  if (!health.ok && isLocalApiBaseUrl(runtime.apiBaseUrl)) {
    if (health.code === "reachable_auth_required") {
      warnings.push({
        code: "reachable_auth_required",
        message: "The configured Granoflow API is reachable but requires authentication.",
        apiBaseUrl: runtime.apiBaseUrl,
        nextActions: ["Check GRANOFLOW_API_TOKEN, then call granoflow_setup_status again."],
      });
    } else if (appProcess.running === false) {
      warnings.push({
        code: "granoflow_app_not_running",
        message:
          "The configured Granoflow API is local, but the API is unreachable and no Granoflow app process was found.",
        apiBaseUrl: runtime.apiBaseUrl,
        granoflow: GRANOFLOW_INTRODUCTION,
        nextActions: [
          "Ask the user whether they want to open Granoflow.",
          "Call granoflow_setup_open_app with dryRun=true before opening the app.",
        ],
      });
    } else if (appProcess.running === true) {
      warnings.push({
        code: "local_api_unreachable_app_running",
        message:
          "A Granoflow process appears to be running, but the configured local API is unreachable.",
        apiBaseUrl: runtime.apiBaseUrl,
        granoflow: GRANOFLOW_INTRODUCTION,
        nextActions: [
          "Ask the user to verify that the Granoflow Local HTTP API is enabled.",
          "Call granoflow_setup_detect_local_api to check bounded localhost candidates.",
        ],
      });
    }
    return unavailableSetupStatus(runtime, health, version, capabilities, appProcess, warnings);
  }
  return {
    configPath: runtime.configPath,
    configExists: runtime.configExists,
    configError: runtime.configError,
    apiBaseUrl: runtime.apiBaseUrl,
    apiBaseUrlSource: runtime.apiBaseUrlSource,
    configuredApiBaseUrl: runtime.configuredApiBaseUrl,
    apiToken: {
      present: runtime.hasApiToken,
      source: runtime.apiTokenSource,
    },
    mcp: mcpRuntimeSummary(),
    health,
    version,
    capabilities: summarizeCapabilities(capabilities),
    appProcess,
    warnings,
    nextActions: runtime.configurationShadowedByEnv
      ? [
          "Update or remove GRANOFLOW_API_BASE_URL in the MCP client, then reload that client process.",
        ]
      : health.ok
        ? ["Granoflow Local HTTP API is reachable."]
        : [
            "Start Granoflow and enable the Local HTTP API.",
            "Call granoflow_setup_detect_local_api to look for a local Granoflow API.",
          ],
  };
}

export { detectLocalApi } from "./setup-probe.js";

export async function writeSetupConfig(input: WriteConfigInput, options: SetupOptions = {}) {
  const result = await writeMcpConfig(input, options.env);
  if (!result.written) {
    return result;
  }
  return {
    ...result,
    verification: await getSetupStatus(options),
  };
}

export async function openGranoflowApp(input: OpenAppInput = {}, options: SetupOptions = {}) {
  const runCommandImpl = options.runCommand ?? runCommand;
  const appName = input.appName ?? "Granoflow";
  const dryRun = input.dryRun !== false;

  if (process.platform !== "darwin") {
    return {
      ok: false,
      dryRun,
      appName,
      error:
        "Opening the installed Granoflow app is only implemented for macOS in this MCP server.",
      nextActions: ["Open Granoflow manually, then call granoflow_setup_status again."],
    };
  }

  const launchLockPath = options.launchLockPath ?? join(tmpdir(), "granoflow-mcp-app-launch.lock");
  let launchLeaseAcquired = false;
  let retainLaunchLease = false;
  const lease = await prepareLaunchLease(input, dryRun, launchLockPath, options.now ?? Date.now);
  launchLeaseAcquired = lease.acquired;
  if (lease.failure) return lease.failure;

  try {
    const appProcess = await checkGranoflowProcess(runCommandImpl);
    const processFailure = appProcessGuardResult(appProcess, input, dryRun);
    if (processFailure) return processFailure;

    const command = "open";
    const attempts = [
      ...(input.appPath ? [{ kind: "path", args: [input.appPath] }] : []),
      { kind: "path", args: ["/Applications/granoflow.app"] },
      { kind: "path", args: ["/Applications/Granoflow.app"] },
      { kind: "appName", args: ["-a", appName] },
      { kind: "appName", args: ["-a", "granoflow"] },
    ];
    if (dryRun) {
      return {
        ok: true,
        dryRun,
        appName,
        appPath: input.appPath ?? null,
        command,
        attempts,
        nextActions: [
          "Ask the user to confirm opening Granoflow.",
          "Call this tool again with dryRun=false only after the user approves.",
        ],
      };
    }

    const results = await executeAppOpenAttempts(attempts, runCommandImpl);
    if (results.some((result) => result.exitCode === 0)) {
      retainLaunchLease = true;
      return {
        ok: true,
        dryRun,
        appName,
        appPath: input.appPath ?? null,
        command,
        attempts: results,
        launchLeaseMs: APP_LAUNCH_LEASE_MS,
        nextActions: [
          "Wait briefly for Granoflow to start, then call granoflow_setup_status again.",
        ],
      };
    }

    return {
      ok: false,
      dryRun,
      appName,
      appPath: input.appPath ?? null,
      command,
      attempts: results,
      nextActions: ["Open Granoflow manually, then call granoflow_setup_status again."],
    };
  } finally {
    if (launchLeaseAcquired && !retainLaunchLease) {
      await releaseAppLaunchLease(launchLockPath);
    }
  }
}

export async function openSetupConfig(
  input: { createIfMissing?: boolean; open?: boolean } = {},
  options: SetupOptions = {},
) {
  const env = options.env ?? process.env;
  const configPath = getMcpConfigPath(env);
  const exists = await configFileExists(configPath);
  let created = false;

  if (!exists && input.createIfMissing !== false) {
    await mkdir(dirname(configPath), { recursive: true });
    await writeFile(
      configPath,
      `${JSON.stringify({ apiBaseUrl: "http://127.0.0.1:56789" }, null, 2)}\n`,
      { mode: 0o600 },
    );
    created = true;
  }

  const readResult = await readMcpConfig(env);
  const openResult = input.open === true ? await openPath(configPath) : { attempted: false };

  return {
    configPath,
    exists: readResult.exists,
    created,
    open: openResult,
    configError: readResult.error,
    nextActions: [
      "Edit apiBaseUrl if the default is wrong.",
      "Keep GRANOFLOW_API_TOKEN in the MCP client environment, not in this config file.",
      "Call granoflow_setup_status after saving changes.",
    ],
  };
}
