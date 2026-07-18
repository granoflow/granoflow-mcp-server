import { createHash } from "node:crypto";
import { mkdir, mkdtemp, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

import { afterEach, describe, expect, it } from "vitest";

import { createBundledSkillResources, type BundledSkillId } from "../src/workflow-resources.js";

const temporaryRoots: string[] = [];

async function createPackageRoot(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), "granoflow-workflow-resources-"));
  temporaryRoots.push(root);
  return root;
}

async function writeReference(
  root: string,
  skillId: BundledSkillId,
  filename: string,
  content: string,
): Promise<void> {
  const references = join(root, "skills", skillId, "references");
  await mkdir(references, { recursive: true });
  await writeFile(join(references, filename), content, "utf8");
}

afterEach(async () => {
  await Promise.all(temporaryRoots.splice(0).map((root) => rm(root, { recursive: true })));
});

describe("bundled skill workflow resources", () => {
  it("publishes the unattended interaction contract through the public manifest", async () => {
    const resources = createBundledSkillResources(new URL("../", import.meta.url));
    const manifest = await resources.listReferences("granoflow-agent-workflow");

    expect(manifest).toContainEqual({
      skillId: "granoflow-agent-workflow",
      referenceId: "unattended-interaction-contract",
      path: "skills/granoflow-agent-workflow/references/unattended-interaction-contract.md",
    });
    await expect(
      resources.readReference("granoflow-agent-workflow", "unattended-interaction-contract"),
    ).resolves.toMatchObject({
      content: expect.stringContaining("interaction_budget: 0"),
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
