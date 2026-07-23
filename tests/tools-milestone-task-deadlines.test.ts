import { describe, expect, it } from "vitest";

import {
  collectHandlers,
  installToolTestLifecycle,
  parseToolText,
  startServer,
} from "./tools-test-harness.js";

installToolTestLifecycle();

const description =
  "用户需要让里程碑任务始终有明确截止日期。打个比方，这像行程中的每一站都不能晚于终点。例如，未指定任务日期时直接使用所属里程碑日期。";
const authoringEvidence = {
  titleIntent: "action_or_outcome",
  plainLanguageReviewed: true,
  analogyExcerpt: "打个比方，这像行程中的每一站都不能晚于终点。",
  exampleExcerpt: "例如，未指定任务日期时直接使用所属里程碑日期。",
};

async function startMilestoneServer(dueAt: unknown = "2026-07-25T23:59:59.000") {
  const port = await startServer((request, response) => {
    response.setHeader("content-type", "application/json");
    if (request.url === "/v1/milestones/milestone-1") {
      response.end(
        JSON.stringify({
          ok: true,
          data: { entity: { id: "milestone-1", projectId: "project-1", dueAt } },
        }),
      );
      return;
    }
    response.statusCode = 404;
    response.end(JSON.stringify({ ok: false }));
  });
  process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
}

describe("milestone task deadline resolution", () => {
  it("inherits the milestone deadline when task dueAt is omitted", async () => {
    await startMilestoneServer();
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "继承里程碑截止日期",
      description,
      projectId: "project-1",
      milestoneId: "milestone-1",
      authoringEvidence,
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        body: { milestoneId: "milestone-1", dueAt: "2026-07-25T23:59:59.000" },
        deadlineResolution: {
          source: "inherited_milestone",
          requestedDueAt: null,
          effectiveDueAt: "2026-07-25T23:59:59.000",
        },
      },
    });
  });

  it("preserves an explicit earlier deadline", async () => {
    await startMilestoneServer();
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "保留更早任务日期",
      description,
      dueAt: "2026-07-24T23:59:59.000",
      projectId: "project-1",
      milestoneId: "milestone-1",
      authoringEvidence,
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      data: {
        body: { dueAt: "2026-07-24T23:59:59.000" },
        deadlineResolution: { source: "explicit" },
      },
    });
  });

  it("fails before write when an explicit task deadline exceeds the milestone", async () => {
    await startMilestoneServer();
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "拒绝越界任务日期",
      description,
      dueAt: "2026-07-26T23:59:59.000",
      projectId: "project-1",
      milestoneId: "milestone-1",
      authoringEvidence,
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "milestone_task_due_at_after_milestone",
    });
  });

  it("fails closed when the milestone has no valid deadline", async () => {
    await startMilestoneServer(null);
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "拒绝无日期里程碑任务",
      description,
      projectId: "project-1",
      milestoneId: "milestone-1",
      authoringEvidence,
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "milestone_task_due_at_inheritance_failed",
    });
  });
});
