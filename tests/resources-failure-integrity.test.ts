import { pathToFileURL } from "node:url";
import { join } from "node:path";
import { mkdir, rm, symlink, writeFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { createBundledSkillResources } from "../src/workflow-resources.js";
import {
  createPackageRoot,
  installWorkflowResourceLifecycle,
  writeReference,
} from "./workflow-resources-test-harness.js";

installWorkflowResourceLifecycle();

describe("resources-failure-integrity", () => {
  it("returns a stable not-found error for an unknown safe identifier", async () => {
    const root = await createPackageRoot();
    await writeReference(root, "granoflow-agent-workflow", "known-reference.md", "known\n");
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));

    await expect(
      resources.readReference("granoflow-agent-workflow", "unknown-reference"),
    ).rejects.toMatchObject({ code: "workflow_reference_not_found" });
  });

  it("reports a manifested reference that disappears before readback", async () => {
    const root = await createPackageRoot();
    const referencePath = join(
      root,
      "skills",
      "granoflow-agent-workflow",
      "references",
      "disappearing.md",
    );
    await writeReference(root, "granoflow-agent-workflow", "disappearing.md", "gone soon\n");
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));
    await resources.listReferences("granoflow-agent-workflow");
    await rm(referencePath);

    await expect(
      resources.readReference("granoflow-agent-workflow", "disappearing"),
    ).rejects.toMatchObject({ code: "workflow_reference_missing" });
  });

  it("rejects a manifested file replaced by a symlink outside its fixed root", async () => {
    const root = await createPackageRoot();
    const outside = join(root, "outside.md");
    const referencePath = join(
      root,
      "skills",
      "granoflow-agent-workflow",
      "references",
      "linked.md",
    );
    await writeFile(outside, "secret\n", "utf8");
    await writeReference(root, "granoflow-agent-workflow", "linked.md", "public\n");
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));
    await resources.listReferences("granoflow-agent-workflow");
    await rm(referencePath);
    await symlink(outside, referencePath);

    await expect(
      resources.readReference("granoflow-agent-workflow", "linked"),
    ).rejects.toMatchObject({ code: "workflow_reference_unsafe" });
  });

  it("rejects references larger than 256 KiB without truncating them", async () => {
    const root = await createPackageRoot();
    const references = join(root, "skills", "granoflow-agent-workflow", "references");
    await mkdir(references, { recursive: true });
    await writeFile(join(references, "too-large.md"), Buffer.alloc(256 * 1024 + 1, "a"));
    const resources = createBundledSkillResources(pathToFileURL(`${root}/`));

    await expect(
      resources.readReference("granoflow-agent-workflow", "too-large"),
    ).rejects.toMatchObject({ code: "workflow_reference_too_large" });
  });
});
