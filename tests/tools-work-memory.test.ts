import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-work-memory", () => {
  it("previews controlled work-memory write endpoints without writing", async () => {
    const { handlers } = collectHandlers();

    const taskResult = await handlers.get("granoflow_task_completion_record")?.({
      repo: "granoflow/mcp-server",
      title: "Fix flaky CI",
      summary: "Fixed cache race.",
      outcome: "success",
      decisions: ["Use isolated cache."],
      dryRun: true,
    });
    const cardResult = await handlers.get("granoflow_review_card_record")?.({
      title: "CI cache race",
      problem: "Shared cache caused flaky CI.",
      solution: "Use isolated cache.",
      tags: ["ci"],
      dryRun: true,
    });

    expect(parseToolText(taskResult)).toMatchObject({
      code: "dry_run",
      data: { path: "/v1/ai-agent/task-completions" },
    });
    expect(parseToolText(cardResult)).toMatchObject({
      code: "dry_run",
      data: { path: "/v1/ai-agent/review-cards" },
    });
  });

  it("forwards controlled work-memory write endpoints after capability confirmation", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        requested.push({ method: request.method, url: request.url });
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [
                {
                  toolId: "granoflow_context_pack_v1",
                  enabled: true,
                  capabilities: {
                    contextPack: {
                      capability: "context_pack_v1",
                      matchSignals: true,
                      recommendations: false,
                      embeddingScores: false,
                    },
                    controlledWrites: {
                      taskCompletion: true,
                      reviewCard: "controlled_import_or_fail_closed",
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (
        request.url === "/v1/ai-agent/task-completions" ||
        request.url === "/v1/ai-agent/review-cards"
      ) {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            data: { status: "forwarded" },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    await handlers.get("granoflow_task_completion_record")?.({
      repo: "granoflow/mcp-server",
      title: "Fix flaky CI",
      summary: "Fixed cache race.",
      outcome: "success",
      decisions: ["Use isolated cache."],
      source: { taskId: "task-1", threadId: "thread-1" },
      dryRun: false,
    });
    await handlers.get("granoflow_review_card_record")?.({
      title: "CI cache race",
      problem: "Shared cache caused flaky CI.",
      solution: "Use isolated cache.",
      tags: ["ci"],
      source: { taskId: "task-1" },
      dryRun: false,
    });

    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/task-completions",
        body: {
          repo: "granoflow/mcp-server",
          title: "Fix flaky CI",
          summary: "Fixed cache race.",
          decisions: ["Use isolated cache."],
          outcome: "success",
          client: "mcp",
          source: { taskId: "task-1", threadId: "thread-1" },
        },
      },
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/review-cards",
        body: {
          title: "CI cache race",
          problem: "Shared cache caused flaky CI.",
          solution: "Use isolated cache.",
          tags: ["ci"],
          client: "mcp",
          source: { taskId: "task-1" },
        },
      },
    ]);
  });
});
