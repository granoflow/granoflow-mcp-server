import { createHash } from "node:crypto";
import { lstat, open, readdir, realpath } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { isAbsolute, join, posix, relative } from "node:path";

const MAX_REFERENCE_BYTES = 256 * 1024;

export const BUNDLED_SKILL_IDS = [
  "granoflow-agent-workflow",
  "granoflow-daily-review",
  "granoflow-first-run-import",
  "granoflow-review-card-draft",
  "granoflow-gfmcp-runner",
] as const;

export type BundledSkillId = (typeof BUNDLED_SKILL_IDS)[number];

export type BundledSkillReferenceManifestItem = {
  skillId: BundledSkillId;
  referenceId: string;
  path: string;
};

export type WorkflowResourceErrorCode =
  | "workflow_reference_not_found"
  | "workflow_reference_missing"
  | "workflow_reference_unsafe"
  | "workflow_reference_too_large";

export class WorkflowResourceError extends Error {
  constructor(
    readonly code: WorkflowResourceErrorCode,
    message: string,
  ) {
    super(message);
    this.name = "WorkflowResourceError";
  }
}

function isWithin(root: string, target: string): boolean {
  const path = relative(root, target);
  return path === "" || (!path.startsWith("..") && !isAbsolute(path));
}

function requireBundledSkillId(skillId: string): BundledSkillId {
  if (!BUNDLED_SKILL_IDS.some((candidate) => candidate === skillId)) {
    throw new WorkflowResourceError(
      "workflow_reference_unsafe",
      "The bundled workflow skill identifier is unsafe.",
    );
  }
  return skillId as BundledSkillId;
}

export type BundledSkillResources = {
  listReferences: (skillId: string) => Promise<BundledSkillReferenceManifestItem[]>;
  readReference: (
    skillId: string,
    referenceId: string,
  ) => Promise<
    BundledSkillReferenceManifestItem & {
      sha256: string;
      bytes: number;
      content: string;
    }
  >;
};

export function createBundledSkillResources(
  packageRootUrl: URL = new URL("../", import.meta.url),
): BundledSkillResources {
  const packageRoot = fileURLToPath(packageRootUrl);
  const manifests = new Map<BundledSkillId, BundledSkillReferenceManifestItem[]>();

  const listReferences = async (skillId: string): Promise<BundledSkillReferenceManifestItem[]> => {
    const safeSkillId = requireBundledSkillId(skillId);
    const referencesRoot = join(packageRoot, "skills", safeSkillId, "references");
    const entries = await readdir(referencesRoot, { withFileTypes: true });
    const manifest = entries
      .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
      .map((entry) => ({
        skillId: safeSkillId,
        referenceId: entry.name.slice(0, -3),
        path: posix.join("skills", safeSkillId, "references", entry.name),
      }))
      .sort((left, right) => left.referenceId.localeCompare(right.referenceId));
    manifests.set(safeSkillId, manifest);
    return manifest;
  };

  return {
    listReferences,
    async readReference(skillId, referenceId) {
      const safeSkillId = requireBundledSkillId(skillId);
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(referenceId)) {
        throw new WorkflowResourceError(
          "workflow_reference_unsafe",
          "The bundled workflow reference identifier is unsafe.",
        );
      }
      const manifest = manifests.get(safeSkillId) ?? (await listReferences(safeSkillId));
      const item = manifest.find((candidate) => candidate.referenceId === referenceId);
      if (!item) {
        throw new WorkflowResourceError(
          "workflow_reference_not_found",
          "The bundled workflow reference was not found in the public manifest.",
        );
      }
      const path = item.path;
      const referencesRoot = join(packageRoot, "skills", safeSkillId, "references");
      const absolutePath = join(packageRoot, path);
      let content: string;
      try {
        const [realRoot, realTarget, targetStat] = await Promise.all([
          realpath(referencesRoot),
          realpath(absolutePath),
          lstat(absolutePath),
        ]);
        if (
          !isWithin(realRoot, realTarget) ||
          !targetStat.isFile() ||
          targetStat.isSymbolicLink()
        ) {
          throw new WorkflowResourceError(
            "workflow_reference_unsafe",
            "The bundled workflow reference did not resolve to a regular file in its fixed root.",
          );
        }
        if (targetStat.size > MAX_REFERENCE_BYTES) {
          throw new WorkflowResourceError(
            "workflow_reference_too_large",
            "The bundled workflow reference exceeds the 256 KiB limit.",
          );
        }
        const handle = await open(realTarget, "r");
        try {
          const openedStat = await handle.stat();
          if (
            !openedStat.isFile() ||
            openedStat.dev !== targetStat.dev ||
            openedStat.ino !== targetStat.ino
          ) {
            throw new WorkflowResourceError(
              "workflow_reference_unsafe",
              "The bundled workflow reference changed during safe resolution.",
            );
          }
          if (openedStat.size > MAX_REFERENCE_BYTES) {
            throw new WorkflowResourceError(
              "workflow_reference_too_large",
              "The bundled workflow reference exceeds the 256 KiB limit.",
            );
          }
          content = await handle.readFile("utf8");
          if (Buffer.byteLength(content) > MAX_REFERENCE_BYTES) {
            throw new WorkflowResourceError(
              "workflow_reference_too_large",
              "The bundled workflow reference exceeds the 256 KiB limit.",
            );
          }
        } finally {
          await handle.close();
        }
      } catch (error) {
        if (error instanceof WorkflowResourceError) {
          throw error;
        }
        if ((error as NodeJS.ErrnoException).code === "ENOENT") {
          throw new WorkflowResourceError(
            "workflow_reference_missing",
            "The manifested bundled workflow reference is missing.",
          );
        }
        throw error;
      }
      return {
        skillId: safeSkillId,
        referenceId,
        path,
        sha256: createHash("sha256").update(content).digest("hex"),
        bytes: Buffer.byteLength(content),
        content,
      };
    },
  };
}

export const bundledSkillResources = createBundledSkillResources();
