import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-tags-and-list", () => {
  it("omits tags when the tag catalog is unavailable", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/tags") {
        response.statusCode = 503;
        response.end(JSON.stringify({ ok: false, code: "unavailable" }));
        return;
      }
      if (request.method === "POST" && request.url === "/v1/tasks") {
        response.end(
          JSON.stringify({
            ok: true,
            code: "ok",
            data: { entity: { title: "No tags" } },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_create")?.({
      input: {
        title: "No tags",
        description:
          "标签目录不可用时仍创建任务。打个比方，这像通讯录打不开时先记下事情。比如，maybe-tag 会被跳过，任务仍会创建。",
        authoringEvidence: {
          titleIntent: "action_or_outcome",
          plainLanguageReviewed: true,
          analogyExcerpt: "打个比方，这像通讯录打不开时先记下事情。",
          exampleExcerpt: "比如，maybe-tag 会被跳过，任务仍会创建。",
        },
        tags: ["maybe-tag"],
      },
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        entity: {
          title: "No tags",
        },
        tagFilter: {
          acceptedTags: [],
          skippedTags: [{ slug: "maybe-tag", reason: "unknown_tag" }],
          catalogUnavailable: true,
        },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain('"tags"');
  });

  it("rejects generic task creation when analogy and example evidence are invalid", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.statusCode = 500;
      response.end();
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_create")?.({
      input: {
        title: "统一任务创建标准",
        description: "所有入口都遵守同一套标准。",
        authoringEvidence: {
          titleIntent: "action_or_outcome",
          plainLanguageReviewed: true,
          analogyExcerpt: "无",
          exampleExcerpt: "文中没有这个例子",
        },
      },
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "task_authoring_quality_failed",
      data: {
        issues: expect.arrayContaining([
          { field: "authoringEvidence.analogyExcerpt", reason: "placeholder" },
          { field: "authoringEvidence.exampleExcerpt", reason: "not_in_description" },
        ]),
      },
    });
    expect(requestedUrls).toEqual([]);
  });

  it("strips valid generic authoring evidence from the API preview", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_task_create")?.({
      input: {
        title: "统一任务创建标准",
        description:
          "让入口共用规则。打个比方，这像每扇门都由同一位检票员检查。比如，项目自动生成的任务也必须给出通俗例子。",
        authoringEvidence: {
          titleIntent: "action_or_outcome",
          plainLanguageReviewed: true,
          analogyExcerpt: "打个比方，这像每扇门都由同一位检票员检查。",
          exampleExcerpt: "比如，项目自动生成的任务也必须给出通俗例子。",
        },
      },
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        body: {
          title: "统一任务创建标准",
        },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain('"authoringEvidence"');
  });
});
