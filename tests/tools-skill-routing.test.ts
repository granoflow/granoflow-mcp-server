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

  it("exposes the bundled milestone create workflow and coordination skill", async () => {
    const { handlers } = collectHandlers();

    const createResult = parseToolText(
      await handlers.get("granoflow_milestone_workflow_skill")?.({}),
    );
    expect(createResult).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-milestone-workflow/SKILL.md",
        skill: expect.stringContaining("single_create"),
      },
    });
    expect(JSON.stringify(createResult)).toContain("milestone-portfolio-creation.md");

    const coordResult = parseToolText(
      await handlers.get("granoflow_milestone_coordination_skill")?.({}),
    );
    expect(coordResult).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-milestone-coordination/SKILL.md",
        skill: expect.stringContaining("Milestone Work"),
      },
    });
    const coordSerialized = JSON.stringify(coordResult);
    expect(coordSerialized).toContain("milestone-work-document-template.md");
    expect(coordSerialized).toContain("milestone-collaboration-workflow.md");
    expect(coordSerialized).toContain("controller Task");
    expect(coordSerialized).toContain("Child Task Work");
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

  it("exposes the unattended integration test campaign skill", async () => {
    const { handlers } = collectHandlers();

    const result = parseToolText(
      await handlers.get("granoflow_integration_test_campaign_skill")?.({}),
    );
    expect(result).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-integration-test-campaign/SKILL.md",
        skill: expect.stringContaining("naturally unattended"),
      },
    });
    const serialized = JSON.stringify(result);
    expect(serialized).toContain("integration-test-campaign-contract.md");
    expect(serialized).toContain("bug_clustering");
    expect(serialized).toContain("one milestone per round");
  });
});
