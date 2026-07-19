import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-card-and-memory", () => {
  it("applies Markdown semantics to the complete attached Task Work Document", () => {
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    expect(workflow).toContain("Task Work Markdown Quality");
    expect(workflow).toContain("attached Task Work Document");
    expect(template).toContain("complete attached Task Work Document");
    expect(template).toContain("is not a finished document");
  });

  it("reports local drafts honestly and reconciles after Local API recovery", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const workflow = reference("task-work-document-workflow.md");
    const combined = `${skill}\n${workflow}`;

    for (const state of [
      "bound_local_draft",
      "unbound_local_draft",
      "no_local_draft",
      "upload_blocked_api_unreachable",
      "attachment_readback_pending",
      "active_not_established",
      "reconciliation_required",
    ]) {
      expect(combined).toContain(state);
    }
    expect(combined).toContain("configuration_shadowed_by_env");
    expect(combined).toContain("reachable_auth_required");
    expect(combined).toMatch(/re-read the task, attachments, nodes, and task revision/i);
    expect(combined).toMatch(/execution\s+authorization does not survive/i);
    expect(combined).toMatch(/Only App-owned content or SHA-256 readback/i);
  });

  it("uses one lifecycle card-checkpoint owner across all task phases", () => {
    const owner = readFileSync(
      "skills/granoflow-review-card-draft/references/lifecycle-card-checkpoints.md",
      "utf8",
    );
    const work = reference("task-work-document-template.md");
    const delivery = reference("task-delivery-template.md");
    const review = reference("task-review-template.md");
    const completion = reference("task-completion-summary-template.md");

    expect(owner).toContain("task_work | execution | delivery | deferred_review");
    expect(owner).toContain(
      "status: completed | partial | deferred | conflict | verification_failed | not_applicable",
    );
    expect(owner).toContain("change_summary: changed | unchanged");
    expect(owner).toContain("approvedOperationIds");
    expect(owner).toContain("must not persist `previewToken`");
    expect(owner).toContain("projectTaskRequired=false");
    expect(owner).toContain("inboxTaskAuthoring=true");
    expect(owner).toContain("uncategorizedDeckFallback=true");
    expect(owner).toContain("task_not_found");

    for (const phaseTemplate of [delivery, review]) {
      expect(phaseTemplate).toContain("Card Checkpoint");
      expect(phaseTemplate).toContain("lifecycle-card-checkpoints.md");
    }
    expect(work).toContain("card_checkpoint: not_triggered");
    expect(work).toContain("Knowledge/Card Delta Trigger");
    expect(delivery).toContain("Disposition: accepted | superseded | deferred");
    expect(delivery).toContain("Card operation IDs");
    expect(completion).toContain("Delivery Card Checkpoint");
    expect(completion).toContain("Deferred Card Work");
    expect(completion).toContain("Card Verification Failures");
    expect(completion).not.toContain("card_checkpoint:");
  });

  it("ends every review with an open-ended zero-write Note/Card approval session", () => {
    const cardSkill = readFileSync("skills/granoflow-review-card-draft/SKILL.md", "utf8");
    const checkpoints = readFileSync(
      "skills/granoflow-review-card-draft/references/lifecycle-card-checkpoints.md",
      "utf8",
    );
    const reviewDrafting = reference("review-drafting.md");
    const taskReview = reference("task-review-workflow.md");
    const unattended = reference("unattended-interaction-contract.md");
    const combined = `${cardSkill}\n${checkpoints}\n${reviewDrafting}\n${taskReview}\n${unattended}`;

    expect(cardSkill).toContain("## Review-Ending Authoring Session");
    expect(combined).toContain("writesPerformed: false");
    expect(combined).toMatch(/complete planned Note\/Card\s+set/i);
    expect(combined).toContain("open-ended editing conversation");
    expect(combined).toMatch(/addition or edit as a draft change, not write\s+approval/i);
    expect(combined).toMatch(/latest\s+unchanged preview/i);
    expect(combined).toContain("只建第二张");
    expect(combined).toContain("partial approval");
    expect(combined).toContain("practiceReady: true");
    expect(taskReview).toContain("final interactive authoring");
    expect(unattended).toContain("blocker_class: subjective_acceptance");
    expect(unattended).toMatch(
      /Review Note\/Card authoring is also excluded from unattended authorization/i,
    );
  });

  it("uses base plus composable profiles without public local plan numbers", () => {
    const work = reference("task-work-document-template.md");
    const legacyAnalysis = reference("task-analysis-template.md");
    const legacyPlan = reference("task-plan-template.md");

    expect(work).toContain("profiles: [] | [learning] | [software_development]");
    expect(work).not.toMatch(/project_(73|76)/);
    expect(legacyAnalysis).toContain("legacy");
    expect(legacyPlan).toContain("legacy");
    expect(legacyAnalysis).toContain("Do not use it to create");
    expect(legacyPlan).toContain("Do not use it to create");
  });

  it("keeps Work Document nodes personal without assigning an owner", () => {
    const template = reference("task-work-document-template.md");

    expect(template).toContain("Execution Mode: agent | user_action | agent_then_user_acceptance");
    expect(template).not.toContain("Owner: AI | user | both");
    expect(template).toMatch(/The task always belongs\s+to the current individual user/);
    expect(template).toMatch(/The Agent is an execution tool, not the task\s+owner/);
  });
});
