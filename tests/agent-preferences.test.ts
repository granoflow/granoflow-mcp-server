import { describe, expect, it } from "vitest";
import {
  mergeAgentPreferences,
  parseProjectAgentPreferences,
  resolveAgentPreferences,
} from "../src/agent-preferences.js";

describe("agent preferences", () => {
  it("uses newcomer-safe defaults", () => {
    expect(resolveAgentPreferences()).toMatchObject({
      audience: "beginner",
      explanation: "detailed",
      executionMode: "interactive",
      git: {
        missingNotice: "once",
        workflow: "ask",
        checkpoint: { enabled: false, push: false, taskOwnedFilesOnly: true },
      },
      sources: { explanation: "safe_default", gitWorkflow: "safe_default" },
    });
  });

  it("lets project YAML override local defaults field by field", () => {
    const yaml = [
      "agent_preferences:",
      "  audience: professional",
      "  explanation: concise",
      "  execution_mode: unattended",
      "  git:",
      "    missing_notice: never",
      "    workflow: current_branch",
      "    checkpoint_enabled: true",
    ].join("\n");
    expect(
      resolveAgentPreferences(
        {
          audience: "beginner",
          explanation: "detailed",
          git: { workflow: "develop", checkpoint: { enabled: false } },
        },
        yaml,
      ),
    ).toMatchObject({
      audience: "professional",
      explanation: "concise",
      executionMode: "unattended",
      git: {
        missingNotice: "never",
        workflow: "current_branch",
        checkpoint: { enabled: true, push: false },
      },
      sources: {
        audience: "project",
        explanation: "project",
        gitWorkflow: "project",
        gitCheckpoint: "project",
      },
    });
  });

  it("ignores invalid values instead of weakening safe defaults", () => {
    expect(
      resolveAgentPreferences({
        explanation: "silent",
        git: { workflow: "force_push", checkpoint: { enabled: "yes" } },
      }),
    ).toMatchObject({
      explanation: "detailed",
      git: { workflow: "ask", checkpoint: { enabled: false, push: false } },
    });
  });

  it("parses only an explicit agent_preferences section", () => {
    expect(parseProjectAgentPreferences("interaction_style:\n  explanation: concise")).toEqual({});
  });

  it("merges a partial update without erasing sibling Git settings", () => {
    expect(
      mergeAgentPreferences(
        { explanation: "detailed", git: { workflow: "develop", checkpoint: { enabled: false } } },
        { explanation: "concise", git: { checkpoint: { enabled: true } } },
      ),
    ).toMatchObject({
      explanation: "concise",
      git: { workflow: "develop", checkpoint: { enabled: true } },
    });
  });
});
