import { describe, expect, it } from "vitest";
import {
  reviewTaskDescriptionImpact,
  taskDescriptionSha256,
  verifyTaskDescriptionImpact,
} from "../src/tool-runtime-task-description-impact.js";
import { validateTaskAuthoringQuality } from "../src/tool-runtime-authoring.js";
import {
  collectHandlers,
  installToolTestLifecycle,
  parseToolText,
  readJsonBody,
  startServer,
} from "./tools-test-harness.js";

installToolTestLifecycle();

const description =
  "用户需要知道任务更新是否改变原目标。打个比方，这像修改地图标记前先确认道路是否真的改变。例如，只调整提醒时间时，道路不变，描述也不应重写。";
const updatedAt = "2026-07-23T10:00:00.000Z";

function review(
  reasonCode: string,
  decision: "unchanged" | "rewrite" = "unchanged",
  overrides: Record<string, unknown> = {},
) {
  return {
    reviewedTaskUpdatedAt: updatedAt,
    reviewedDescriptionSha256: taskDescriptionSha256(description),
    decision,
    reasonCode,
    rationale: "The requested fields were reviewed against the current task meaning.",
    ...overrides,
  };
}

async function startTaskServer(status = "pending") {
  let task: Record<string, unknown> = {
    id: "task-1",
    title: "检查任务描述更新影响",
    description,
    status,
    dueAt: null,
    updatedAt,
  };
  const requests: Array<{ method?: string; url?: string; body?: unknown }> = [];
  const port = await startServer(async (request, response) => {
    response.setHeader("content-type", "application/json");
    if (request.method === "GET" && request.url === "/v1/tasks/task-1") {
      response.end(JSON.stringify({ ok: true, data: { entity: task } }));
      return;
    }
    if (request.method === "PATCH" && request.url === "/v1/tasks/task-1") {
      const body = (await readJsonBody(request)) as Record<string, unknown>;
      requests.push({ method: request.method, url: request.url, body });
      task = { ...task, ...body, updatedAt: "2026-07-23T10:01:00.000Z" };
      response.end(JSON.stringify({ ok: true, data: { entity: task } }));
      return;
    }
    response.statusCode = 404;
    response.end(JSON.stringify({ ok: false }));
  });
  process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
  return { requests, getTask: () => task };
}

describe("task description impact guard", () => {
  it("allows operational updates without rewriting legacy description", async () => {
    await startTaskServer();
    const gate = await reviewTaskDescriptionImpact(
      {
        taskId: "task-1",
        review: review("operational_only"),
        operation: "update",
      },
      { dueAt: "2026-07-30T23:59:59.000Z" },
      validateTaskAuthoringQuality,
    );
    expect(gate).toMatchObject({
      ok: true,
      changedFields: ["dueAt"],
      currentDescriptionSha256: taskDescriptionSha256(description),
    });
  });

  it("fails before write when review is missing or stale", async () => {
    await startTaskServer();
    await expect(
      reviewTaskDescriptionImpact(
        { taskId: "task-1", review: undefined, operation: "update" },
        { status: "doing" },
        validateTaskAuthoringQuality,
      ),
    ).resolves.toMatchObject({
      ok: false,
      code: "task_description_impact_review_required",
    });
    await expect(
      reviewTaskDescriptionImpact(
        {
          taskId: "task-1",
          review: review("operational_only", "unchanged", {
            reviewedDescriptionSha256: "0".repeat(64),
          }),
          operation: "update",
        },
        { status: "doing" },
        validateTaskAuthoringQuality,
      ),
    ).resolves.toMatchObject({
      ok: false,
      code: "task_description_review_digest_mismatch",
    });
  });

  it("requires complete quality evidence for semantic rewrites", async () => {
    await startTaskServer();
    const nextDescription =
      "用户需要让任务的新范围成为当前事实。打个比方，这像道路改线后同步更新地图。例如，任务从仅改提醒扩展到修改授权行为后，描述必须说明新的验收结果。";
    const missingEvidence = await reviewTaskDescriptionImpact(
      {
        taskId: "task-1",
        review: review("semantic_change", "rewrite", {
          fiveDimensionsReviewed: true,
          writebackRefs: ["task-work://task-1/revision-2"],
        }),
        operation: "update",
      },
      { description: nextDescription, scope: "authorization" },
      validateTaskAuthoringQuality,
    );
    expect(missingEvidence).toMatchObject({
      ok: false,
      code: "task_description_quality_failed",
    });

    const gate = await reviewTaskDescriptionImpact(
      {
        taskId: "task-1",
        review: review("semantic_change", "rewrite", {
          fiveDimensionsReviewed: true,
          writebackRefs: ["task-work://task-1/revision-2"],
          authoringEvidence: {
            titleIntent: "action_or_outcome",
            plainLanguageReviewed: true,
            analogyExcerpt: "打个比方，这像道路改线后同步更新地图。",
            exampleExcerpt: "例如，任务从仅改提醒扩展到修改授权行为后，描述必须说明新的验收结果。",
          },
        }),
        operation: "update",
      },
      { description: nextDescription, scope: "authorization" },
      validateTaskAuthoringQuality,
    );
    expect(gate).toMatchObject({
      ok: true,
      changedFields: ["description", "scope"],
    });
  });
});

describe("task description impact completion and readback", () => {
  it("freezes completed prose but permits an exact managed summary update", async () => {
    await startTaskServer("done");
    const overwrite = await reviewTaskDescriptionImpact(
      {
        taskId: "task-1",
        review: review("description_correction", "rewrite", {
          fiveDimensionsReviewed: true,
          authoringEvidence: {
            titleIntent: "action_or_outcome",
            plainLanguageReviewed: true,
            analogyExcerpt: "打个比方，这像修改地图标记前先确认道路是否真的改变。",
            exampleExcerpt: "例如，只调整提醒时间时，道路不变，描述也不应重写。",
          },
        }),
        operation: "update",
      },
      { description: `${description}\n覆盖正文` },
      validateTaskAuthoringQuality,
    );
    expect(overwrite).toMatchObject({
      ok: false,
      code: "task_description_post_completion_overwrite_forbidden",
    });

    const start = "<!-- summary:start -->";
    const end = "<!-- summary:end -->";
    const managed = await reviewTaskDescriptionImpact(
      {
        taskId: "task-1",
        review: review("completion_summary_only"),
        operation: "completion_summary",
        managedBlockMarkers: { start, end },
      },
      { description: `${description}${start}\n结果已确认\n${end}` },
      validateTaskAuthoringQuality,
    );
    expect(managed).toMatchObject({ ok: true });
  });

  it("strips transient review and verifies real update readback", async () => {
    const server = await startTaskServer();
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_update_structured")?.({
      taskId: "task-1",
      dueAt: "2026-07-30T23:59:59.000Z",
      descriptionImpactReview: review("operational_only"),
      dryRun: false,
    });
    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        descriptionImpact: {
          changedFields: ["dueAt"],
          readbackStatus: "verified",
        },
      },
    });
    expect(server.requests).toHaveLength(1);
    expect(server.requests[0].body).not.toHaveProperty("descriptionImpactReview");

    const task = server.getTask();
    const gate = await reviewTaskDescriptionImpact(
      {
        taskId: "task-1",
        review: {
          ...review("operational_only"),
          reviewedTaskUpdatedAt: task.updatedAt,
          reviewedDescriptionSha256: taskDescriptionSha256(task.description),
        },
        operation: "update",
      },
      { status: "doing" },
      validateTaskAuthoringQuality,
    );
    expect(gate.ok).toBe(true);
    if (gate.ok) {
      expect(await verifyTaskDescriptionImpact("task-1", gate, { status: "doing" })).toMatchObject({
        ok: false,
        code: "task_description_readback_mismatch",
      });
    }
  });
});
