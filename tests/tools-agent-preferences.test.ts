import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import {
  collectHandlers,
  installToolTestLifecycle,
  parseToolText,
  readJsonBody,
  startServer,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("Agent preference tools", () => {
  it("writes non-secret local defaults and reads them back", async () => {
    const { handlers } = collectHandlers();
    const write = parseToolText(
      await handlers.get("granoflow_agent_preferences_write_defaults")?.({
        preferences: {
          explanation: "concise",
          git: { workflow: "current_branch", checkpoint: { enabled: true } },
        },
        dryRun: false,
      }),
    ) as { data: { readback: { agentPreferences: unknown } } };

    expect(write.data.readback.agentPreferences).toMatchObject({
      explanation: "concise",
      git: { workflow: "current_branch", checkpoint: { enabled: true } },
    });
    const persisted = JSON.parse(
      await readFile(process.env.GRANOFLOW_MCP_CONFIG_PATH!, "utf8"),
    ) as Record<string, unknown>;
    expect(persisted.agentPreferences).toEqual(write.data.readback.agentPreferences);
    expect(JSON.stringify(persisted)).not.toMatch(/token|password|credential/i);
  });

  it("resolves a project override above local defaults", async () => {
    const port = await startServer(async (request, response) => {
      expect(request.url).toBe("/v1/ai-agent/project-context-attachments/read");
      expect(await readJsonBody(request)).toMatchObject({
        projectId: "project-1",
        section: "agent_preferences",
      });
      response.setHeader("content-type", "application/json");
      response.end(
        JSON.stringify({
          ok: true,
          data: {
            content: [
              "agent_preferences:",
              "  explanation: detailed",
              "  git:",
              "    workflow: develop",
              "    checkpoint_enabled: false",
            ].join("\n"),
          },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();
    await handlers.get("granoflow_agent_preferences_write_defaults")?.({
      preferences: {
        explanation: "concise",
        git: { workflow: "current_branch", checkpoint: { enabled: true } },
      },
      dryRun: false,
    });
    const resolved = parseToolText(
      await handlers.get("granoflow_agent_preferences_get")?.({
        projectId: "project-1",
        dryRun: false,
      }),
    ) as { data: { preferences: unknown } };
    expect(resolved.data.preferences).toMatchObject({
      explanation: "detailed",
      git: { workflow: "develop", checkpoint: { enabled: false, push: false } },
      sources: {
        explanation: "project",
        gitWorkflow: "project",
        gitCheckpoint: "project",
      },
    });
  });

  it("stores the one-time no-Git notice marker without repository actions", async () => {
    const { handlers } = collectHandlers();
    const result = parseToolText(
      await handlers.get("granoflow_git_missing_notice_record")?.({
        shown: true,
        dryRun: false,
      }),
    ) as { data: { nextConfig: Record<string, unknown> } };
    expect(result.data.nextConfig.gitMissingNoticeShown).toBe(true);
  });
});
