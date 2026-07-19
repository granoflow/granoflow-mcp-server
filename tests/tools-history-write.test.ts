import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-history-write", () => {
  it("requires the historical task mutation capability before writing", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [{ toolId: "granoflow_task_history_mutate", enabled: true }],
            },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "softDelete",
          taskId: "task-1",
          reason: "Remove duplicate historical import.",
        },
      ],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "historical_task_mutations_v1",
        endpoint: "/v1/ai-agent/tasks/historical-mutations",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("writes historical task mutations only after capability confirmation", async () => {
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
                  toolId: "granoflow_task_history_mutate",
                  enabled: true,
                  capabilities: {
                    historicalTaskMutations: {
                      enabled: true,
                      capability: "historical_task_mutations_v1",
                      preservesHistoricalTimes: true,
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/tasks/historical-mutations") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            code: "historical_task_mutations_applied",
            data: { results: [{ clientMutationId: "mutation-1", ok: true }] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      source: { kind: "test" },
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "update",
          taskId: "task-1",
          fields: { startedAt: "2026-06-30T10:00:00.000" },
          reason: "Restore true start time.",
        },
      ],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "historical_task_mutations_applied",
      data: { results: [{ clientMutationId: "mutation-1", ok: true }] },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/tasks/historical-mutations",
        body: {
          dryRun: false,
          source: { kind: "test" },
          mutations: [
            {
              clientMutationId: "mutation-1",
              op: "update",
              taskId: "task-1",
              fields: { startedAt: "2026-06-30T10:00:00.000" },
              reason: "Restore true start time.",
            },
          ],
        },
      },
    ]);
  });
});
