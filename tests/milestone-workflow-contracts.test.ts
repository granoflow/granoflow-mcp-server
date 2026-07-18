import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const skill = readFileSync("skills/granoflow-milestone-workflow/SKILL.md", "utf8");
const template = readFileSync(
  "skills/granoflow-milestone-workflow/references/milestone-work-document-template.md",
  "utf8",
);
const workflow = readFileSync(
  "skills/granoflow-milestone-workflow/references/milestone-collaboration-workflow.md",
  "utf8",
);
const persistentSkill = readFileSync(
  "skills/granoflow-persistent-milestone-runner/SKILL.md",
  "utf8",
);
const runtimeContract = readFileSync(
  "skills/granoflow-persistent-milestone-runner/references/runtime-contract.md",
  "utf8",
);
const authorizationManifest = readFileSync(
  "skills/granoflow-persistent-milestone-runner/references/authorization-manifest.md",
  "utf8",
);

describe("milestone workflow contracts", () => {
  it("keeps milestone orchestration separate from child Task Work", () => {
    expect(skill).toContain("The MCP server stays a thin workflow and API adapter");
    expect(skill).toContain("one controller Task");
    expect(skill).toContain("Each child task owns its Task Work");
    expect(skill).toContain("Do not begin with a frozen task list");
    expect(skill).toContain("Do not infer milestone readiness from every child being `done`");
    expect(template).toContain("It is not a large Task Work document");
    expect(template).toContain("Child Task Work documents own task-local Analysis");
    expect(workflow).toContain("It does not replace child Task Work");
  });

  it("defines a stable charter with an evolving task portfolio", () => {
    for (const field of [
      "document_type: milestone_work",
      "milestone_id:",
      "controller_task_id:",
      "charter_status:",
      "decomposition_status:",
      "integration_readiness_status:",
      "acceptance_status:",
    ]) {
      expect(template).toContain(field);
    }
    expect(template).toContain("## User-visible Acceptance");
    expect(template).toContain("## Decomposition Rules");
    expect(template).toContain("## Dependency And Handoff Map");
    expect(template).toContain("## Integration Verification");
    expect(workflow).toContain("`portfolio_change`");
    expect(workflow).toContain("`charter_change`");
    expect(workflow).toContain("`follow_up`");
  });

  it("requires coverage, integration evidence, authorization, and App readback", () => {
    expect(workflow).toContain("every mandatory acceptance ID");
    expect(workflow).toContain("exact milestone");
    expect(workflow).toContain("user-visible or system-visible journey works");
    expect(workflow).toContain("App-owned milestone context archive/closure preview");
    expect(workflow).toContain("read back milestone state");
    expect(skill).toContain("Never persist secrets, OTPs, recovery codes, tokens");
  });

  it("defines durable evidence-gated execution without premature completion", () => {
    expect(skill).toContain("granoflow_persistent_milestone_runner_skill");
    expect(workflow).toContain("A final answer, summary, successful process exit");
    expect(workflow).toContain("three consecutive attempts");
    expect(workflow).toContain("continue other eligible tasks");
    expect(persistentSkill).toContain("Durable lease, heartbeat, checkpoint");
    expect(persistentSkill).toContain("Task Delivery");
    expect(runtimeContract).toContain("Attempt history is capped at 100 records");
  });

  it("requires full access and an exhaustive external capability decision", () => {
    expect(template).toContain("### Persistent Execution Preflight");
    expect(template).toContain("### External Capability Matrix");
    expect(workflow).toContain("full runtime access");
    expect(workflow).toContain("`granted`, `excluded`, or");
    expect(authorizationManifest).toContain("reference-only JSON manifest");
    expect(authorizationManifest).toContain("record only its reference");
  });

  it("keeps public worker routing provider-neutral and user-overridable", () => {
    const publicContract = [skill, workflow, template, persistentSkill].join("\n");
    expect(publicContract).toContain("user Skill");
    expect(publicContract).toContain("provider-neutral");
    expect(publicContract).not.toMatch(/\b(?:Luna|Terra|Sol)\b/);
  });
});
