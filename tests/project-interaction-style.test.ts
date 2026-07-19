import { describe, expect, it } from "vitest";
import { resolveProjectInteractionStyle } from "../src/project-interaction-style.js";

describe("project interaction style", () => {
  it("defaults missing settings to detailed newcomer guidance", () => {
    expect(resolveProjectInteractionStyle("project-1")).toMatchObject({
      audience: "beginner",
      explanation: "detailed",
      source: "default",
      recordCopy: { audience: "beginner", explanation: "detailed" },
    });
  });

  it("honors a project-only professional concise setting", () => {
    expect(
      resolveProjectInteractionStyle(
        "project-2",
        ["interaction_style:", "  audience: professional", "  explanation: concise"].join("\n"),
      ),
    ).toMatchObject({
      audience: "professional",
      explanation: "concise",
      source: "project",
      recordCopy: { audience: "beginner", explanation: "detailed" },
    });
  });
});
