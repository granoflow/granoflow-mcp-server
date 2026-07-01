import { spawn } from "node:child_process";

export interface CliResult {
  exitCode: number;
  stdout: string;
  stderr: string;
  json: unknown;
}

export interface CliRunnerOptions {
  command?: string;
  env?: NodeJS.ProcessEnv;
  timeoutMs?: number;
}

const DEFAULT_TIMEOUT_MS = 60_000;

const FORBIDDEN_ARGS = new Set(["backup"]);

export function resolveCliCommand(env: NodeJS.ProcessEnv = process.env): string {
  return env.GRANOFLOW_CLI_PATH || "granoflow";
}

export function normalizeCliArgs(args: string[]): string[] {
  if (args.length === 0) {
    return ["--json", "help"];
  }
  if (FORBIDDEN_ARGS.has(args[0] ?? "")) {
    throw new Error("The MCP server does not expose offline backup encrypt/decrypt commands.");
  }
  return args.includes("--json") ? args : ["--json", ...args];
}

export async function runGranoflowCli(
  args: string[],
  input?: unknown,
  options: CliRunnerOptions = {},
): Promise<CliResult> {
  const command = options.command ?? resolveCliCommand(options.env);
  const normalizedArgs = normalizeCliArgs(args);
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;

  return await new Promise<CliResult>((resolve, reject) => {
    const child = spawn(command, normalizedArgs, {
      env: { ...process.env, ...options.env },
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";
    let settled = false;

    const timer = setTimeout(() => {
      if (settled) {
        return;
      }
      settled = true;
      child.kill("SIGTERM");
      reject(new Error(`granoflow CLI timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk: string) => {
      stderr += chunk;
    });
    child.on("error", (error) => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timer);
      reject(error);
    });
    child.on("close", (exitCode) => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timer);
      let json: unknown = null;
      try {
        json = stdout.trim() ? JSON.parse(stdout) : null;
      } catch {
        json = null;
      }
      resolve({
        exitCode: exitCode ?? 1,
        stdout,
        stderr,
        json,
      });
    });

    if (input === undefined) {
      child.stdin.end();
    } else {
      child.stdin.end(JSON.stringify(input));
    }
  });
}

export function resultToText(result: CliResult): string {
  if (result.json !== null) {
    return JSON.stringify(result.json, null, 2);
  }
  const parts = [result.stdout.trim(), result.stderr.trim()].filter(Boolean);
  return parts.join("\n\n") || `granoflow exited with code ${result.exitCode}`;
}
