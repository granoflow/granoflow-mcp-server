import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { BUNDLED_SKILL_IDS } from "../src/workflow-resources.js";

const SKILLS_ROOT = "skills";
const MAX_DESCRIPTION_LENGTH = 1024;

type Frontmatter = {
  name?: string;
  description?: string;
};

function parseFrontmatter(content: string): Frontmatter {
  if (!content.startsWith("---")) {
    return {};
  }
  const end = content.indexOf("\n---", 3);
  if (end < 0) {
    return {};
  }
  const block = content.slice(3, end).trim();
  const result: Frontmatter = {};
  for (const line of block.split("\n")) {
    const match = /^(name|description):\s*(.*)$/.exec(line);
    if (!match) {
      continue;
    }
    const key = match[1] as keyof Frontmatter;
    let value = match[2].trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    result[key] = value;
  }
  return result;
}

function listSkillDirectories(): string[] {
  return readdirSync(SKILLS_ROOT)
    .filter((name) => {
      try {
        return statSync(join(SKILLS_ROOT, name)).isDirectory();
      } catch {
        return false;
      }
    })
    .sort();
}

describe("skills structure", () => {
  it("requires valid SKILL.md frontmatter for every skill directory", () => {
    const directories = listSkillDirectories();
    expect(directories.length).toBeGreaterThan(0);

    for (const skillId of directories) {
      const skillPath = join(SKILLS_ROOT, skillId, "SKILL.md");
      const content = readFileSync(skillPath, "utf8");
      const frontmatter = parseFrontmatter(content);

      expect(frontmatter.name, `${skillId} name`).toBe(skillId);
      expect(frontmatter.description, `${skillId} description`).toBeTruthy();
      expect(
        (frontmatter.description ?? "").length,
        `${skillId} description length`,
      ).toBeGreaterThan(0);
      expect(
        (frontmatter.description ?? "").length,
        `${skillId} description max length`,
      ).toBeLessThanOrEqual(MAX_DESCRIPTION_LENGTH);
    }
  });

  it("keeps every bundled skill id present on disk", () => {
    for (const skillId of BUNDLED_SKILL_IDS) {
      const skillPath = join(SKILLS_ROOT, skillId, "SKILL.md");
      expect(() => readFileSync(skillPath, "utf8")).not.toThrow();
    }
  });

  it("lists python scripts under skills/*/scripts as real files", () => {
    for (const skillId of listSkillDirectories()) {
      const scriptsDir = join(SKILLS_ROOT, skillId, "scripts");
      let entries: string[];
      try {
        entries = readdirSync(scriptsDir);
      } catch {
        continue;
      }
      for (const entry of entries) {
        if (!entry.endsWith(".py")) {
          continue;
        }
        expect(statSync(join(scriptsDir, entry)).isFile(), `${skillId}/scripts/${entry}`).toBe(
          true,
        );
      }
    }
  });
});
