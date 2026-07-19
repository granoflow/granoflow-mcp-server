import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-memory-capability", () => {
  it("requires memory_batch_preview_v1 before calling memory batch preview", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { tools: [{ toolId: "granoflow_context_pack_v1", enabled: true }] },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_memory_batch_preview")?.({
      items: [{ title: "Add batch memory preview" }],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "memory_batch_preview_v1",
        endpoint: "/v1/ai-agent/memory-batches/preview",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("forwards memory batch preview after capability confirmation", async () => {
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
                  toolId: "granoflow_memory_batch_preview_v1",
                  enabled: true,
                  capabilities: {
                    memoryBatchPreview: {
                      capability: "memory_batch_preview_v1",
                      maxItems: 20,
                      writesPerformed: false,
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/memory-batches/preview") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            data: { previewMode: "server_side", writesPerformed: false, items: [] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_memory_batch_preview")?.({
      target: { projectId: "project-1" },
      items: [{ title: "Add batch memory preview" }],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        data: {
          previewMode: "server_side",
          writesPerformed: false,
        },
      },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/memory-batches/preview",
        body: {
          target: { projectId: "project-1" },
          items: [{ title: "Add batch memory preview" }],
          dryRun: true,
        },
      },
    ]);
  });
});
