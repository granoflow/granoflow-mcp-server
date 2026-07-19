import { createHash } from "node:crypto";
import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { describe, expect, it } from "vitest";
import { createBundledSkillResources } from "../src/workflow-resources.js";
import {
  createPackageRoot,
  installWorkflowResourceLifecycle,
  writeReference,
} from "./workflow-resources-test-harness.js";

installWorkflowResourceLifecycle();

describe("resources-read-safety", () => {
  it("lists public Markdown references in deterministic order", async () => {
    const root = await createPackageRoot();
    await writeReference(root, "granoflow-agent-workflow", "z-last.md", "last\n");
    await writeReference(root, "granoflow-agent-workflow", "a-first.md", "first\n");
    await writeFile(
      join(root, "skills", "granoflow-agent-workflow", "references", "ignored.txt"),
      "not public\n",
      "utf8",
    );
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));

    await expect(resources.listReferences("granoflow-agent-workflow")).resolves.toEqual([
      {
        skillId: "granoflow-agent-workflow",
        referenceId: "a-first",
        path: "skills/granoflow-agent-workflow/references/a-first.md",
      },
      {
        skillId: "granoflow-agent-workflow",
        referenceId: "z-last",
        path: "skills/granoflow-agent-workflow/references/z-last.md",
      },
    ]);
  });

  it("reads one manifested reference with package-relative evidence", async () => {
    const root = await createPackageRoot();
    const content = "# Analysis workflow\n\nControl-plane instructions.\n";
    await writeReference(root, "granoflow-agent-workflow", "task-analysis-execution.md", content);
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));

    await expect(
      resources.readReference("granoflow-agent-workflow", "task-analysis-execution"),
    ).resolves.toEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "task-analysis-execution",
      path: "skills/granoflow-agent-workflow/references/task-analysis-execution.md",
      sha256: createHash("sha256").update(content).digest("hex"),
      bytes: Buffer.byteLength(content),
      content,
    });
  });

  it("rejects unsafe reference identifiers before filesystem access", async () => {
    const root = await createPackageRoot();
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));

    await expect(
      resources.readReference("granoflow-agent-workflow", "../../outside"),
    ).rejects.toMatchObject({ code: "workflow_reference_unsafe" });
  });

  it("rejects unknown skill identifiers when callers bypass MCP validation", async () => {
    const root = await createPackageRoot();
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));

    await expect(resources.readReference("../../outside", "safe-reference")).rejects.toMatchObject({
      code: "workflow_reference_unsafe",
    });
  });
});
