import { describe, expect, it } from "vitest";
import { createBundledSkillResources } from "../src/workflow-resources.js";
import { installWorkflowResourceLifecycle } from "./workflow-resources-test-harness.js";

installWorkflowResourceLifecycle();

describe("resources-manifests", () => {
  it("publishes the unattended interaction contract through the public manifest", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "unattended-interaction-contract",
      path: "skills/granoflow-agent-workflow/references/unattended-interaction-contract.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "git-capability-detection",
      path: "skills/granoflow-agent-workflow/references/git-capability-detection.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "git-checkpoint-workflow",
      path: "skills/granoflow-agent-workflow/references/git-checkpoint-workflow.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "requirement-intake-and-traceability",
      path: "skills/granoflow-agent-workflow/references/requirement-intake-and-traceability.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "prototype-expression-brainstorm",
      path: "skills/granoflow-agent-workflow/references/prototype-expression-brainstorm.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "prototype-baseline-fit",
      path: "skills/granoflow-agent-workflow/references/prototype-baseline-fit.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "change-impact-fanout",
      path: "skills/granoflow-agent-workflow/references/change-impact-fanout.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "discussion-writeback-contract",
      path: "skills/granoflow-agent-workflow/references/discussion-writeback-contract.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "prototype-product-truth-writeback",
      path: "skills/granoflow-agent-workflow/references/prototype-product-truth-writeback.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "prototype-doc-coverage",
      path: "skills/granoflow-agent-workflow/references/prototype-doc-coverage.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "user-visible-copy-boundary",
      path: "skills/granoflow-agent-workflow/references/user-visible-copy-boundary.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "parallel-task-execution",
      path: "skills/granoflow-agent-workflow/references/parallel-task-execution.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "milestone-plan-acceptance-pack",
      path: "skills/granoflow-agent-workflow/references/milestone-plan-acceptance-pack.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "milestone-plan-acceptance-pack-template",
      path: "skills/granoflow-agent-workflow/references/milestone-plan-acceptance-pack-template.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "plan-design-gate",
      path: "skills/granoflow-agent-workflow/references/plan-design-gate.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "unattended-interaction-contract"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("interaction_budget: 0"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "milestone-plan-acceptance-pack"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Milestone Plan Acceptance Pack"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "milestone-plan-acceptance-pack"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Implementation And Delivery Reference"),
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "workflow-jargon-plain-language",
      path: "skills/granoflow-agent-workflow/references/workflow-jargon-plain-language.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "workflow-jargon-plain-language"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Workflow Jargon"),
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "long-task-run-continuity",
      path: "skills/granoflow-agent-workflow/references/long-task-run-continuity.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "durable-run-plan-template",
      path: "skills/granoflow-agent-workflow/references/durable-run-plan-template.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "long-task-run-continuity"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Collaborative planning surface"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "long-task-run-continuity"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Durable run plan"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "requirement-intake-and-traceability"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("The inputs are evidence, not forms"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "change-impact-fanout"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Change Impact Ledger"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "prototype-product-truth-writeback"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("decision_class"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "parallel-task-execution"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Only `parallel_safe` pairs may share a batch"),
    });
  });
});

describe("resources-manifests agent-workflow extras", () => {
  it("publishes the confirmed chrome lock contract", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "prototype-confirmed-chrome-lock",
      path: "skills/granoflow-agent-workflow/references/prototype-confirmed-chrome-lock.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "prototype-confirmed-chrome-lock"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Prototype Confirmed Chrome Lock"),
    });
  });

  it("publishes app icon source and prototype implementation fidelity gates", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "app-icon-source-gate",
      path: "skills/granoflow-agent-workflow/references/app-icon-source-gate.md",
    });
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "prototype-implementation-fidelity",
      path: "skills/granoflow-agent-workflow/references/prototype-implementation-fidelity.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "prototype-doc-coverage"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Prototype → Document Coverage"),
    });
  });

  it("publishes the acceptance outcome contract", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "acceptance-outcome-contract",
      path: "skills/granoflow-agent-workflow/references/acceptance-outcome-contract.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "acceptance-outcome-contract"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Acceptance Outcome Contract"),
    });
  });

  it("publishes the code signing strategy contract", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "code-signing-strategy",
      path: "skills/granoflow-agent-workflow/references/code-signing-strategy.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "code-signing-strategy"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Code Signing Strategy"),
    });
  });
});

describe("resources-manifests campaign and orchestration extras", () => {
  it("discovers the persistent milestone runner contracts", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-persistent-milestone-runner");

    expect(manifest.map((item) => item.referenceId)).toEqual([
      "acceptance-report-manifest",
      "authorization-manifest",
      "runtime-contract",
      "worker-report",
    ]);
  });

  it("discovers integration test campaign references", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-integration-test-campaign");

    expect(manifest.map((item) => item.referenceId)).toEqual([
      "integration-campaign-closing-summary",
      "integration-campaign-closing-summary-template",
      "integration-suite-orchestration",
      "integration-test-campaign-contract",
    ]);
    await expect(
      resources.readReference(
        "granoflow-integration-test-campaign",
        "integration-suite-orchestration",
      ),
    ).resolves.toMatchObject({
      skillId: "granoflow-integration-test-campaign",
      path: "skills/granoflow-integration-test-campaign/references/integration-suite-orchestration.md",
    });
  });

  it("discovers e2e test campaign references", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-e2e-test-campaign");

    expect(manifest.map((item) => item.referenceId)).toEqual([
      "e2e-campaign-closing-summary",
      "e2e-campaign-closing-summary-template",
      "e2e-evidence-pack",
      "e2e-host-capabilities",
      "e2e-suite-orchestration",
      "e2e-test-campaign-contract",
      "e2e-user-flow-coverage",
    ]);
    await expect(
      resources.readReference("granoflow-e2e-test-campaign", "e2e-evidence-pack"),
    ).resolves.toMatchObject({
      skillId: "granoflow-e2e-test-campaign",
      path: "skills/granoflow-e2e-test-campaign/references/e2e-evidence-pack.md",
    });
  });

  it("discovers milestone workflow create and coordination references", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const createManifest = await resources.listReferences("granoflow-milestone-workflow");
    expect(createManifest.map((item) => item.referenceId)).toEqual([
      "milestone-portfolio-creation",
    ]);
    const coordManifest = await resources.listReferences("granoflow-milestone-coordination");
    expect(coordManifest.map((item) => item.referenceId)).toEqual([
      "milestone-collaboration-workflow",
      "milestone-work-document-template",
    ]);
    await expect(
      resources.readReference(
        "granoflow-milestone-coordination",
        "milestone-work-document-template",
      ),
    ).resolves.toMatchObject({
      skillId: "granoflow-milestone-coordination",
      path: "skills/granoflow-milestone-coordination/references/milestone-work-document-template.md",
    });
  });

  it("discovers task-orchestrator public references", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-task-orchestrator");

    expect(manifest.map((item) => item.referenceId)).toEqual(
      expect.arrayContaining([
        "intent-and-maturity-routing",
        "task-depth-placement-and-dates",
        "short-command-contract",
        "end-to-end-orchestration",
      ]),
    );
    await expect(
      resources.readReference("granoflow-task-orchestrator", "short-command-contract"),
    ).resolves.toMatchObject({
      skillId: "granoflow-task-orchestrator",
      path: "skills/granoflow-task-orchestrator/references/short-command-contract.md",
    });
  });
});
