import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-resolve-delete", () => {
  it("resolves task candidates without writing data", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      expect(request.method).toBe("GET");
      expect(request.url).toBe("/v1/tasks");
      response.end(
        JSON.stringify({
          ok: true,
          data: {
            items: [
              { id: "task-1", title: "Ship MCP", status: "pending", projectId: "project-1" },
              { id: "task-2", title: "Ship docs", status: "done", projectId: "project-1" },
            ],
          },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_resolve")?.({
      query: "Ship",
      matchMode: "contains",
      projectId: "project-1",
      includeDone: false,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "resolved",
      data: {
        entityType: "task",
        count: 1,
        matches: [expect.objectContaining({ id: "task-1", title: "Ship MCP" })],
      },
    });
  });

  it("previews safe project deletion and reports linked tasks", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/projects") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { items: [{ id: "project-1", title: "Granoflow MCP", status: "pending" }] },
          }),
        );
        return;
      }
      if (request.url === "/v1/tasks") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { items: [{ id: "task-1", title: "Linked", projectId: "project-1" }] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_project_delete")?.({
      projectId: "project-1",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        path: "/v1/projects/project-1",
        impact: {
          resource: { id: "project-1", title: "Granoflow MCP" },
          linkedTaskCount: 1,
        },
      },
    });
  });
});
