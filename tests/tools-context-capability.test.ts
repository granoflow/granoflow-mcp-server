import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-context-capability", () => {
  it("requires context_pack_v1 before calling context-pack endpoints", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { tools: [{ toolId: "single_task_ai", enabled: true }] },
          }),
        );
        return;
      }
      response.statusCode = 500;
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
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "context_pack_v1",
        endpoint: "/v1/ai-agent/context-pack",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });
});
