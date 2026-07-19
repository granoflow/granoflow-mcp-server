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
      referenceId: "parallel-task-execution",
      path: "skills/granoflow-agent-workflow/references/parallel-task-execution.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "unattended-interaction-contract"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("interaction_budget: 0"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "requirement-intake-and-traceability"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("The inputs are evidence, not forms"),
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "parallel-task-execution"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("Only `parallel_safe` pairs may share a batch"),
    });
  });

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

  it("discovers milestone workflow contract references", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-milestone-workflow");

    expect(manifest.map((item) => item.referenceId)).toEqual([
      "milestone-collaboration-workflow",
      "milestone-work-document-template",
    ]);
    await expect(
      resources.readReference("granoflow-milestone-workflow", "milestone-work-document-template"),
    ).resolves.toMatchObject({
      skillId: "granoflow-milestone-workflow",
      path: "skills/granoflow-milestone-workflow/references/milestone-work-document-template.md",
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
