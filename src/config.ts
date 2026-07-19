import { mkdir, open, readFile, rename, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { mergeAgentPreferences, type AgentPreferencesOverride } from "./agent-preferences.js";

export interface GranoflowMcpConfig {
  apiBaseUrl?: string;
  dailyReviewSuggestionLastShownDate?: string;
  agentPreferences?: AgentPreferencesOverride;
  gitMissingNoticeShown?: boolean;
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
  apiBaseUrl: string;
  apiBaseUrlSource: "env" | "config" | "default";
  configuredApiBaseUrl?: string;
  configurationShadowedByEnv: boolean;
  hasApiToken: boolean;
  apiTokenSource: "env" | "none";
  apiToken?: string;
}

export interface WriteConfigInput {
  apiBaseUrl?: string;
  apiPort?: number;
  agentPreferences?: AgentPreferencesOverride;
  gitMissingNoticeShown?: boolean;
  dryRun?: boolean;
}

export interface WriteConfigResult {
  code: "ok" | "configuration_shadowed_by_env";
  configPath: string;
  dryRun: boolean;
  written: boolean;
  backupPath: string | null;
  previousConfig: Record<string, unknown>;
  nextConfig: Record<string, unknown>;
  changedKeys: string[];
  proposedApiBaseUrl?: string;
  persistedApiBaseUrl?: string;
  effectiveApiBaseUrl: string;
  effectiveSource: RuntimeResolution["apiBaseUrlSource"];
  targetScope: "local" | "remote";
  shadowedByEnv: boolean;
  nextActions: string[];
}

export interface DailyReviewSuggestion {
  code: "daily_review_suggested";
  date: string;
  thresholdLocalTime: "16:30";
  message: string;
  messageZh: string;
  nextActions: string[];
  weeklyReviewSuggestion?: WeeklyReviewSuggestion;
  monthlyReviewSuggestion?: MonthlyReviewSuggestion;
}

export interface WeeklyReviewSuggestion {
  code: "weekly_review_suggested";
  weekStart?: string;
  weekEnd?: string;
  target: "this_week" | "last_week";
  checkedDate: string;
  message: string;
  messageZh: string;
  nextActions: string[];
}

export interface MonthlyReviewSuggestion {
  code: "monthly_review_suggested";
  year?: number;
  month?: number;
  target: "this_month" | "last_month";
  checkedDate: string;
  message: string;
  messageZh: string;
  nextActions: string[];
}

const SECRET_KEY_PATTERN = /(token|secret|password|credential|key)/i;
const DEFAULT_API_BASE_URL = "http://127.0.0.1:56789";

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function validateApiBaseUrl(apiBaseUrl: string): void {
  const url = new URL(apiBaseUrl);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("apiBaseUrl must use http or https.");
  }
  if (url.username || url.password) {
    throw new Error("apiBaseUrl must not contain credentials.");
  }
}

function apiTargetScope(apiBaseUrl: string): WriteConfigResult["targetScope"] {
  const hostname = new URL(apiBaseUrl).hostname;
  return ["localhost", "127.0.0.1", "::1", "[::1]"].includes(hostname) ? "local" : "remote";
}

function selectedApiBaseUrl(input: WriteConfigInput): string | undefined {
  if (input.apiBaseUrl !== undefined && input.apiPort !== undefined) {
    throw new Error("Provide apiBaseUrl or apiPort, not both.");
  }
  if (input.apiPort !== undefined) {
    if (!Number.isInteger(input.apiPort) || input.apiPort < 1 || input.apiPort > 65_535) {
      throw new Error("apiPort must be an integer between 1 and 65535.");
    }
    return `http://127.0.0.1:${input.apiPort}`;
  }
  return input.apiBaseUrl;
}

function stableJson(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function localDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function isAfterDailyReviewThreshold(date: Date): boolean {
  const minutes = date.getHours() * 60 + date.getMinutes();
  return minutes >= 16 * 60 + 30;
}

async function writeConfigFile(configPath: string, config: GranoflowMcpConfig): Promise<void> {
  await mkdir(dirname(configPath), { recursive: true });
  const tempPath = `${configPath}.tmp-${process.pid}`;
  await writeFile(tempPath, stableJson(config), { mode: 0o600 });
  await rename(tempPath, configPath);
  const handle = await open(configPath, "r+");
  await handle.chmod(0o600);
  await handle.close();
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
    (typeof config.apiBaseUrl === "string" ? config.apiBaseUrl : undefined) ??
    DEFAULT_API_BASE_URL;
  const configuredApiBaseUrl =
    typeof config.apiBaseUrl === "string" ? config.apiBaseUrl : undefined;

  return {
    configPath: configResult.configPath,
    configExists: configResult.exists,
    configError: configResult.error,
    apiBaseUrl,
    apiBaseUrlSource: env.GRANOFLOW_API_BASE_URL
      ? "env"
      : typeof config.apiBaseUrl === "string"
        ? "config"
        : "default",
    configuredApiBaseUrl,
    configurationShadowedByEnv: Boolean(
      env.GRANOFLOW_API_BASE_URL &&
      configuredApiBaseUrl &&
      env.GRANOFLOW_API_BASE_URL !== configuredApiBaseUrl,
    ),
    hasApiToken: Boolean(env.GRANOFLOW_API_TOKEN),
    apiTokenSource: env.GRANOFLOW_API_TOKEN ? "env" : "none",
    apiToken: env.GRANOFLOW_API_TOKEN,
  };
}

export async function writeMcpConfig(
  input: WriteConfigInput,
  env: NodeJS.ProcessEnv = process.env,
): Promise<WriteConfigResult> {
  const apiBaseUrl = selectedApiBaseUrl(input);
  if (apiBaseUrl !== undefined) {
    validateApiBaseUrl(apiBaseUrl);
  }
  const readResult = await readMcpConfig(env);
  const nextConfig: GranoflowMcpConfig = { ...readResult.config };
  if (apiBaseUrl !== undefined) {
    nextConfig.apiBaseUrl = apiBaseUrl;
  }
  if (input.agentPreferences !== undefined) {
    nextConfig.agentPreferences = mergeAgentPreferences(
      readResult.config.agentPreferences,
      input.agentPreferences,
    );
  }
  if (input.gitMissingNoticeShown !== undefined) {
    nextConfig.gitMissingNoticeShown = input.gitMissingNoticeShown;
  }

  const previousConfig = redactConfig(readResult.config);
  const redactedNextConfig = redactConfig(nextConfig);
  const changedKeys = Object.keys(redactedNextConfig).filter(
    (key) => JSON.stringify(previousConfig[key]) !== JSON.stringify(redactedNextConfig[key]),
  );
  const dryRun = input.dryRun !== false;
  const currentApiBaseUrl =
    typeof readResult.config.apiBaseUrl === "string" ? readResult.config.apiBaseUrl : undefined;
  const proposedApiBaseUrl =
    typeof nextConfig.apiBaseUrl === "string" ? nextConfig.apiBaseUrl : undefined;
  const shadowedByEnv = Boolean(
    env.GRANOFLOW_API_BASE_URL && proposedApiBaseUrl !== env.GRANOFLOW_API_BASE_URL,
  );
  const effectiveApiBaseUrl =
    env.GRANOFLOW_API_BASE_URL ?? proposedApiBaseUrl ?? DEFAULT_API_BASE_URL;
  const effectiveSource: RuntimeResolution["apiBaseUrlSource"] = env.GRANOFLOW_API_BASE_URL
    ? "env"
    : proposedApiBaseUrl
      ? "config"
      : "default";
  const resultState = (persistedApiBaseUrl: string | undefined) => ({
    code: shadowedByEnv ? ("configuration_shadowed_by_env" as const) : ("ok" as const),
    proposedApiBaseUrl,
    persistedApiBaseUrl,
    effectiveApiBaseUrl,
    effectiveSource,
    targetScope: apiTargetScope(proposedApiBaseUrl ?? effectiveApiBaseUrl),
    shadowedByEnv,
  });

  if (dryRun) {
    return {
      ...resultState(currentApiBaseUrl),
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

  let backupPath: string | null = null;
  if (readResult.exists) {
    backupPath = `${readResult.configPath}.bak-${new Date().toISOString().replace(/[:.]/g, "-")}`;
    await writeFile(backupPath, stableJson(readResult.config), { mode: 0o600 });
  }

  await writeConfigFile(readResult.configPath, nextConfig);

  return {
    ...resultState(proposedApiBaseUrl),
    configPath: readResult.configPath,
    dryRun,
    written: true,
    backupPath,
    previousConfig,
    nextConfig: redactedNextConfig,
    changedKeys,
    nextActions: [
      "Call granoflow_setup_status to verify the resolved configuration.",
      ...(shadowedByEnv
        ? [
            "Update or remove GRANOFLOW_API_BASE_URL in the MCP client before this config can apply.",
          ]
        : []),
    ],
  };
}

export async function maybeCreateDailyReviewSuggestion(
  env: NodeJS.ProcessEnv = process.env,
  now: Date = new Date(),
  periodicReviewChecker?: (
    kind: "week" | "month",
    date: string,
    target: WeeklyReviewSuggestion["target"] | MonthlyReviewSuggestion["target"],
    env: NodeJS.ProcessEnv,
  ) => Promise<WeeklyReviewSuggestion | MonthlyReviewSuggestion | null>,
): Promise<DailyReviewSuggestion | null> {
  if (!isAfterDailyReviewThreshold(now)) {
    return null;
  }

  const today = localDateKey(now);
  const readResult = await readMcpConfig(env);
  if (readResult.error) {
    return null;
  }
  if (readResult.config.dailyReviewSuggestionLastShownDate === today) {
    return null;
  }

  await writeConfigFile(readResult.configPath, {
    ...readResult.config,
    dailyReviewSuggestionLastShownDate: today,
  });

  const weeklyReviewTarget = weeklyReviewTargetForDate(now);
  let weeklyReviewSuggestion: WeeklyReviewSuggestion | null = null;
  if (periodicReviewChecker && weeklyReviewTarget) {
    try {
      const checked = await periodicReviewChecker(
        "week",
        weeklyReviewCheckDate(now),
        weeklyReviewTarget,
        env,
      );
      weeklyReviewSuggestion = checked?.code === "weekly_review_suggested" ? checked : null;
    } catch {
      weeklyReviewSuggestion = null;
    }
  }
  const monthlyReviewTarget = monthlyReviewTargetForDate(now);
  let monthlyReviewSuggestion: MonthlyReviewSuggestion | null = null;
  if (periodicReviewChecker && monthlyReviewTarget) {
    try {
      const checked = await periodicReviewChecker(
        "month",
        monthlyReviewCheckDate(now),
        monthlyReviewTarget,
        env,
      );
      monthlyReviewSuggestion = checked?.code === "monthly_review_suggested" ? checked : null;
    } catch {
      monthlyReviewSuggestion = null;
    }
  }

  return {
    code: "daily_review_suggested",
    date: today,
    thresholdLocalTime: "16:30",
    message:
      "It is after 16:30. After finishing the current request, consider doing today's Granoflow review: summarize completed work, lessons, and knowledge worth turning into review cards. This reminder appears at most once per day.",
    messageZh:
      "现在已经过了 16:30。完成当前需求后，建议你做一次 Granoflow 今日回顾：整理今天完成的工作、经验教训，以及值得做成复习卡片的知识点。这个提醒每天最多出现一次。",
    nextActions: [
      "Open today's Granoflow review.",
      "Review completed tasks and extract durable lessons.",
      "Turn worthwhile lessons into review cards.",
    ],
    weeklyReviewSuggestion: weeklyReviewSuggestion ?? undefined,
    monthlyReviewSuggestion: monthlyReviewSuggestion ?? undefined,
  };
}

export function weeklyReviewCheckDate(now: Date): string {
  const day = now.getDay();
  if (day === 1) {
    const lastWeek = new Date(now);
    lastWeek.setDate(now.getDate() - 2);
    return localDateKey(lastWeek);
  }
  return localDateKey(now);
}

export function isWeeklyReviewSuggestionDay(now: Date): boolean {
  return [0, 1, 5, 6].includes(now.getDay());
}

export function weeklyReviewTargetForDate(now: Date): WeeklyReviewSuggestion["target"] | null {
  if (!isWeeklyReviewSuggestionDay(now)) {
    return null;
  }
  return now.getDay() === 1 ? "last_week" : "this_week";
}

export function monthlyReviewCheckDate(now: Date): string {
  const monthKey = (date: Date): string =>
    `${date.getFullYear().toString().padStart(4, "0")}-${(date.getMonth() + 1).toString().padStart(2, "0")}`;
  if (now.getDate() === 1) {
    const lastMonth = new Date(now);
    lastMonth.setDate(0);
    return monthKey(lastMonth);
  }
  return monthKey(now);
}

export function isLastDayOfMonth(now: Date): boolean {
  const nextDay = new Date(now);
  nextDay.setDate(now.getDate() + 1);
  return nextDay.getDate() === 1;
}

export function monthlyReviewTargetForDate(now: Date): MonthlyReviewSuggestion["target"] | null {
  if (now.getDate() === 1) {
    return "last_month";
  }
  return isLastDayOfMonth(now) ? "this_month" : null;
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
