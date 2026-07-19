import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-task-lifecycle", () => {
  it("lists tasks filtered by tag query param", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/tasks?tag=custom_ai") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [{ id: "task-ai", title: "AI work", tags: ["custom_ai"] }],
            },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_list")?.({ tag: "custom_ai" });
    const parsed = parseToolText(result) as { ok: boolean; data: { data?: { items?: unknown[] } } };
    expect(parsed.ok).toBe(true);
    const items = parsed.data.data?.items ?? parsed.data.items;
    expect(items).toEqual([expect.objectContaining({ id: "task-ai" })]);
  });

  it("fetches review card draft schema from the Local HTTP API", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/review-card-drafts/schema") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              capability: "review_card_draft_schema_v1",
              cardTypes: [{ cardType: "basic_qa" }],
            },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_review_card_draft_schema")?.({});
    const parsed = parseToolText(result) as {
      ok: boolean;
      data: { data?: { capability?: string } };
    };
    expect(parsed.ok).toBe(true);
    expect(
      parsed.data.data?.capability ?? (parsed.data as { capability?: string }).capability,
    ).toBe("review_card_draft_schema_v1");
  });

  it("previews structured task reminder updates through the Local HTTP API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_update_structured")?.({
      taskId: "task-1",
      remindAt: "2026-07-05T10:10:00.000",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/tasks/task-1",
        body: {
          remindAt: "2026-07-05T10:10:00.000",
        },
      },
    });
  });

  it("preserves status doing for human focus without sending startedAt", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_update_structured")?.({
      taskId: "task-1",
      status: "doing",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/tasks/task-1",
        body: { status: "doing" },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain("startedAt");
  });

  it("previews milestone creation through the Local HTTP API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_create")?.({
      projectId: "project-1",
      title: "First milestone",
      dueAt: "2026-07-08T23:59:59.000",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        path: "/v1/milestones",
        body: {
          projectId: "project-1",
          dueAt: "2026-07-08T23:59:59.000",
        },
      },
    });
  });
});
