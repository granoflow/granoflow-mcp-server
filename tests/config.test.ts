import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

import { describe, expect, it } from "vitest";

import {
  maybeCreateDailyReviewSuggestion,
  readMcpConfig,
  resolveMcpRuntime,
  writeMcpConfig,
} from "../src/config.js";

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

  it("suggests daily review once per local day after 16:30", async () => {
    const configPath = await tempConfigPath("daily-review");
    const env = { GRANOFLOW_MCP_CONFIG_PATH: configPath };

    await expect(
      maybeCreateDailyReviewSuggestion(env, new Date(2026, 6, 3, 16, 29)),
    ).resolves.toBeNull();

    const first = await maybeCreateDailyReviewSuggestion(env, new Date(2026, 6, 3, 16, 30));
    expect(first).toMatchObject({
      code: "daily_review_suggested",
      date: "2026-07-03",
      thresholdLocalTime: "16:30",
      messageZh: expect.stringContaining("今日回顾"),
    });

    await expect(
      maybeCreateDailyReviewSuggestion(env, new Date(2026, 6, 3, 20, 0)),
    ).resolves.toBeNull();

    const nextDay = await maybeCreateDailyReviewSuggestion(env, new Date(2026, 6, 4, 16, 31));
    expect(nextDay).toMatchObject({
      code: "daily_review_suggested",
      date: "2026-07-04",
    });

    const config = (await readMcpConfig(env)).config;
    expect(config.dailyReviewSuggestionLastShownDate).toBe("2026-07-04");
  });

  it("attaches weekly review suggestions only on Friday through Monday", async () => {
    const calls: Array<{ kind: string; date: string; target: string }> = [];
    const checker = async (
      kind: "week" | "month",
      date: string,
      target: "this_week" | "last_week" | "this_month" | "last_month",
    ) => {
      calls.push({ kind, date, target });
      if (kind !== "week") {
        return null;
      }
      return {
        code: "weekly_review_suggested" as const,
        target: target as "this_week" | "last_week",
        checkedDate: date,
        message: "Weekly review missing.",
        messageZh: "每周回顾还没写。",
        nextActions: ["Open weekly review."],
      };
    };

    const thursdayConfigPath = await tempConfigPath("weekly-thursday");
    const thursday = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: thursdayConfigPath },
      new Date(2026, 6, 2, 16, 31),
      checker,
    );
    expect(thursday?.weeklyReviewSuggestion).toBeUndefined();

    const fridayConfigPath = await tempConfigPath("weekly-friday");
    const friday = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: fridayConfigPath },
      new Date(2026, 6, 3, 16, 31),
      checker,
    );
    expect(friday?.weeklyReviewSuggestion).toMatchObject({
      code: "weekly_review_suggested",
      target: "this_week",
      checkedDate: "2026-07-03",
    });

    const saturdayConfigPath = await tempConfigPath("weekly-saturday");
    const saturday = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: saturdayConfigPath },
      new Date(2026, 6, 4, 16, 31),
      checker,
    );
    expect(saturday?.weeklyReviewSuggestion).toMatchObject({
      target: "this_week",
      checkedDate: "2026-07-04",
    });

    const sundayConfigPath = await tempConfigPath("weekly-sunday");
    const sunday = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: sundayConfigPath },
      new Date(2026, 6, 5, 16, 31),
      checker,
    );
    expect(sunday?.weeklyReviewSuggestion).toMatchObject({
      target: "this_week",
      checkedDate: "2026-07-05",
    });

    const mondayConfigPath = await tempConfigPath("weekly-monday");
    const monday = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: mondayConfigPath },
      new Date(2026, 6, 6, 16, 31),
      checker,
    );
    expect(monday?.weeklyReviewSuggestion).toMatchObject({
      code: "weekly_review_suggested",
      target: "last_week",
      checkedDate: "2026-07-04",
    });

    expect(calls).toEqual([
      { kind: "week", date: "2026-07-03", target: "this_week" },
      { kind: "week", date: "2026-07-04", target: "this_week" },
      { kind: "week", date: "2026-07-05", target: "this_week" },
      { kind: "week", date: "2026-07-04", target: "last_week" },
    ]);
  });

  it("attaches monthly review suggestions on month end and month start", async () => {
    const calls: Array<{ kind: string; date: string; target: string }> = [];
    const checker = async (
      kind: "week" | "month",
      date: string,
      target: "this_week" | "last_week" | "this_month" | "last_month",
    ) => {
      calls.push({ kind, date, target });
      if (kind !== "month") {
        return null;
      }
      return {
        code: "monthly_review_suggested" as const,
        target: target as "this_month" | "last_month",
        checkedDate: date,
        message: "Monthly review missing.",
        messageZh: "本月回顾还没写。",
        nextActions: ["Open monthly review."],
      };
    };

    const ordinaryConfigPath = await tempConfigPath("monthly-ordinary");
    const ordinary = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: ordinaryConfigPath },
      new Date(2026, 6, 15, 16, 31),
      checker,
    );
    expect(ordinary?.monthlyReviewSuggestion).toBeUndefined();

    const monthEndConfigPath = await tempConfigPath("monthly-end");
    const monthEnd = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: monthEndConfigPath },
      new Date(2026, 6, 31, 16, 31),
      checker,
    );
    expect(monthEnd?.monthlyReviewSuggestion).toMatchObject({
      code: "monthly_review_suggested",
      target: "this_month",
      checkedDate: "2026-07",
    });

    const monthStartConfigPath = await tempConfigPath("monthly-start");
    const monthStart = await maybeCreateDailyReviewSuggestion(
      { GRANOFLOW_MCP_CONFIG_PATH: monthStartConfigPath },
      new Date(2026, 7, 1, 16, 31),
      checker,
    );
    expect(monthStart?.monthlyReviewSuggestion).toMatchObject({
      code: "monthly_review_suggested",
      target: "last_month",
      checkedDate: "2026-07",
    });

    expect(calls.filter((call) => call.kind === "month")).toEqual([
      { kind: "month", date: "2026-07", target: "this_month" },
      { kind: "month", date: "2026-07", target: "last_month" },
    ]);
  });
});
