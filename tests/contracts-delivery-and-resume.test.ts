import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-delivery-and-resume", () => {
  it("publishes thin software routing without coupling every task to Matt Skills", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const profile = reference("task-analysis-profile-software-development.md");
    const readme = readFileSync("README.md", "utf8");

    expect(skill).toContain("references/external-skill-routing.md");
    expect(skill).toContain("invocation permission");
    expect(profile).toMatch(/code, tests, builds, or an\s+engineering repository/);
    expect(profile).toContain("host-visible Skill metadata");
    expect(profile).toMatch(/Ordinary copywriting, manga, animation/);
    expect(readme).toContain("External Skill routing");
    expect(readme).toContain("user-only Skills");
    expect(readme).toContain("model capability fallback");
    expect(readme).toMatch(/does not scan or modify the host's global Skill environment/);
  });

  it("defines immutable Delivery with hash readback and single completion ownership", () => {
    const template = reference("task-delivery-template.md");
    const workflow = reference("task-delivery-workflow.md");

    for (const section of [
      "Final Outcome",
      "Deliverables",
      "Differences From Work Document",
      "Verification Evidence",
      "Residuals And Deferred Work",
      "Handoff And Usage",
      "Traceability",
    ]) {
      expect(template).toContain(section);
    }
    expect(template).toContain("content_sha256");
    expect(template).toContain("source_work_document");
    expect(template).not.toContain("source_analysis:");
    expect(template).not.toContain("source_plan:");
    expect(workflow).toContain("Legacy Delivery may read existing `source_analysis`");
    expect(workflow).toContain("Same filename/version plus same hash");
    expect(workflow).toContain("Filename-only list and HTTP success do not pass");
    expect(workflow).toContain("NodeService");
    expect(workflow).toContain("compatibility finish once");
    expect(workflow).toContain("create and read back Delivery first");
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
});
