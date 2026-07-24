import { describe, expect, it } from "vitest";
import {
  collectHandlers,
  installToolTestLifecycle,
  parseToolText,
  startTaskReadbackServer,
  taskDescriptionImpactReview,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-finish-review", () => {
  it("previews finishing a task as a multi-step dry-run", async () => {
    await startTaskReadbackServer();
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_finish")?.({
      taskId: "task-1",
      projectId: "project-1",
      milestoneId: "milestone-1",
      summary: "Finished with durable learning.",
      startedAt: "2026-07-02T09:00:00.000",
      taskReview: "Done with evidence.",
      reviewCardDrafts: [
        {
          clientCardId: "card-1",
          cardType: "basic_qa",
          front: "What should be remembered?",
          back: "The durable lesson.",
        },
      ],
      endedAt: "2026-07-02T10:15:00.000",
      descriptionImpactReview: taskDescriptionImpactReview("completion_only"),
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        previewMode: "local_request_sequence_only",
        steps: expect.arrayContaining([
          expect.objectContaining({ method: "PATCH", path: "/v1/tasks/task-1" }),
          expect.objectContaining({
            method: "POST",
            path: "/v1/tasks/task-1/complete",
            body: {
              startedAt: "2026-07-02T09:00:00.000",
              endedAt: "2026-07-02T10:15:00.000",
            },
          }),
          expect.objectContaining({
            method: "POST",
            path: "/v1/ai-agent/tasks/import",
            body: expect.objectContaining({
              "agent-id": "granoflow",
              "tool-id": "single_task_ai",
              data: expect.objectContaining({
                task_id: "task-1",
                project_id: "project-1",
                milestone_id: "milestone-1",
                task_review_update: {
                  mode: "replace",
                  content: "Done with evidence.",
                },
                review_card_drafts: [
                  expect.objectContaining({
                    client_card_id: "card-1",
                    card_type: "basic_qa",
                  }),
                ],
              }),
            }),
          }),
          expect.objectContaining({ method: "GET", path: "/v1/tasks" }),
        ]),
        finishGuidance: expect.arrayContaining([
          expect.stringContaining("no Plan nodes"),
          expect.stringContaining("Task Delivery"),
          expect.stringContaining("Do not generate Task Review"),
        ]),
      },
    });
  });

  it("requires project and milestone ids before importing review data", async () => {
    await startTaskReadbackServer();
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_finish")?.({
      taskId: "task-1",
      taskReview: "Worth keeping.",
      descriptionImpactReview: taskDescriptionImpactReview("completion_only"),
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "review_import_context_required",
      data: {
        requiredInput: {
          projectId: "Granoflow project id",
          milestoneId: "Granoflow milestone id",
        },
      },
    });
  });

  it("fails closed on malformed Task Review and Completion Summary markers", async () => {
    const { handlers } = collectHandlers();

    const review = await handlers.get("granoflow_task_review_update")?.({
      taskId: "task-1",
      taskReview: "review_revision: 1\nNo managed markers",
      expectedUpdatedAt: "2026-07-13T10:00:00.000Z",
      dryRun: false,
    });
    const summary = await handlers.get("granoflow_task_completion_summary_update")?.({
      taskId: "task-1",
      description: "<!-- granoflow-task-completion-summary:v1:start -->\nOne-sided summary",
      expectedUpdatedAt: "2026-07-13T10:00:00.000Z",
      dryRun: false,
    });

    expect(parseToolText(review)).toMatchObject({
      ok: false,
      code: "task_review_markers_invalid",
      data: { reason: "missing_marker" },
    });
    expect(parseToolText(summary)).toMatchObject({
      ok: false,
      code: "task_completion_summary_markers_invalid",
      data: { reason: "missing_marker" },
    });
  });
});
