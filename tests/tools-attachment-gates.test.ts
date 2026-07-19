import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-attachment-gates", () => {
  it("rejects a relative project design baseline path", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_project_design_baseline_import")?.({
      projectId: "project-1",
      filePath: "project-design-baseline.zip",
      idempotencyKey: "baseline-v1",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsafe_project_design_baseline_path",
    });
  });

  it("blocks completion when no analysis or plan attachment is present", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/tasks/task-1/nodes") {
        response.end(JSON.stringify({ ok: true, data: { items: [] } }));
        return;
      }
      if (request.url === "/v1/tasks/task-1/attachments") {
        response.end(JSON.stringify({ ok: true, data: { items: [] } }));
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_complete")?.({
      taskId: "task-1",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_analysis_plan_attachment_required",
    });
  });

  it("rejects non-Markdown task workflow attachments", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_attachment_add_markdown")?.({
      taskId: "task-1",
      filePath: "/etc/hosts",
      idempotencyKey: "plan-v01",
      expectedTaskUpdatedAt: "2026-07-13T10:00:00.000Z",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsafe_attachment_path",
    });
  });
});
