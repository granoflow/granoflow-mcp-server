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

const DEFAULT_PORTS = [56789, 47631, 38080];
const MAX_PORT_CANDIDATES = 20;
const PROBE_PATHS = ["/health", "/api/capabilities", "/v1/health", "/v1/capabilities"];
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

function validatePorts(ports: number[]): void {
  if (ports.length > MAX_PORT_CANDIDATES) {
    throw new Error(`ports must contain at most ${MAX_PORT_CANDIDATES} candidates.`);
  }
  for (const port of ports) {
    if (!Number.isInteger(port) || port < 1 || port > 65_535) {
      throw new Error("ports must be integers between 1 and 65535.");
    }
  }
}

function hasExplicitGranoflowIdentity(value: unknown): boolean {
  if (!isObject(value)) {
    return false;
  }
  const service = typeof value.service === "string" ? value.service.toLowerCase() : "";
  const product = typeof value.product === "string" ? value.product.toLowerCase() : "";
  return service === "granoflow" || product === "granoflow";
}

function hasGranoflowEnvelope(value: unknown): boolean {
  return isObject(value) && value.ok === true && typeof value.code === "string" && "data" in value;
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

async function fetchWithTimeout(
  fetchImpl: typeof fetch,
  url: string,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchImpl(url, { signal: controller.signal });
  } finally {
    clearTimeout(timer);
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
      health: {
        ...health,
        appProcess,
      },
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

export async function detectLocalApi(
  input: LocalApiDetectionInput = {},
  options: SetupOptions = {},
) {
  const ports = input.ports ?? DEFAULT_PORTS;
  const timeoutMs = input.timeoutMs ?? 300;
  validatePorts(ports);
  const fetchImpl = options.fetch ?? fetch;
  const candidates: Array<Record<string, unknown>> = [];
  const checked: string[] = [];
  let ambiguousServiceCount = 0;

  for (const port of [...new Set(ports)]) {
    const apiBaseUrl = `http://127.0.0.1:${port}`;
    const explicitPaths: string[] = [];
    const envelopePaths: string[] = [];
    const authPaths: string[] = [];
    let jsonResponseCount = 0;
    for (const path of PROBE_PATHS) {
      const url = `${apiBaseUrl}${path}`;
      checked.push(url);
      try {
        const response = await fetchWithTimeout(fetchImpl, url, timeoutMs);
        if (response.status === 401 || response.status === 403) {
          authPaths.push(path);
          continue;
        }
        if (response.status !== 200) {
          continue;
        }
        let json: unknown = null;
        try {
          json = await response.json();
          jsonResponseCount += 1;
        } catch {
          json = null;
        }
        if (hasExplicitGranoflowIdentity(json)) {
          explicitPaths.push(path);
        } else if (hasGranoflowEnvelope(json)) {
          envelopePaths.push(path);
        }
      } catch {
        // Timeouts and connection refusals are expected while probing bounded localhost ports.
      }
    }
    const consistentV1Envelope =
      envelopePaths.includes("/v1/health") && envelopePaths.includes("/v1/capabilities");
    if (explicitPaths.length > 0 || consistentV1Envelope) {
      candidates.push({
        apiBaseUrl,
        path: explicitPaths[0] ?? "/v1/health",
        confidence: "high",
        authRequired: false,
        evidence:
          explicitPaths.length > 0
            ? "HTTP 200 JSON contains explicit Granoflow service identity."
            : "Two fixed v1 endpoints returned consistent Granoflow envelopes.",
      });
    } else if (authPaths.length > 0) {
      candidates.push({
        apiBaseUrl,
        path: authPaths[0],
        confidence: "low",
        authRequired: true,
        evidence: "A fixed candidate path requires authentication; service identity is unverified.",
      });
    } else if (jsonResponseCount > 0) {
      ambiguousServiceCount += 1;
    }
  }

  const highConfidenceCount = candidates.filter(
    (candidate) => candidate.confidence === "high",
  ).length;
  const authRequiredCount = candidates.filter(
    (candidate) => candidate.authRequired === true,
  ).length;
  const candidateState =
    highConfidenceCount === 1
      ? "single_high_confidence"
      : highConfidenceCount > 1
        ? "multiple_high_confidence"
        : authRequiredCount > 0
          ? "auth_required_only"
          : ambiguousServiceCount > 0
            ? "ambiguous_non_granoflow_service"
            : "none";

  return {
    checked,
    candidates,
    candidateState,
    persistenceRecommended: highConfidenceCount > 0,
    nextActions:
      candidateState === "single_high_confidence"
        ? [
            "Preview the candidate, config path, old/new value, and env override in one dry-run.",
            "Ask once for confirmation before writing that exact config.",
          ]
        : candidateState === "multiple_high_confidence"
          ? [
              "Show all high-confidence candidates and ask the user to choose one.",
              "Preview the selected config in dry-run mode before one write confirmation.",
            ]
          : candidateState === "auth_required_only"
            ? [
                "Candidate paths require authentication; verify service identity and GRANOFLOW_API_TOKEN before persisting a URL.",
              ]
            : candidateState === "ambiguous_non_granoflow_service"
              ? [
                  "A local HTTP service responded without Granoflow identity; do not persist it automatically.",
                  "Ask the user for the configured Granoflow port or full URL.",
                ]
              : [
                  "Start Granoflow and enable the Local HTTP API.",
                  "If Granoflow is already running, ask once for its custom port or full URL.",
                ],
  };
}

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
  if (!dryRun) {
    try {
      launchLeaseAcquired = await acquireAppLaunchLease(launchLockPath, options.now ?? Date.now);
    } catch (error) {
      return {
        ok: false,
        code: "granoflow_app_launch_guard_failed",
        dryRun,
        appName,
        appPath: input.appPath ?? null,
        error: `The MCP server could not establish its single-launch guard: ${safeError(error)}`,
        nextActions: [
          "Check local temporary-directory permissions.",
          "Open Granoflow manually only after confirming that no Granoflow instance is running.",
        ],
      };
    }
    if (!launchLeaseAcquired) {
      return {
        ok: false,
        code: "granoflow_app_launch_in_progress",
        dryRun,
        appName,
        appPath: input.appPath ?? null,
        error:
          "Another Granoflow MCP launch request is still in progress, so this request will not inspect or open the app again.",
        nextActions: [
          "Do not open another Granoflow instance.",
          "Wait for the existing launch request, then call granoflow_setup_status.",
        ],
      };
    }
  }

  try {
    const appProcess = await checkGranoflowProcess(runCommandImpl);
    if (appProcess.running === true) {
      return {
        ok: false,
        code: "granoflow_app_already_running",
        dryRun,
        appName,
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
        appName,
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

    const results = [];
    for (const attempt of attempts) {
      const result = await runCommandImpl(command, attempt.args);
      results.push({
        kind: attempt.kind,
        args: attempt.args,
        exitCode: result.exitCode,
        stderr: result.stderr.trim() ? "[present]" : "[empty]",
      });
      if (result.exitCode === 0) {
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
