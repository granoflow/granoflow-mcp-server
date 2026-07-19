import { describe, expect, it } from "vitest";
import { tempConfigPath } from "./config-test-harness.js";
import { maybeCreateDailyReviewSuggestion, readMcpConfig } from "../src/config.js";

describe("config-daily-review", () => {
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
});
