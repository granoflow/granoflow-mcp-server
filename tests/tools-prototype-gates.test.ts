import { describe, expect, it } from "vitest";
import { collectHandlers, installToolTestLifecycle, parseToolText } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-prototype-gates", () => {
  it("rejects a relative task prototype path", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_prototype_import")?.({
      taskId: "task-1",
      filePath: "demo.granoprototype",
      idempotencyKey: "task-prototype-v1",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsafe_task_prototype_path",
    });
  });
});
