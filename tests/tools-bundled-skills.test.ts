import { describe, expect, it } from "vitest";
import { installToolTestLifecycle, parseToolText, collectHandlers } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-bundled-skills", () => {
  it("exposes the bundled public Granoflow workflow skill", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_agent_workflow_skill")?.({});

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-agent-workflow/SKILL.md",
        skill: expect.stringContaining("User Dissatisfaction"),
      },
    });
    const serialized = JSON.stringify(parseToolText(result));
    expect(serialized).toContain("wrapper skill");
    expect(serialized).toContain("Long-Term Work Memory");
    expect(serialized).toContain("long-term-work-memory.md");
    expect(serialized).toContain("Process today's tasks");
    expect(serialized).toContain("处理今日任务");
    expect(serialized).toContain("Analyze the first task");
    expect(serialized).toContain("请分析第一个任务");
    expect(serialized).toContain("task-work-document-workflow.md");
    expect(serialized).toContain("task-work-document-template.md");
    expect(serialized).toContain("task-analysis-profile-learning.md");
    expect(serialized).toContain("task-analysis-profile-software-development.md");
    expect(serialized).toContain("single-task workflow");
    expect(serialized).toContain("Create a task from this requirement");
    expect(serialized).toContain("把我们讨论的需求建一个任务");
    expect(serialized).toContain("discussed-requirement-task-capture.md");
    expect(serialized).toContain("explicit task-creation request confirms this write");
    expect(serialized).toContain("omit both `projectId`");
    expect(serialized).toContain("`milestoneId`");
    expect(serialized).toContain("exactly one placement sentence");
    expect(serialized).toContain("user's language");
    expect(serialized).toContain("Task Work Document");
    expect(serialized).toContain("grill");
    expect(serialized).toContain("planning_status=not_required");
    expect(serialized).toContain("Attach and hash-read back only");
    expect(serialized).toContain("plain-language explanations");
    expect(serialized).toContain("notification task");
    expect(serialized).toContain("3 minutes");
    expect(serialized).toContain("10 minutes");
    expect(serialized).toContain("synced_to_server");
    expect(serialized).toContain("unknown_remote_visibility");
    expect(serialized).toContain("decision");
    expect(serialized).toContain("similar");
    expect(serialized).toContain("project-context-attachments.md");
    expect(serialized).toContain("project_snapshot.yaml");
    expect(serialized).toContain("project_rules.yaml");
  });

  it("exposes the bundled first-run import workflow skill", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_first_run_import_skill")?.({});
    const parsed = parseToolText(result);

    expect(parsed).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-first-run-import/SKILL.md",
        skill: expect.stringContaining("Initialize Granoflow and import data"),
      },
    });
    const serialized = JSON.stringify(parsed);
    expect(serialized).toContain("初始化 Granoflow 并导入数据");
    expect(serialized).toContain("multilingual");
    expect(serialized).toContain("Cursor");
    expect(serialized).toContain("Codex");
    expect(serialized).toContain("Hermes");
    expect(serialized).toContain("Import Preview");
    expect(serialized).toContain("bounded batches");
    expect(serialized).toContain("hidden chat histories");
    expect(serialized).toContain("recommended-external-skills.md");
    expect(serialized).toContain("approved_all");
    expect(serialized).toContain("capability_pack_not_ready");
  });

  it("exposes the bundled daily-review owner skill", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_daily_review_skill")?.({});

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-daily-review/SKILL.md",
        skill: expect.stringContaining("Conversation and confirmation"),
      },
    });
    const serialized = JSON.stringify(parseToolText(result));
    expect(serialized).toContain("Display");
    expect(serialized).toContain("Write and readback");
    expect(serialized).toContain("explicitly confirmed");
  });

  it("exposes the bundled GFMCP runner skill and safe dry-run tools", async () => {
    const { handlers } = collectHandlers();

    const skill = parseToolText(await handlers.get("granoflow_gfmcp_runner_skill")?.({}));
    expect(skill).toMatchObject({
      ok: true,
      data: {
        path: "skills/granoflow-gfmcp-runner/SKILL.md",
        skill: expect.stringContaining("five-minute interval"),
      },
    });

    const prepare = parseToolText(
      await handlers.get("granoflow_gfmcp_prepare")?.({ dryRun: true }),
    );
    expect(prepare).toMatchObject({
      ok: true,
      code: "dry_run",
      data: { method: "POST", path: "/v1/ai-agent/gfmcp/prepare" },
    });
    const sync = parseToolText(await handlers.get("granoflow_gfmcp_safe_sync")?.({ dryRun: true }));
    expect(sync).toMatchObject({
      ok: true,
      code: "dry_run",
      data: { method: "POST", path: "/v1/sync/gfmcp-safe-run" },
    });
  });
});
