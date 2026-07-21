import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-skills-and-authorization", () => {
  it("requires concrete examples and material-boundary rationale", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const combined = `${capture}\n${template}\n${workflow}`;

    expect(combined).toMatch(/Every description must include at least one concrete example/i);
    expect(combined).toMatch(/meaningful choice, trade-off, or scope boundary/i);
    expect(combined).toMatch(/why this approach is reasonable/i);
    expect(combined).toMatch(
      /why the boundary belongs here|why the work stops at this boundary|why the boundary is set there/i,
    );
    expect(combined).toMatch(/do not invent a rationale|no material choice or boundary/i);
    expect(combined).toMatch(/cold-start reader/i);
    expect(combined).toMatch(/reproduction, inspection, or comparison/i);
    expect(combined).toMatch(/Do not fabricate an example|do not claim the Task Work is ready/i);
  });

  it("routes external Skills through one host-owned, authorization-safe contract", () => {
    const routing = reference("external-skill-routing.md");

    expect(routing).toContain("invocation_mode: model_allowed | user_only | unknown");
    expect(routing).toContain("phase: analysis | planning | execution | delivery | review");
    expect(routing).toContain("necessity: required_capability | preferred_method | explicit_only");
    expect(routing).toContain("missing_behavior: wait | native_fallback | skip_nonblocking");
    expect(routing).toContain("authorization_effect: none");
    expect(routing).toContain("disable-model-invocation: true");
    expect(routing).toContain("declined");
    expect(routing).toContain("install_offered");
    expect(routing).toContain("pending_user_decision");
    expect(routing).toContain("model_fallback");
    expect(routing).toContain("capability_pack_drift");
    expect(routing).toMatch(/Do not reopen\s+item-by-item installation choices/i);
    expect(routing).toMatch(/model_allowed[\s\S]*silently/i);
    expect(routing).toMatch(/rediscover[\s\S]*reload/i);
    expect(routing).toContain("pipeline_required");
    expect(routing).toContain("post_finalizer_grill_me_required");
    expect(routing).toMatch(/grill-finalizer[\s\S]*temporary candidate[\s\S]*grill-me/i);
    expect(routing).toMatch(
      /interactive[\s\S]*one question[\s\S]*wait[\s\S]*Unattended[\s\S]*auto-adopt/i,
    );
    expect(routing).toMatch(/only[\s\S]*relevant[\s\S]*(?:provider|reviewer)/i);
    expect(routing).toMatch(/suggesting installation[\s\S]*does not authorize/i);
    expect(routing).toMatch(/Do not guess\s+an installation command/);
    expect(routing).toContain("Project and Granoflow rules take precedence");
    expect(routing).toMatch(/does not\s+authorize implementation/);
    expect(routing).toMatch(/preferred_method[\s\S]*does not[\s\S]*waiting/i);
    expect(routing).toMatch(/explicit_only[\s\S]*never auto-discovered/i);
    expect(routing).toMatch(/全仓 commit push[\s\S]*instruction[\s\S]*authorization/i);
    expect(routing).not.toContain("Do not pause that fallback");
  });

  it("consumes a hash-verified delegated authorization before repeating a phase prompt", () => {
    const workflow = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
      "utf8",
    );
    const template = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-template.md",
      "utf8",
    );
    const waiting = readFileSync(
      "skills/granoflow-agent-workflow/references/waiting-for-user-input.md",
      "utf8",
    );
    const combined = `${workflow}\n${template}\n${waiting}`;

    expect(combined).toContain("granoflow_delegated_authorization_skill");
    expect(combined).toContain("authorizationOwnerTaskId");
    expect(combined).toContain("attachmentSha256");
    expect(combined).toContain("receiptVerified");
    expect(combined).toContain("analysisConfirmation");
    expect(combined).toContain("planningPermission");
    expect(combined).toContain("planConfirmation");
    expect(combined).toContain("executionAuthorization");
    expect(combined).toMatch(/decision=allowed[\s\S]*continue/i);
    expect(combined).toMatch(/decision=denied[\s\S]*waiting/i);
    expect(combined).toMatch(/tag[\s\S]*(?:not|never)[\s\S]*authorization/i);
  });

  it("waits only for required helpers and keeps optional helpers nonblocking", () => {
    const routing = reference("external-skill-routing.md");
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const readme = readFileSync("README.md", "utf8");
    const active = `${routing}\n${workflow}\n${template}\n${skill}\n${readme}`;

    expect(template).toContain("install_offered");
    expect(template).toContain("pending_user_decision");
    expect(workflow).toMatch(/model_allowed[\s\S]*grill-finalizer/);
    expect(workflow).toContain("post_finalizer_grill_me_required");
    expect(workflow).toMatch(/grill-me[\s\S]*pipeline/i);
    expect(workflow).toMatch(/required_capability[\s\S]*pending_user_decision[\s\S]*waiting/i);
    expect(workflow).toMatch(/preferred_method[\s\S]*native_fallback[\s\S]*continue/i);
    expect(workflow).toMatch(/preferred_method[\s\S]*native_fallback[\s\S]*continue/i);
    expect(active).toMatch(/post-finalizer[\s\S]*grill-me[\s\S]*pipeline/i);
    expect(active).toMatch(/not (?:install|invoke)[\s\S]*(?:entire|whole) (?:family|series)/i);
    expect(active).toMatch(/installation authorization[\s\S]*does not authorize/i);
    expect(active).toMatch(
      /Bundle[\s\S]*installer[\s\S]*(?:license|licensing)[\s\S]*(?:redistribut|distribution)/i,
    );
    expect(active).not.toContain("immediately use bundled Grill");
    expect(active).not.toContain("falls back immediately");
    expect(active).not.toContain("immediately use bundled Grill");
  });

  it("records capability decisions only when Task Work triggers Skill routing", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const legacyAnalysis = reference("task-analysis-execution.md");
    const legacyPlan = reference("task-plan-workflow.md");

    expect(template).toContain("Capability And Skill Routing");
    expect(template).toContain("skill_routing: not_triggered");
    expect(template).toContain("external-skill-routing.md");
    expect(workflow).toContain("at most one directly relevant");
    expect(workflow).toContain("Never preload all Profiles");
    expect(legacyAnalysis).toContain("task-work-document-workflow.md");
    expect(legacyPlan).toContain("task-work-document-workflow.md");
  });
});
