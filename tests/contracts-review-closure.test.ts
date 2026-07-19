import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-review-closure", () => {
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
