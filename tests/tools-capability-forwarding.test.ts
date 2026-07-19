import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-capability-forwarding", () => {
  it("forwards exact prototype export controls to the App", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      response.end(
        JSON.stringify({
          ok: true,
          data: { executionAdmission: { allowed: true } },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_export")?.({
      taskId: "task-1",
      includePrototypes: true,
      assetMode: "file",
      ttlSeconds: 300,
      fetchMissing: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        data: { executionAdmission: { allowed: true } },
      },
    });
    expect(requestedUrls).toEqual([
      "/v1/ai-agent/tasks/task-1/export?includePrototypes=true&assetMode=file&ttlSeconds=300&fetchMissing=true",
    ]);
  });

  it("fails Knowledge Pack closed when the App does not advertise the resource action", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, data: { resources: {} } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_knowledge_pack")?.({
      taskId: "task-1",
      query: "release verification",
      limitPerLane: 5,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        resource: "task-knowledge",
        requiredActions: ["pack"],
      },
    });
    expect(requestedUrls).toEqual(["/v1/capabilities"]);
  });

  it("forwards Knowledge Pack unchanged after capability confirmation", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/capabilities") {
        requested.push({ method: request.method, url: request.url });
        response.end(
          JSON.stringify({
            ok: true,
            data: { resources: { "task-knowledge": ["pack"] } },
          }),
        );
        return;
      }
      requested.push({
        method: request.method,
        url: request.url,
        body: await readJsonBody(request),
      });
      response.end(
        JSON.stringify({
          ok: true,
          data: { writesPerformed: false, lanes: { evidence: {}, experience: {}, knowledge: {} } },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_knowledge_pack")?.({
      taskId: "task-1",
      query: "release verification",
      limitPerLane: 5,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: { data: { writesPerformed: false } },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/capabilities" },
      {
        method: "POST",
        url: "/v1/task-knowledge/task-1/pack",
        body: { query: "release verification", limitPerLane: 5 },
      },
    ]);
  });
});
