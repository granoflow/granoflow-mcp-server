import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
  taskDescriptionImpactReview,
  writeTaskReadback,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-completion-gates", () => {
  it("refuses a second completion path for a node-backed task", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/tasks/task-1/nodes") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { items: [{ id: "node-1", status: "pending" }] },
          }),
        );
        return;
      }
      if (request.url === "/v1/tasks/task-1") {
        writeTaskReadback(response);
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_complete")?.({
      taskId: "task-1",
      descriptionImpactReview: taskDescriptionImpactReview("completion_only"),
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "node_managed_completion_required",
      data: { completionOwner: "task_node_service", nodeCount: 1 },
    });
    expect(requestedUrls).toEqual(["/v1/tasks/task-1", "/v1/tasks/task-1/nodes"]);
  });

  it("fails fast when enhanced review card fields are not advertised by the app", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [{ toolId: "single_task_ai", enabled: true }],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/tasks/task-1") {
        writeTaskReadback(response);
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_finish")?.({
      taskId: "task-1",
      projectId: "project-1",
      milestoneId: "milestone-1",
      taskReview: "Durable lesson.",
      reviewCardDrafts: [
        {
          clientCardId: "card-1",
          cardType: "basic_qa",
          front: "What is idempotent?",
          back: "A repeated operation has the same durable effect.",
          noteFields: [
            {
              key: "pronunciation",
              label: "Pronunciation",
              type: "text_to_speech",
              value: "idempotent",
              ttsLanguageCode: "en-US",
            },
          ],
          frontLayout: ["front", "pronunciation"],
          backLayout: ["back"],
        },
      ],
      descriptionImpactReview: taskDescriptionImpactReview("completion_only"),
      confirmComplete: true,
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "review_card_draft_note_fields_unsupported",
      data: {
        unsupportedFields: ["noteFields", "frontLayout", "backLayout"],
      },
    });
    expect(requestedUrls).toEqual(["/v1/tasks/task-1", "/v1/ai-agent/tools"]);
  });
});
