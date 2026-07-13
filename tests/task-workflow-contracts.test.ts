import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("Task Delivery and Deferred Task Review contracts", () => {
  it("uses one lifecycle card-checkpoint owner across all task phases", () => {
    const owner = readFileSync(
      "skills/granoflow-review-card-draft/references/lifecycle-card-checkpoints.md",
      "utf8",
    );
    const analysis = reference("task-analysis-template.md");
    const plan = reference("task-plan-template.md");
    const delivery = reference("task-delivery-template.md");
    const review = reference("task-review-template.md");
    const completion = reference("task-completion-summary-template.md");

    expect(owner).toContain("analysis | plan | execution | delivery | deferred_review");
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

    for (const phaseTemplate of [analysis, plan, delivery, review]) {
      expect(phaseTemplate).toContain("Card Checkpoint");
      expect(phaseTemplate).toContain("lifecycle-card-checkpoints.md");
    }
    expect(plan).toContain("Knowledge/Card Delta Trigger");
    expect(delivery).toContain("Disposition: accepted | superseded | deferred");
    expect(delivery).toContain("Card operation IDs");
    expect(completion).toContain("Delivery Card Checkpoint");
    expect(completion).toContain("Deferred Card Work");
    expect(completion).toContain("Card Verification Failures");
    expect(completion).not.toContain("card_checkpoint:");
  });

  it("uses base plus composable profiles without public local plan numbers", () => {
    const analysis = reference("task-analysis-template.md");
    const plan = reference("task-plan-template.md");

    expect(analysis).toContain(
      "profiles: [] | [learning] | [software_development] | [learning, software_development]",
    );
    expect(plan).toContain(
      "profiles: [] | [learning] | [software_development] | [learning, software_development]",
    );
    expect(`${analysis}\n${plan}`).not.toMatch(/project_(73|76)/);
    expect(analysis).toContain("This is pre-task analysis");
    expect(plan).toContain("Task Delivery governs what was actually delivered");
  });

  it("defines immutable Delivery with hash readback and single completion ownership", () => {
    const template = reference("task-delivery-template.md");
    const workflow = reference("task-delivery-workflow.md");

    for (const section of [
      "Final Outcome",
      "Deliverables",
      "Differences From Analysis",
      "Differences From Plan",
      "Verification Evidence",
      "Residuals And Deferred Work",
      "Handoff And Usage",
      "Traceability",
    ]) {
      expect(template).toContain(section);
    }
    expect(template).toContain("content_sha256");
    expect(workflow).toContain("Same filename/version plus same hash");
    expect(workflow).toContain("Filename-only list and HTTP success do not pass");
    expect(workflow).toContain("NodeService");
    expect(workflow).toContain("compatibility finish once");
  });

  it("defines marker-safe resumable Review for inbox tasks", () => {
    const template = reference("task-review-template.md");
    const workflow = reference("task-review-workflow.md");

    expect(template).toContain("<!-- granoflow-task-review:v1:start -->");
    expect(template).toContain("<!-- granoflow-task-review:v1:end -->");
    expect(template).toContain("review_revision");
    expect(template).toContain("review_operation_id");
    expect(template).toContain("acceptance latency");
    expect(workflow).toContain("gaps over five minutes");
    expect(workflow).toContain("Completed inbox task");
    expect(workflow).toContain("expectedUpdatedAt");
    expect(workflow).toContain("Never replay completed steps");
  });

  it("defines completion-summary and milestone managed blocks", () => {
    const completion = reference("task-completion-summary-template.md");
    const promotion = reference("context-promotion-entry.md");

    expect(completion).toContain("granoflow-task-completion-summary:v1:start");
    expect(completion).toContain("Review status: pending | completed");
    expect(completion).toContain("task_completion_summary_markers_invalid");
    expect(promotion).toContain("granoflow-milestone-context:v1:start");
    expect(promotion).toContain("project_snapshot.yaml");
    expect(promotion).toContain("project_rules.yaml");
    expect(promotion).toContain("semantic similarity");
  });

  it("keeps ordinary completion separate from Review and cards in public docs", () => {
    const publicText = [
      readFileSync("README.md", "utf8"),
      readFileSync("docs/user-install-demo.md", "utf8"),
      readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8"),
    ].join("\n");

    expect(publicText).toContain("Deferred Task Review");
    expect(publicText).toContain("does not automatically create");
    expect(publicText).not.toContain("factual `taskReview` may be written automatically");
  });

  it("allows an explicitly requested daily review to orchestrate missing task reviews", () => {
    const workflow = reference("task-review-workflow.md");

    expect(workflow).toContain("explicitly requested daily review");
    expect(workflow).toContain("daily task ledger");
    expect(workflow).toContain("daily skill does not directly");
    expect(workflow).toContain("card outcome");
  });
});
