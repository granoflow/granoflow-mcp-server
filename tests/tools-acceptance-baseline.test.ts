import { createHash } from "node:crypto";
import { writeFile } from "node:fs/promises";
import { mkdtemp } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  readJsonBody,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-acceptance-baseline", () => {
  it("accepts self-contained HTML only for the acceptance report slot", async () => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-acceptance-"));
    const filePath = join(dir, "acceptance-report.html");
    await writeFile(filePath, "<!doctype html><title>Accepted evidence</title>", "utf8");
    const requests: Array<{ url?: string; body: unknown }> = [];
    const port = await startServer(async (request, response) => {
      requests.push({
        url: request.url,
        body: request.method === "GET" ? null : await readJsonBody(request),
      });
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/capabilities") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              resources: {
                task: ["attachment.conditional-add", "attachment.read-content-hash"],
              },
            },
          }),
        );
        return;
      }
      response.end(JSON.stringify({ ok: true, data: { entity: { id: "report-1" } } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    await handlers.get("granoflow_logical_attachment_replace")?.({
      entityType: "task",
      entityId: "task-1",
      logicalSlot: "acceptance_report",
      filePath,
      expectedUpdatedAt: "2026-07-18T10:00:00.000Z",
      idempotencyKey: "acceptance-v01",
      visualConfirmed: false,
      dryRun: false,
    });

    expect(requests[1]).toMatchObject({
      url: "/v1/tasks/task-1/attachments",
      body: { logicalSlot: "acceptance_report" },
    });
  });

  it("forwards explicit UI prototype visual confirmation", async () => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-prototype-"));
    const filePath = join(dir, "demo-ui-prototype.zip");
    await writeFile(filePath, Buffer.from("deterministic-zip-fixture"));
    const requests: Array<{ url?: string; body: unknown }> = [];
    const port = await startServer(async (request, response) => {
      requests.push({
        url: request.url,
        body: request.method === "GET" ? null : await readJsonBody(request),
      });
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/capabilities") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              resources: {
                project: ["attachment.conditional-add", "attachment.read-content-hash"],
              },
            },
          }),
        );
        return;
      }
      response.end(JSON.stringify({ ok: true, data: { entity: { id: "prototype-1" } } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    await handlers.get("granoflow_logical_attachment_replace")?.({
      entityType: "project",
      entityId: "project-1",
      logicalSlot: "ui_prototype",
      filePath,
      expectedUpdatedAt: "2026-07-17T10:00:00.000Z",
      idempotencyKey: "prototype-v01",
      visualConfirmed: true,
      dryRun: false,
    });

    expect(requests[1]).toMatchObject({
      url: "/v1/projects/project-1/attachments",
      body: {
        logicalSlot: "ui_prototype",
        visualConfirmed: true,
      },
    });
  });

  it("imports and reads one exact App-owned project design baseline", async () => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-design-baseline-"));
    const filePath = join(dir, "project-design-baseline.zip");
    const bytes = Buffer.from("deterministic-project-design-baseline");
    await writeFile(filePath, bytes);
    const requests: Array<{ url?: string; body: unknown }> = [];
    const port = await startServer(async (request, response) => {
      requests.push({ url: request.url, body: await readJsonBody(request) });
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, data: { current: true } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    await handlers.get("granoflow_project_design_baseline_import")?.({
      projectId: "project-1",
      filePath,
      idempotencyKey: "baseline-v1",
      dryRun: false,
    });
    const packageSha256 = createHash("sha256").update(bytes).digest("hex");
    await handlers.get("granoflow_project_design_baseline_read")?.({
      projectId: "project-1",
      prototypeId: "prototype-1",
      versionId: "version-1",
      expectedPackageSha256: packageSha256,
    });

    expect(requests[0]).toMatchObject({
      url: "/v1/ai-agent/project-design-baseline/import",
      body: {
        projectId: "project-1",
        displayName: "project-design-baseline.zip",
        packageBase64: bytes.toString("base64"),
        expectedPackageSha256: packageSha256,
        idempotencyKey: "baseline-v1",
      },
    });
    expect(requests[1]).toMatchObject({
      url: "/v1/ai-agent/project-design-baseline/read",
      body: {
        projectId: "project-1",
        prototypeId: "prototype-1",
        versionId: "version-1",
        expectedPackageSha256: packageSha256,
      },
    });
  });
});
