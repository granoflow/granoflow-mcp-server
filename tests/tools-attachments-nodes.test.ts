import { writeFile } from "node:fs/promises";
import { mkdtemp } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-attachments-nodes", () => {
  it("forwards and verifies a generated Markdown attachment", async () => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-plan-"));
    const filePath = join(dir, "task-plan-v01.md");
    const markdown = "# Plan\n";
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
      if (request.method === "POST") {
        response.end(JSON.stringify({ ok: true, data: { entity: { id: "attachment-1" } } }));
        return;
      }
      response.end(
        JSON.stringify({
          ok: true,
          data: {
            content: "# Plan\n",
            contentSha256: "c3964bb3b70a957ec9b233c7dd3653f6ba17701ab00facf88ae1393dc6155577",
          },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    await handlers.get("granoflow_task_attachment_add_markdown")?.({
      taskId: "task-1",
      filePath,
      idempotencyKey: "task-plan-v01",
      expectedTaskUpdatedAt: "2026-07-13T10:00:00.000Z",
      dryRun: false,
    });

    expect(requests).toEqual([
      { url: "/v1/capabilities", body: null },
      {
        url: "/v1/tasks/task-1/attachments",
        body: {
          contentBase64: Buffer.from(markdown, "utf8").toString("base64"),
          fileName: "task-plan-v01.md",
          idempotencyKey: "task-plan-v01",
          expectedTaskUpdatedAt: "2026-07-13T10:00:00.000Z",
          expectedContentSha256: "c3964bb3b70a957ec9b233c7dd3653f6ba17701ab00facf88ae1393dc6155577",
        },
      },
      { url: "/v1/tasks/task-1/attachments/attachment-1", body: null },
    ]);
  });

  it("checks task node capability before forwarding a write", async () => {
    const requests: Array<{ url?: string; body: unknown }> = [];
    const port = await startServer(async (request, response) => {
      const body = request.method === "GET" ? null : await readJsonBody(request);
      requests.push({ url: request.url, body });
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/capabilities") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              resources: {
                task: [
                  "node.list",
                  "node.batch-create",
                  "node.update-title",
                  "node.apply-status",
                  "node.delete",
                ],
              },
            },
          }),
        );
        return;
      }
      response.end(JSON.stringify({ ok: true, data: { nodes: [] } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    await handlers.get("granoflow_task_node_batch_create")?.({
      taskId: "task-1",
      idempotencyKey: "plan-v01",
      expectedTaskUpdatedAt: "2026-07-13T09:00:00.000Z",
      nodes: [{ title: "Prepare API" }],
      dryRun: false,
    });

    expect(requests).toEqual([
      { url: "/v1/capabilities", body: null },
      {
        url: "/v1/tasks/task-1/nodes",
        body: {
          idempotencyKey: "plan-v01",
          expectedTaskUpdatedAt: "2026-07-13T09:00:00.000Z",
          nodes: [{ title: "Prepare API" }],
        },
      },
    ]);
  });
});
