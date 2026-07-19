import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-task-creation", () => {
  it("rejects historical fields locally on ordinary task update", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.statusCode = 500;
      response.end();
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_update")?.({
      taskId: "task-1",
      input: { startedAt: "2026-07-18T09:00:00.000Z" },
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "historical_fields_not_supported",
      data: { operation: "update", unsupportedFields: ["startedAt"] },
    });
    expect(requestedUrls).toEqual([]);
  });

  it("previews structured task creation through the Local HTTP API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "Ship MCP v0",
      description:
        "Release the package. 打个比方，这像给包裹贴好地址再交给快递。比如，发布后用 npx 安装并验证版本号。",
      authoringEvidence: {
        titleIntent: "action_or_outcome",
        plainLanguageReviewed: true,
        analogyExcerpt: "打个比方，这像给包裹贴好地址再交给快递。",
        exampleExcerpt: "比如，发布后用 npx 安装并验证版本号。",
      },
      remindAt: "2026-07-05T10:05:00.000",
      projectId: "project-1",
      milestoneId: "milestone-1",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        path: "/v1/tasks",
        body: {
          projectId: "project-1",
          remindAt: "2026-07-05T10:05:00.000",
        },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain('"tags"');
    expect(JSON.stringify(parseToolText(result))).not.toContain('"authoringEvidence"');
  });

  it("filters unknown tags before structured task creation", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer(async (request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/tags") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [{ id: "tag-1", slug: "known-tag" }],
            },
          }),
        );
        return;
      }
      if (request.method === "POST" && request.url === "/v1/tasks") {
        const body = await readJsonBody(request);
        response.end(
          JSON.stringify({
            ok: true,
            code: "ok",
            data: { entity: body },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "Tagged task",
      description:
        "保留已知标签。打个比方，这像门卫只放名单上的访客进门。比如，请求中的 known-tag 会保留，unknown-tag 会跳过。",
      authoringEvidence: {
        titleIntent: "action_or_outcome",
        plainLanguageReviewed: true,
        analogyExcerpt: "打个比方，这像门卫只放名单上的访客进门。",
        exampleExcerpt: "比如，请求中的 known-tag 会保留，unknown-tag 会跳过。",
      },
      tags: ["known-tag", "unknown-tag"],
      dryRun: false,
    });

    expect(requestedUrls).toEqual(["/v1/tags", "/v1/tasks"]);
    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        entity: {
          title: "Tagged task",
          tags: ["known-tag"],
        },
        tagFilter: {
          acceptedTags: ["known-tag"],
          skippedTags: [{ slug: "unknown-tag", reason: "unknown_tag" }],
        },
      },
    });
  });
});
