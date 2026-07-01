import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

import {
  configFileExists,
  getMcpConfigPath,
  readMcpConfig,
  resolveMcpRuntime,
  writeMcpConfig,
  type WriteConfigInput,
} from "./config.js";
import { type CliResult, runGranoflowCli } from "./cli.js";

export interface SetupOptions {
  env?: NodeJS.ProcessEnv;
  runCli?: (
    args: string[],
    input?: unknown,
    options?: { env?: NodeJS.ProcessEnv },
  ) => Promise<CliResult>;
  fetch?: typeof fetch;
}

export interface LocalApiDetectionInput {
  ports?: number[];
  timeoutMs?: number;
}

export interface InstallCliInput {
  packageSpec?: string;
  packageManager?: "npm";
  dryRun?: boolean;
}

const DEFAULT_PORTS = [56789, 47631, 38080];
const MAX_PORT_CANDIDATES = 20;
const PROBE_PATHS = ["/health", "/api/capabilities", "/v1/health"];
const GRANOFLOW_JSON_KEYS = ["ok", "status", "capabilities", "tools", "version", "service"];

function safeError(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function getErrorCode(error: unknown): string | undefined {
  return isObject(error) && typeof error.code === "string" ? error.code : undefined;
}

export function isCliMissingError(error: unknown): boolean {
  return getErrorCode(error) === "ENOENT";
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

async function runCommand(
  command: string,
  args: string[],
): Promise<{
  exitCode: number;
  stdout: string;
  stderr: string;
}> {
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

export async function getSetupStatus(options: SetupOptions = {}) {
  const env = options.env ?? process.env;
  const runCli = options.runCli ?? runGranoflowCli;
  const runtime = await resolveMcpRuntime(env);
  let health: Record<string, unknown>;

  try {
    const result = await runCli(["health"], undefined, { env: runtime.env });
    health = {
      ok: result.exitCode === 0,
      exitCode: result.exitCode,
      hasJson: result.json !== null,
      stderr: result.stderr.trim() ? "[present]" : "[empty]",
    };
  } catch (error) {
    health = {
      ok: false,
      cliMissing: isCliMissingError(error),
      error: safeError(error),
    };
  }

  return {
    configPath: runtime.configPath,
    configExists: runtime.configExists,
    configError: runtime.configError,
    cliPath: runtime.cliPath ?? "granoflow",
    cliPathSource: runtime.cliPathSource,
    apiBaseUrl: runtime.apiBaseUrl ?? null,
    apiBaseUrlSource: runtime.apiBaseUrlSource,
    apiToken: {
      present: runtime.hasApiToken,
      source: runtime.apiTokenSource,
    },
    health,
    nextActions:
      health.cliMissing === true
        ? [
            "Ask the user whether they want to install or update granoflow-cli.",
            "Call granoflow_setup_install_or_update_cli with dryRun=true and a packageSpec.",
            "If the CLI is already installed elsewhere, call granoflow_setup_write_config with cliPath.",
          ]
        : runtime.configExists
          ? [
              "If health is not ok, call granoflow_setup_detect_local_api.",
              "Verify the Granoflow app Local HTTP API is enabled.",
            ]
          : [
              "Call granoflow_setup_detect_local_api to look for a local Granoflow API.",
              "Call granoflow_setup_write_config with dryRun=true before writing config.",
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

export async function installOrUpdateCli(input: InstallCliInput = {}, options: SetupOptions = {}) {
  const env = options.env ?? process.env;
  const packageSpec = input.packageSpec ?? env.GRANOFLOW_CLI_INSTALL_SPEC;
  const packageManager = input.packageManager ?? "npm";
  const dryRun = input.dryRun !== false;

  if (!packageSpec) {
    return {
      ok: false,
      dryRun,
      packageManager,
      packageSpec: null,
      error:
        "No granoflow-cli install source is configured. Provide packageSpec or set GRANOFLOW_CLI_INSTALL_SPEC.",
      nextActions: [
        "Confirm the official granoflow-cli install source with the user.",
        "Call this tool with dryRun=true and that packageSpec.",
        "Call again with dryRun=false only after the user approves installation or update.",
      ],
    };
  }

  const command = packageManager;
  const args = ["install", "--global", packageSpec];
  if (dryRun) {
    return {
      ok: true,
      dryRun,
      packageManager,
      packageSpec,
      command,
      args,
      nextActions: [
        "Review the install or update command with the user.",
        "Call this tool again with dryRun=false only after the user approves.",
      ],
    };
  }

  const result = await runCommand(command, args);
  return {
    ok: result.exitCode === 0,
    dryRun,
    packageManager,
    packageSpec,
    command,
    args,
    exitCode: result.exitCode,
    stdout: result.stdout.trim() ? "[present]" : "[empty]",
    stderr: result.stderr.trim() ? "[present]" : "[empty]",
    nextActions:
      result.exitCode === 0
        ? ["Call granoflow_setup_status to verify granoflow-cli is now available."]
        : [
            "Review the packageSpec and package manager availability.",
            "If the CLI installed elsewhere, call granoflow_setup_write_config with cliPath.",
          ],
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
      JSON.stringify({ apiBaseUrl: "http://127.0.0.1:56789", cliPath: "granoflow" }, null, 2) +
        "\n",
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
      "Edit apiBaseUrl or cliPath if the defaults are wrong.",
      "Keep GRANOFLOW_API_TOKEN in the MCP client environment, not in this config file.",
      "Call granoflow_setup_status after saving changes.",
    ],
  };
}
