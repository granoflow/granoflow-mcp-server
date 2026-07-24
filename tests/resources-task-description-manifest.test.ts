import { describe, expect, it } from "vitest";

import { createBundledSkillResources } from "../src/workflow-resources.js";

describe("task description update reference manifest", () => {
  it("lists and reads the contract without locking its prose", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "task-description-update-contract",
      path: "skills/granoflow-agent-workflow/references/task-description-update-contract.md",
    });
    const reference = await resources.readReference(
      "granoflow-agent-workflow",
      "task-description-update-contract",
    );
    expect(reference.content.length).toBeGreaterThan(0);
  });

  it("lists and reads the implementation learning ledger contract", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");
    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "implementation-learning-ledger",
      path: "skills/granoflow-agent-workflow/references/implementation-learning-ledger.md",
    });
    const reference = await resources.readReference(
      "granoflow-agent-workflow",
      "implementation-learning-ledger",
    );
    expect(reference.content.length).toBeGreaterThan(0);
  });
});
