import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-authoring-basics", () => {
  it("rejects structured task creation without authoring quality evidence", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.statusCode = 500;
      response.end();
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "统一任务创建标准",
      description: "让所有自动创建的任务都遵守同一套质量标准。",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_authoring_quality_failed",
      data: {
        issues: expect.arrayContaining([
          expect.objectContaining({ field: "authoringEvidence.titleIntent" }),
          expect.objectContaining({ field: "authoringEvidence.plainLanguageReviewed" }),
          expect.objectContaining({ field: "authoringEvidence.analogyExcerpt" }),
          expect.objectContaining({ field: "authoringEvidence.exampleExcerpt" }),
        ]),
      },
    });
    expect(requestedUrls).toEqual([]);
  });

  it("requires different analogy and example excerpts", async () => {
    const { handlers } = collectHandlers();
    const sharedExcerpt = "比如，这像所有入口共用同一位检票员。";

    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "统一任务创建标准",
      description: `让所有入口遵守同一标准。${sharedExcerpt}`,
      authoringEvidence: {
        titleIntent: "action_or_outcome",
        plainLanguageReviewed: true,
        analogyExcerpt: sharedExcerpt,
        exampleExcerpt: sharedExcerpt,
      },
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_authoring_quality_failed",
      data: {
        issues: expect.arrayContaining([
          { field: "authoringEvidence.exampleExcerpt", reason: "must_differ" },
        ]),
      },
    });
  });

  it("rejects historical fields locally instead of attempting ordinary task creation", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.statusCode = 500;
      response.end();
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();
    const description =
      "先创建待办任务。打个比方，这像先把车停在起跑线。比如，真正执行时再切换为 doing。";

    const result = await handlers.get("granoflow_task_create")?.({
      input: {
        title: "规范任务启动时机",
        description,
        startedAt: "2026-07-18T09:00:00.000Z",
        authoringEvidence: {
          titleIntent: "action_or_outcome",
          plainLanguageReviewed: true,
          analogyExcerpt: "打个比方，这像先把车停在起跑线。",
          exampleExcerpt: "比如，真正执行时再切换为 doing。",
        },
      },
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "historical_fields_not_supported",
      data: {
        operation: "create",
        unsupportedFields: ["startedAt"],
        historicalCorrectionTool: "granoflow_task_history_mutate",
      },
    });
    expect(requestedUrls).toEqual([]);
  });

  it("requires ordinary current tasks to be created pending", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "规范任务启动时机",
      description:
        "先创建待办任务。打个比方，这像先把车停在起跑线。比如，真正执行时再切换为 doing。",
      status: "doing",
      authoringEvidence: {
        titleIntent: "action_or_outcome",
        plainLanguageReviewed: true,
        analogyExcerpt: "打个比方，这像先把车停在起跑线。",
        exampleExcerpt: "比如，真正执行时再切换为 doing。",
      },
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_creation_must_start_pending",
      data: {
        requestedStatus: "doing",
        requiredStatus: "pending",
      },
    });
  });
});
