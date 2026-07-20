import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const skill = readFileSync("skills/granoflow-project-definition/SKILL.md", "utf8");
const workflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
  "utf8",
);
const quality = readFileSync(
  "skills/granoflow-agent-workflow/references/task-authoring-quality-contract.md",
  "utf8",
);
const projectTemplate = readFileSync(
  "skills/granoflow-agent-workflow/references/project-work-document-template.md",
  "utf8",
);

describe("capability-critical dependency selection contracts", () => {
  it("forces concrete package selection in Project Definition Step 1", () => {
    expect(skill).toMatch(
      /do not defer to the first coding task/i,
    );
    expect(skill).toMatch(/Framework-only answers[\s\S]*capability_dependency_unselected/i);
    expect(projectTemplate).toContain("capability_dependency_unselected");
    expect(projectTemplate).toMatch(/EPUB parse\/render/i);
  });

  it("requires Analysis to challenge unreasonable dependency selections", () => {
    expect(workflow).toContain("Analysis-time dependency challenge");
    expect(workflow).toMatch(
      /silently swap libraries in code/i,
    );
    expect(workflow).toMatch(
      /capability-critical libraries[\s\S]*dependency selections were challenged/i,
    );
    expect(quality).toMatch(
      /capability-critical library[\s\S]*dependencies\.approved/i,
    );
    expect(quality).toMatch(/silently pick a\s+different EPUB/i);
  });
});
