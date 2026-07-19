import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-merge-and-setup", () => {
  it("forwards final Experience merge and Knowledge control payload contracts", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/capabilities") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              resources: {
                experience: ["merge-apply"],
                "knowledge-materialization": ["control-preview"],
              },
            },
          }),
        );
        return;
      }
      requested.push({
        method: request.method,
        url: request.url,
        body: await readJsonBody(request),
      });
      response.end(JSON.stringify({ ok: true, data: { forwarded: true } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    await handlers.get("granoflow_experience_merge_apply")?.({
      canonicalExperienceId: "canonical-1",
      mergedExperienceId: "merged-1",
      expectedCanonicalRevision: 2,
      expectedMergedRevision: 3,
      previewHash: "hash-1",
      confirmed: true,
    });
    await handlers.get("granoflow_knowledge_control_preview")?.({
      materializationId: "knowledge-1",
      status: "verified",
      evidence: { readback: "ok" },
    });

    expect(requested).toEqual([
      {
        method: "POST",
        url: "/v1/experiences/canonical-1/merge/apply",
        body: {
          expectedCanonicalRevision: 2,
          expectedMergedRevision: 3,
          previewHash: "hash-1",
          confirmed: true,
          mergedId: "merged-1",
        },
      },
      {
        method: "POST",
        url: "/v1/knowledge-materializations/control/preview",
        body: {
          materializationId: "knowledge-1",
          status: "verified",
          evidence: { readback: "ok" },
        },
      },
    ]);
  });

  it("previews a persistent custom Local API port without writing", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_setup_write_config")?.({
      apiPort: 61_234,
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "ok",
      dryRun: true,
      written: false,
      proposedApiBaseUrl: "http://127.0.0.1:61234",
      effectiveApiBaseUrl: "http://127.0.0.1:61234",
      effectiveSource: "config",
      targetScope: "local",
    });
  });
});
