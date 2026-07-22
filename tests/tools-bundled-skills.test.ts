import { describe, expect, it } from "vitest";
import { installToolTestLifecycle, parseToolText, collectHandlers } from "./tools-test-harness.js";

installToolTestLifecycle();

type SkillToolPayload = {
  ok: boolean;
  code: string;
  data: {
    path: string;
    skill: string;
    references?: Array<{ referenceId: string }>;
  };
};

function assertSkillSurface(
  parsed: unknown,
  expectedPath: string,
  expectedReferenceIds: string[] = [],
): void {
  const result = parsed as SkillToolPayload;
  expect(result).toMatchObject({
    ok: true,
    code: "ok",
    data: { path: expectedPath },
  });
  expect(typeof result.data.skill).toBe("string");
  expect(result.data.skill.length).toBeGreaterThan(0);
  expect(result.data.skill.startsWith("---")).toBe(true);
  if (expectedReferenceIds.length > 0) {
    const ids = (result.data.references ?? []).map((item) => item.referenceId);
    expect(ids).toEqual(expect.arrayContaining(expectedReferenceIds));
  }
}

describe("tools-bundled-skills", () => {
  it("exposes the bundled public Granoflow workflow skill", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_agent_workflow_skill")?.({});
    assertSkillSurface(parseToolText(result), "skills/granoflow-agent-workflow/SKILL.md", [
      "long-term-work-memory",
      "task-work-document-workflow",
    ]);
  });

  it("exposes the bundled first-run import workflow skill", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_first_run_import_skill")?.({});
    assertSkillSurface(parseToolText(result), "skills/granoflow-first-run-import/SKILL.md", [
      "recommended-external-skills",
    ]);
  });

  it("exposes the bundled daily-review owner skill", async () => {
    const { handlers } = collectHandlers();
    const result = await handlers.get("granoflow_daily_review_skill")?.({});
    assertSkillSurface(parseToolText(result), "skills/granoflow-daily-review/SKILL.md");
  });

  it("exposes the bundled GFMCP runner skill and safe dry-run tools", async () => {
    const { handlers } = collectHandlers();

    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_gfmcp_runner_skill")?.({})),
      "skills/granoflow-gfmcp-runner/SKILL.md",
    );

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
