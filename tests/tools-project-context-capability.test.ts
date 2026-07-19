import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-project-context-capability", () => {
  it("requires project context attachment capability before reading YAML", async () => {
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

    const result = await handlers.get("granoflow_project_context_attachment_read")?.({
      projectId: "project-1",
      attachment: "snapshot",
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "granoflow_project_context_attachments_v1",
        endpoint: "/v1/ai-agent/project-context-attachments/read",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("forwards project context attachment read after capability confirmation", async () => {
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
                  toolId: "granoflow_project_context_attachments_v1",
                  enabled: true,
                  capabilities: {
                    fullReadRequiresExplicitIntent: true,
                    freshnessCheck: true,
                    incrementalReconcile: true,
                    consistencySafety: {
                      rulesAndWordingConflicts: "proposal_required",
                      secretOrPrivacyRisk: "fail_closed",
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/project-context-attachments/read") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              status: "fresh",
              contentReturned: false,
              matchedSections: ["summary"],
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

    const result = await handlers.get("granoflow_project_context_attachment_read")?.({
      projectId: "project-1",
      attachment: "rules",
      query: "copy",
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        data: {
          status: "fresh",
          contentReturned: false,
        },
      },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/project-context-attachments/read",
        body: {
          projectId: "project-1",
          attachment: "rules",
          query: "copy",
          allowFullRead: false,
        },
      },
    ]);
  });
});
