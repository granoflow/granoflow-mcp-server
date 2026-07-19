import { describe, expect, it } from "vitest";
import { createBundledSkillResources } from "../src/workflow-resources.js";
import { installWorkflowResourceLifecycle } from "./workflow-resources-test-harness.js";

installWorkflowResourceLifecycle();

describe("resources-skill-routing", () => {
  it("discovers delegated-authorization public references", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-delegated-authorization");

    expect(manifest.map((item) => item.referenceId)).toEqual(
      expect.arrayContaining(["authorization-envelope", "host-routing-and-waiting"]),
    );
  });

  it("discovers and reads the first-run recommended external Skills owner", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-first-run-import");

    expect(manifest).toContainEqual({
      skillId: "granoflow-first-run-import",
      referenceId: "recommended-external-skills",
      path: "skills/granoflow-first-run-import/references/recommended-external-skills.md",
    });
    await expect(
      resources.readReference("granoflow-first-run-import", "recommended-external-skills"),
    ).resolves.toMatchObject({
      skillId: "granoflow-first-run-import",
      referenceId: "recommended-external-skills",
      path: "skills/granoflow-first-run-import/references/recommended-external-skills.md",
    });
  });

  it("discovers and reads the packaged external Skill routing contract", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "external-skill-routing",
      path: "skills/granoflow-agent-workflow/references/external-skill-routing.md",
    });

    await expect(
      resources.readReference("granoflow-agent-workflow", "external-skill-routing"),
    ).resolves.toMatchObject({
      skillId: "granoflow-agent-workflow",
      referenceId: "external-skill-routing",
      path: "skills/granoflow-agent-workflow/references/external-skill-routing.md",
    });
  });

  it("discovers and reads the unified Task Work Document contracts", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    for (const referenceId of [
      "software-structural-budget",
      "task-work-document-template",
      "task-work-document-workflow",
      "visual-narrative-task-work",
    ]) {
      expect(manifest).toContainEqual({
        skillId: "granoflow-agent-workflow",
        referenceId,
        path: `skills/granoflow-agent-workflow/references/${referenceId}.md`,
      });
      await expect(
        resources.readReference("granoflow-agent-workflow", referenceId),
      ).resolves.toMatchObject({
        skillId: "granoflow-agent-workflow",
        referenceId,
        path: `skills/granoflow-agent-workflow/references/${referenceId}.md`,
      });
    }
  });
});
