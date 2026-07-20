import { createHash } from "node:crypto";
import { writeFile } from "node:fs/promises";
import { mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  collectHandlers,
  installToolTestLifecycle,
  readJsonBody,
  startServer,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-task-prototype", () => {
  it("imports and reads one exact App-owned task prototype", async () => {
    const dir = await mkdtemp(join(tmpdir(), "granoflow-task-prototype-"));
    const filePath = join(dir, "demo.granoprototype");
    const bytes = Buffer.from("deterministic-task-prototype");
    await writeFile(filePath, bytes);
    const requests: Array<{ url?: string; body: unknown }> = [];
    const port = await startServer(async (request, response) => {
      requests.push({ url: request.url, body: await readJsonBody(request) });
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, data: { current: true } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;

    const { handlers } = collectHandlers();
    await handlers.get("granoflow_task_prototype_import")?.({
      taskId: "task-1",
      filePath,
      idempotencyKey: "task-prototype-v1",
      dryRun: false,
    });
    const packageSha256 = createHash("sha256").update(bytes).digest("hex");
    await handlers.get("granoflow_task_prototype_read")?.({
      taskId: "task-1",
      prototypeId: "prototype-1",
      versionId: "version-1",
      expectedPackageSha256: packageSha256,
    });

    expect(requests[0]).toMatchObject({
      url: "/v1/ai-agent/task-prototype/import",
      body: {
        taskId: "task-1",
        displayName: "demo.granoprototype",
        packageBase64: bytes.toString("base64"),
        expectedPackageSha256: packageSha256,
        idempotencyKey: "task-prototype-v1",
      },
    });
    expect(requests[1]).toMatchObject({
      url: "/v1/ai-agent/task-prototype/read",
      body: {
        taskId: "task-1",
        prototypeId: "prototype-1",
        versionId: "version-1",
        expectedPackageSha256: packageSha256,
      },
    });
  });
});
