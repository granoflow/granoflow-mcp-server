import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const workflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
  "utf8",
);
const agentSkill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
const orchestrator = readFileSync("skills/granoflow-task-orchestrator/SKILL.md", "utf8");
const coordination = readFileSync("skills/granoflow-milestone-coordination/SKILL.md", "utf8");
const collaboration = readFileSync(
  "skills/granoflow-milestone-coordination/references/milestone-collaboration-workflow.md",
  "utf8",
);

describe("UI change prototype mandate contracts", () => {
  it("requires a high-fidelity prototype for every UI-changing task", () => {
    expect(workflow).toContain("UI Change Prototype Mandate");
    expect(workflow).toContain("prototype_requirement: required");
    expect(workflow).toContain("ui_prototype_required");
    expect(workflow).toMatch(/before Analysis may be confirmed/i);
    expect(workflow).toMatch(/Do not implement UI first/i);
    expect(workflow).toContain("Prototype Preview Gate");
    expect(workflow).toContain("prototype_preview_review_required");
    expect(workflow).toContain("prototype_link_digest_required");
    expect(workflow).toContain("task_prototype_seed_forbidden");
    expect(workflow).toContain("widgets.yaml");
    expect(workflow).toContain("widget_reuse_required");
    expect(workflow).toContain("task_prototype_craft_incomplete");
    expect(workflow).toContain("delta_match");
    expect(workflow).toContain("ai_challenger");
    expect(workflow).toContain("industry_peer_c");
    expect(workflow).toContain("prototype_option_contrast_insufficient");
    expect(workflow).toContain("prototype_option_near_duplicate");
    expect(workflow).toContain("prototype_option_third_unjustified");
    expect(agentSkill).toContain("UI Change Prototype Mandate");
    expect(orchestrator).toContain("ui_prototype_required");
    expect(orchestrator).toMatch(/cannot pass Readiness without[\s\S]*ui_prototype/i);
    expect(coordination).toContain("UI Change Prototype Mandate");
    expect(collaboration).toContain("ui_prototype_required");
  });
});
