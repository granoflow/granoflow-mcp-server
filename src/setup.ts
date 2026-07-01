import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

import { requestGranoflowApi } from "./api.js";
import {
  configFileExists,
  getMcpConfigPath,
  readMcpConfig,
  resolveMcpRuntime,
  writeMcpConfig,
  type WriteConfigInput,
} from "./config.js";

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
const PROBE_PATHS = ["/health", "/api/capabilities", "/v1/health"];
const GRANOFLOW_JSON_KEYS = ["ok", "status", "capabilities", "tools", "version", "service"];

function safeError(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
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

function looksLikeGranoflowJson(value: unknown): boolean {
  if (!isObject(value)) {
    return false;
  }
  return GRANOFLOW_JSON_KEYS.some((key) => key in value);
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
    const result = await runCommandImpl("pgrep", ["-ifl", "granoflow"]);
    const matches =
      result.exitCode === 0
        ? result.stdout
            .split("\n")
            .filter(Boolean)
            .filter((line) => !line.toLowerCase().includes("granoflow-mcp-server"))
        : [];
    return {
      checked: true,
      running: matches.length > 0,
      count: matches.length,
      matches: matches.map((line) => line.trim()),
    };
  } catch (error) {
    return {
      checked: false,
      running: null,
      error: safeError(error),
    };
  }
}

export async function getSetupStatus(options: SetupOptions = {}) {
  const env = options.env ?? process.env;
  const runCommandImpl = options.runCommand ?? runCommand;
  const runtime = await resolveMcpRuntime(env);
  const health = await requestGranoflowApi({ path: "/v1/health" }, env);
  const version = await requestGranoflowApi({ path: "/v1/version" }, env);
  const warnings: Array<Record<string, unknown>> = [];
  const appProcess = isLocalApiBaseUrl(runtime.apiBaseUrl)
    ? await checkGranoflowProcess(runCommandImpl)
    : {
        checked: false,
        running: null,
        reason: "Process check is only run for local API base URLs.",
      };

  if (!health.ok && isLocalApiBaseUrl(runtime.apiBaseUrl)) {
    if (appProcess.running === false) {
      warnings.push({
        code: "granoflow_app_not_running",
        message:
          "The configured Granoflow API is local, but the API is unreachable and no Granoflow app process was found.",
        apiBaseUrl: runtime.apiBaseUrl,
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
      apiToken: {
        present: runtime.hasApiToken,
        source: runtime.apiTokenSource,
      },
      health: {
        ...health,
        appProcess,
      },
      version,
      warnings,
      nextActions: warnings.some((warning) => warning.code === "granoflow_app_not_running")
        ? [
            "Ask the user whether they want to open Granoflow.",
            "Call granoflow_setup_open_app with dryRun=true before opening the app.",
          ]
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
    apiToken: {
      present: runtime.hasApiToken,
      source: runtime.apiTokenSource,
    },
    health,
    version,
    appProcess,
    warnings,
    nextActions: health.ok
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

  for (const port of [...new Set(ports)]) {
    for (const path of PROBE_PATHS) {
      const apiBaseUrl = `http://127.0.0.1:${port}`;
      const url = `${apiBaseUrl}${path}`;
      checked.push(url);
      try {
        const response = await fetchWithTimeout(fetchImpl, url, timeoutMs);
        if (response.status === 401 || response.status === 403) {
          candidates.push({
            apiBaseUrl,
            path,
            confidence: "low",
            authRequired: true,
            evidence: `HTTP ${response.status} from fixed Granoflow candidate path.`,
          });
          continue;
        }
        if (response.status !== 200) {
          continue;
        }
        let json: unknown = null;
        try {
          json = await response.json();
        } catch {
          json = null;
        }
        if (looksLikeGranoflowJson(json)) {
          candidates.push({
            apiBaseUrl,
            path,
            confidence: "high",
            authRequired: false,
            evidence: "HTTP 200 JSON contains Granoflow-shaped keys.",
          });
        }
      } catch {
        // Timeouts and connection refusals are expected while probing bounded localhost ports.
      }
    }
  }

  return {
    checked,
    candidates,
    nextActions:
      candidates.length > 0
        ? [
            "Review the candidate API URL.",
            "Call granoflow_setup_write_config with dryRun=true before writing config.",
          ]
        : [
            "Start Granoflow and enable the Local HTTP API.",
            "If Granoflow is already running, open the config manually with granoflow_setup_open_config.",
          ],
  };
}

export async function writeSetupConfig(input: WriteConfigInput, options: SetupOptions = {}) {
  return await writeMcpConfig(input, options.env);
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
      return {
        ok: true,
        dryRun,
        appName,
        appPath: input.appPath ?? null,
        command,
        attempts: results,
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
