import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const skill = readFileSync(
  "skills/granoflow-integration-test-campaign/SKILL.md",
  "utf8",
);
const contract = readFileSync(
  "skills/granoflow-integration-test-campaign/references/integration-test-campaign-contract.md",
  "utf8",
);
const openaiYaml = readFileSync(
  "skills/granoflow-integration-test-campaign/agents/openai.yaml",
  "utf8",
);
const taskWorkflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
  "utf8",
);

describe("integration test campaign bundled skill", () => {
  it("defines unattended round loop with full suite then bug tasks", () => {
    expect(skill).toContain("naturally unattended");
    expect(skill).toContain("one milestone per round");
    expect(skill).toMatch(/Run the full suite first/i);
    expect(skill).toContain("Cluster bugs");
    expect(skill).toContain("integration_campaign_bug_clustering_required");
    expect(skill).toContain("granoflow-milestone-workflow");
    expect(skill).toContain("granoflow-task-orchestrator");
    expect(skill).toMatch(/Next round/i);
    expect(skill).toMatch(/Campaign done/i);
    expect(skill).toContain("local_machine");
    expect(openaiYaml).toContain("unattended");
  });

  it("separates campaign execution from task-local write-only policy", () => {
    expect(skill).toContain("Task Integration Test Policy");
    expect(skill).toContain("user-visible-copy-boundary.md");
    expect(contract).toContain("Relationship To Task-Local Policy");
    expect(contract).toMatch(/do not execute/i);
    expect(contract).toContain("integration_campaign_round_suite_incomplete");
    expect(contract).toContain("integration_campaign_external_deferred");
    expect(skill).toContain("Unattended Residual Report");
    expect(taskWorkflow).toContain("granoflow-integration-test-campaign");
  });
});
