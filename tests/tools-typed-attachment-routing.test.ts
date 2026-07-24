import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  collectHandlers,
  installToolTestLifecycle,
  parseToolText,
  readJsonBody,
  startServer,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("typed task attachment routing", () => {
  it.each([
    ["task_work", "execution", "task_work_execution"],
    ["task_work", "post_completion_revision", "task_work_post_completion_revision"],
    ["task_delivery", null, "task_delivery"],
  ])("routes %s to %s", async (documentType, documentSlot, logicalSlot) => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-typed-attachment-"));
    const filePath = join(dir, `${documentType}.md`);
    const markdown = [
      `# ${documentType}`,
      "",
      `document_type: ${documentType}`,
      ...(documentSlot ? [`document_slot: ${documentSlot}`] : []),
      "",
      "## Body",
      "Evidence.",
    ].join("\n");
    await writeFile(filePath, markdown, "utf8");
    const requests: Array<{ url?: string; body: unknown }> = [];
    const port = await startServer(async (request, response) => {
      requests.push({
        url: request.url,
        body: request.method === "GET" ? null : await readJsonBody(request),
      });
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/capabilities") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              resources: {
                task: ["attachment.conditional-add", "attachment.read-content-hash"],
              },
            },
          }),
        );
        return;
      }
      response.end(
        JSON.stringify({
          ok: true,
          code: "logical_attachment_replaced",
          data: { entity: { id: "attachment-1", logicalSlot } },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_attachment_add_markdown")?.({
      taskId: "task-1",
      filePath,
      idempotencyKey: `${documentType}-v1`,
      expectedTaskUpdatedAt: "2026-07-24T10:00:00.000Z",
      dryRun: false,
    });

    expect(requests[1]).toMatchObject({
      url: "/v1/tasks/task-1/attachments",
      body: {
        contentBase64: Buffer.from(markdown, "utf8").toString("base64"),
        logicalSlot,
        expectedUpdatedAt: "2026-07-24T10:00:00.000Z",
      },
    });
    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        transport: "contentBase64",
        localPathRole: "mcp_read_boundary_only",
        route: "logical_attachment_replace",
        logicalSlot,
      },
    });
  });

  it("rejects a typed task work document without a slot before any HTTP request", async () => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-invalid-task-work-"));
    const filePath = join(dir, "task-work.md");
    await writeFile(filePath, "# Work\n\ndocument_type: task_work\n", "utf8");
    const requests: string[] = [];
    const port = await startServer((request, response) => {
      requests.push(request.url);
      response.statusCode = 500;
      response.end();
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_attachment_add_markdown")?.({
      taskId: "task-1",
      filePath,
      idempotencyKey: "task-work-invalid",
      expectedTaskUpdatedAt: "2026-07-24T10:00:00.000Z",
      dryRun: false,
    });

    expect(requests).toEqual([]);
    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_workflow_header_invalid",
      data: { writesPerformed: false },
    });
  });

  it("reads an App-owned task execution snapshot", async () => {
    const requests: string[] = [];
    const port = await startServer((request, response) => {
      requests.push(request.url);
      response.setHeader("content-type", "application/json");
      response.end(
        JSON.stringify({
          ok: true,
          data: {
            schema: "granoflow_task_execution_snapshot_v1",
            task: { id: "task-1", updatedAt: "2026-07-24T10:00:00.000Z" },
            nodes: [],
          },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_execution_snapshot")?.({
      taskId: "task-1",
    });

    expect(requests).toEqual(["/v1/ai-agent/tasks/task-1/execution-snapshot"]);
    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        ok: true,
        data: { schema: "granoflow_task_execution_snapshot_v1" },
      },
    });
  });
});
