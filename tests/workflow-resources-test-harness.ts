import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach } from "vitest";

export const temporaryRoots: string[] = [];

export async function createPackageRoot(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), "granoflow-workflow-resources-"));
  temporaryRoots.push(root);
  return root;
}

export async function writeReference(
  root: string,
  skillId: BundledSkillId,
  filename: string,
  content: string,
): Promise<void> {
  const references = join(root, "skills", skillId, "references");
  await mkdir(references, { recursive: true });
  await writeFile(join(references, filename), content, "utf8");
}

export function installWorkflowResourceLifecycle(): void {
  afterEach(async () => {
    await Promise.all(temporaryRoots.splice(0).map((root) => rm(root, { recursive: true })));
  });
}
