import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-history-capability", () => {
  it("forwards context-pack requests after capability confirmation", async () => {
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
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/context-pack") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            code: "ok",
            data: { model: "granoflow_task_review_card_context_v1", tasks: [] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_context_pack")?.({
      scope: "repo",
      repo: "granoflow/mcp-server",
      query: "Fix flaky CI",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        model: "granoflow_task_review_card_context_v1",
        tasks: [],
      },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/context-pack",
        body: {
          scope: "repo",
          repo: "granoflow/mcp-server",
          query: "Fix flaky CI",
          limit: 12,
          client: "mcp",
        },
      },
    ]);
  });
});
