import { describe, expect, it } from "vitest";
import { tempConfigPath } from "./config-test-harness.js";
import { maybeCreateDailyReviewSuggestion } from "../src/config.js";

describe("config-month-boundaries", () => {
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
