import { describe, expect, it } from "vitest";
import { installToolTestLifecycle, parseToolText, collectHandlers } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-skill-routing", () => {
  it("exposes the bundled delegated-authorization skill and public references", async () => {
    const { handlers } = collectHandlers();

    const result = parseToolText(
      await handlers.get("granoflow_delegated_authorization_skill")?.({}),
    );
    expect(result).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-delegated-authorization/SKILL.md",
        skill: expect.stringContaining("conditional delegation"),
      },
    });
    expect(JSON.stringify(result)).toContain("authorization-envelope.md");
    expect(JSON.stringify(result)).toContain("host-routing-and-waiting.md");
    expect(JSON.stringify(result)).toContain("unattended-interaction-contract.md");
  });

  it("exposes the bundled task-orchestrator skill and short-command contract", async () => {
    const { handlers } = collectHandlers();

    const result = parseToolText(await handlers.get("granoflow_task_orchestrator_skill")?.({}));
    expect(result).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-task-orchestrator/SKILL.md",
        skill: expect.stringContaining("single upper-layer task entrypoint"),
      },
    });
    const serialized = JSON.stringify(result);
    expect(serialized).toContain("short-command-contract.md");
    expect(serialized).toContain("gf做");
    expect(serialized).toContain("finish_audit");
  });

  it("exposes the bundled milestone workflow and its contract references", async () => {
    const { handlers } = collectHandlers();

    const result = parseToolText(await handlers.get("granoflow_milestone_workflow_skill")?.({}));
    expect(result).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-milestone-workflow/SKILL.md",
        skill: expect.stringContaining("milestone-level integration evidence"),
      },
    });
    const serialized = JSON.stringify(result);
    expect(serialized).toContain("milestone-work-document-template.md");
    expect(serialized).toContain("milestone-collaboration-workflow.md");
    expect(serialized).toContain("controller Task");
    expect(serialized).toContain("Child Task Work");
  });

  it("exposes the provider-neutral persistent milestone runner", async () => {
    const { handlers } = collectHandlers();

    const result = parseToolText(
      await handlers.get("granoflow_persistent_milestone_runner_skill")?.({}),
    );
    expect(result).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-persistent-milestone-runner/SKILL.md",
        skill: expect.stringContaining("provider-neutral"),
      },
    });
    const serialized = JSON.stringify(result);
    expect(serialized).toContain("authorization-manifest.md");
    expect(serialized).toContain("runtime-contract.md");
    expect(serialized).toContain("worker-report.md");
  });
});
