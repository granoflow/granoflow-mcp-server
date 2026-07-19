import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const agentReference = (name: string) =>
  readFileSync("skills/granoflow-agent-workflow/references/" + name, "utf8");

describe("requirement intake and traceability contracts", () => {
  const intake = agentReference("requirement-intake-and-traceability.md");
  const projectWork = agentReference("project-work-document-template.md");
  const taskWork = agentReference("task-work-document-template.md");
  const taskWorkflow = agentReference("task-work-document-workflow.md");
  const projectSkill = readFileSync("skills/granoflow-project-definition/SKILL.md", "utf8");
  const milestoneSkill = readFileSync("skills/granoflow-milestone-workflow/SKILL.md", "utf8");
  const milestoneTemplate = readFileSync(
    "skills/granoflow-milestone-workflow/references/milestone-work-document-template.md",
    "utf8",
  );

  it("treats imperfect source documents as evidence instead of forms", () => {
    expect(intake).toContain("The inputs are evidence, not forms");
    expect(intake).toContain("product document and user stories");
    expect(intake).toContain("exact filenames");
    expect(intake).toContain("Content outside the expected headings is not noise");
    expect(intake).toContain("Development Plan is not a default user input");
    expect(intake).toContain("never silently merge, prioritize, or discard");
  });

  it("classifies every statement, gap, inference, and conflict", () => {
    for (const contract of [
      "user_stated | inspected_fact | inferred | recommended | unknown",
      "adopted | needs_clarification | conflicting | deferred | out_of_scope | duplicate | inferred",
      "decision_changing",
      "safe_assumption",
      "deferred_unknown",
      "one primary owner layer",
    ]) {
      expect(intake).toContain(contract);
    }
    expect(intake).toContain("Do not use a numeric confidence score");
  });

  it("persists canonical intake and coverage in Project Work YAML", () => {
    for (const field of [
      "requirement_intake:",
      "recommended_minimum_user_inputs:",
      "separately_required_user_inputs: []",
      "team_development_plan_required: false",
      "source_documents:",
      "extra_content_preserved:",
      "conflict_summary:",
      "requirement_coverage:",
      "every_adopted_requirement_has_one_primary_owner:",
    ]) {
      expect(projectWork).toContain(field);
    }
  });

  it("routes stable requirement ids through milestone and task work", () => {
    expect(taskWork).toContain("## Requirement Traceability");
    expect(taskWork).toContain("Project Work canonical requirement ids");
    expect(taskWorkflow).toContain("arbitrary");
    expect(taskWorkflow).toContain("preserve extra requirements");
    expect(milestoneTemplate).toContain("## Requirement Coverage");
    expect(milestoneTemplate).toMatch(/never\s+copy the complete product ledger/);
    expect(projectSkill).toContain("requirement-intake-and-traceability");
    expect(milestoneSkill).toContain("requirement-intake-and-traceability");
  });
});
