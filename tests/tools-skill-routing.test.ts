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

describe("tools-skill-routing", () => {
  it("exposes the bundled delegated-authorization skill and public references", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_delegated_authorization_skill")?.({})),
      "skills/granoflow-delegated-authorization/SKILL.md",
      ["authorization-envelope", "host-routing-and-waiting"],
    );
  });

  it("exposes the bundled task-orchestrator skill", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_task_orchestrator_skill")?.({})),
      "skills/granoflow-task-orchestrator/SKILL.md",
      ["short-command-contract"],
    );
  });

  it("exposes the bundled milestone create workflow and coordination skill", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_milestone_workflow_skill")?.({})),
      "skills/granoflow-milestone-workflow/SKILL.md",
      ["milestone-portfolio-creation"],
    );
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_milestone_coordination_skill")?.({})),
      "skills/granoflow-milestone-coordination/SKILL.md",
      ["milestone-work-document-template", "milestone-collaboration-workflow"],
    );
  });

  it("exposes the provider-neutral persistent milestone runner", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_persistent_milestone_runner_skill")?.({})),
      "skills/granoflow-persistent-milestone-runner/SKILL.md",
      ["authorization-manifest", "runtime-contract", "worker-report"],
    );
  });

  it("exposes the integration test campaign skill", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_integration_test_campaign_skill")?.({})),
      "skills/granoflow-integration-test-campaign/SKILL.md",
      [
        "integration-campaign-closing-summary",
        "integration-campaign-closing-summary-template",
        "integration-suite-orchestration",
        "integration-test-campaign-contract",
      ],
    );
  });

  it("exposes the e2e test campaign skill", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_e2e_test_campaign_skill")?.({})),
      "skills/granoflow-e2e-test-campaign/SKILL.md",
      [
        "e2e-campaign-closing-summary",
        "e2e-campaign-closing-summary-template",
        "e2e-evidence-pack",
        "e2e-host-capabilities",
        "e2e-suite-orchestration",
        "e2e-test-campaign-contract",
        "e2e-user-flow-coverage",
      ],
    );
  });

  it("exposes the acceptance delivery skill", async () => {
    const { handlers } = collectHandlers();
    assertSkillSurface(
      parseToolText(await handlers.get("granoflow_acceptance_delivery_skill")?.({})),
      "skills/granoflow-acceptance-delivery/SKILL.md",
      [
        "full-delivery-acceptance",
        "milestone-integration-acceptance",
        "task-and-milestone-acceptance-layers",
      ],
    );
  });
});
