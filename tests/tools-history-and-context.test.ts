import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-history-and-context", () => {
  it("previews historical task mutations through the dedicated AI-agent API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      source: { kind: "test", summary: "Backfill historical task." },
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "create",
          fields: {
            title: "Historical import",
            description:
              "补录已经发生的任务。打个比方，这像把旧收据补进账本。比如，将 7 月 1 日创建的工作保留原始时间。",
            createdAt: "2026-07-01T09:00:00.000",
            startedAt: "2026-06-30T10:00:00.000",
          },
          authoringEvidence: {
            titleIntent: "action_or_outcome",
            plainLanguageReviewed: true,
            analogyExcerpt: "打个比方，这像把旧收据补进账本。",
            exampleExcerpt: "比如，将 7 月 1 日创建的工作保留原始时间。",
          },
          reason: "Import existing work history.",
        },
      ],
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/tasks/historical-mutations",
        body: {
          dryRun: true,
          source: { kind: "test", summary: "Backfill historical task." },
          mutations: [
            expect.objectContaining({
              clientMutationId: "mutation-1",
              op: "create",
              fields: expect.objectContaining({
                createdAt: "2026-07-01T09:00:00.000",
                startedAt: "2026-06-30T10:00:00.000",
              }),
            }),
          ],
        },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain('"authoringEvidence"');
  });

  it("rejects historical create mutations without task authoring evidence", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.statusCode = 500;
      response.end();
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "create",
          fields: {
            title: "补录历史任务",
            description: "补录已经完成的工作。",
          },
        },
      ],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_authoring_quality_failed",
      data: {
        mutationIndex: 0,
        clientMutationId: "mutation-1",
        issues: expect.any(Array),
      },
    });
    expect(requestedUrls).toEqual([]);
  });

  it("previews context-pack requests through the dedicated AI-agent API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_context_pack")?.({
      scope: "repo",
      repo: "granoflow/mcp-server",
      query: "Fix flaky CI",
      limit: 8,
      client: "codex",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/context-pack",
        body: {
          scope: "repo",
          repo: "granoflow/mcp-server",
          query: "Fix flaky CI",
          limit: 8,
          client: "codex",
        },
      },
    });
  });

  it("previews historical task candidate requests through the App-owned API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_historical_task_candidates")?.({
      taskId: "task-current",
      summary: "Fix sync regression",
      limit: 3,
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/tasks/similar-solutions",
        body: {
          taskId: "task-current",
          summary: "Fix sync regression",
          limit: 3,
          client: "mcp",
        },
      },
    });
  });
});
