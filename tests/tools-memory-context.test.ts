import { describe, expect, it } from "vitest";
import { installToolTestLifecycle, parseToolText, collectHandlers } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-memory-context", () => {
  it("previews memory batch preview requests through the dedicated AI-agent API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_memory_batch_preview")?.({
      source: { client: "codex", threadId: "thread-1" },
      target: { projectId: "project-1", milestoneId: "milestone-1" },
      items: [
        {
          clientItemId: "item-1",
          kind: "task_completion",
          title: "Add batch memory preview",
          summary: "Preview before writing.",
          completedAt: "2026-07-07T10:00:00.000Z",
        },
      ],
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/memory-batches/preview",
        body: {
          source: { client: "codex", threadId: "thread-1" },
          target: { projectId: "project-1", milestoneId: "milestone-1" },
          dryRun: true,
          items: [
            expect.objectContaining({
              clientItemId: "item-1",
              title: "Add batch memory preview",
            }),
          ],
        },
      },
    });
  });

  it("previews project context description updates without extra fields", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_project_context_update")?.({
      projectId: "project-1",
      description: "Current state: Granoflow MCP context steward is active.",
      evidenceSummary: "Implemented context steward plan.",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/projects/project-1",
        body: {
          description: "Current state: Granoflow MCP context steward is active.",
        },
        contextSteward: {
          target: "project",
          evidenceSummary: "Implemented context steward plan.",
          descriptionPolicy: "living_context",
        },
      },
    });
  });
});
