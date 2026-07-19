import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-delivery-and-review", () => {
  it("makes Task Work a source-grounded cold-start execution manual", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");

    expect(template).toContain("## Reader Summary");
    expect(template).toContain("## Facts And Source Discipline");
    expect(template).toContain(
      "directly inspected source files, screenshots, logs, or runtime state",
    );
    expect(template).toContain("### Step N: <plain-language action + result>");
    expect(template).toContain("Performer: agent | user | agent_then_user | shared");
    expect(template).toContain("client\nvisit");
    expect(template).toContain("## Cold-Handoff Completion Gate");
    expect(workflow).toContain("cold-start execution\nmanual");
    expect(workflow).toContain("task_work_cold_handoff_failed");
    expect(workflow).toContain("task_work_source_evidence_insufficient");
    expect(workflow).toContain("filename, path, title, or completion status proves only");
  });

  it("audits completed historical work without inventing a future plan", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    for (const document of [template, workflow, skill]) {
      expect(document).toContain("decision=completion_audit");
    }
    for (const section of [
      "Original Problem Or Event",
      "Actual Actions",
      "Actual Evidence",
      "Outcome And Differences",
      "Residuals / Unknowns",
    ]) {
      expect(template).toContain(section);
      expect(workflow).toContain(section);
    }
    expect(template).toContain("Do not invent a future plan");
    expect(workflow).toContain("Do not write a prospective Execution Plan");
  });

  it("limits Task Work to an execution slot and one post-completion revision", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    for (const document of [template, workflow, skill]) {
      expect(document).toContain("post_completion_revision");
      expect(document).toMatch(/at\s+most two/);
    }
    expect(template).toContain("document_slot: execution | post_completion_revision");
    expect(template).toContain("task_work_slot_count_exceeded");
    expect(template).toContain("Subsequent corrections update");
    expect(workflow).toContain("task_work_slot_identity_invalid");
    expect(workflow).toContain("unfinished `execution` slot");
    expect(workflow).toContain("Create that slot only once");
    expect(workflow).toContain("replacement is transactional");
    expect(skill).toContain("Before completion, every edit replaces the");
    expect(skill).toContain("later edits never create another slot");
  });

  it("keeps each problem as a separate paragraph and diagrams supplemental", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("each distinct problem as its own natural-language paragraph");
    expect(capture).toContain("does not replace it");
    expect(template).toContain("each problem as a separate natural-language paragraph");
  });

  it("requires semantic Markdown formatting for task writing", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("**bold**");
    expect(capture).toContain("_italics_");
    expect(capture).toContain("fenced code blocks");
    expect(template).toContain("Use Markdown semantically");
    expect(template).toContain("literal commands, APIs, fields, paths");
    expect(template).toContain("There is no formatting quota");
    expect(template).toContain("Plain paragraphs are valid");
  });
});
