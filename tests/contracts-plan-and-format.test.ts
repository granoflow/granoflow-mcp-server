import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-plan-and-format", () => {
  it("selects true-false or multiple-choice cards only when the Note supports them", () => {
    const defaults = readFileSync(
      "skills/granoflow-review-card-draft/references/card-quality-defaults.md",
      "utf8",
    );
    const authoring = reference("review-card-authoring.md");
    expect(defaults).toContain("Use **true/false**");
    expect(defaults).toContain("Use **multiple-choice**");
    expect(defaults).toContain("options field rather than");
    expect(defaults).toContain("Do not force a choice format");
    expect(authoring).toContain("Card's options field");
  });

  it("keeps routine checks in the plan and reserves nodes for costly validation gates", () => {
    const workflow = reference("task-work-document-workflow.md");
    expect(workflow).toContain("Do not create a Granoflow node for every plan step");
    expect(workflow).toContain("deterministic checks such as unit tests, lint");
    expect(workflow).toContain("materially\nexpensive");
    expect(workflow).toContain("explicit opt-in gate");
    expect(workflow).toContain("Do not use a node merely because a test exists");
  });

  it("requires task descriptions to state a concrete failure or risk scenario", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("observed failure");
    expect(capture).toContain("who is affected");
    expect(capture).toContain("observable evidence");
    expect(template).toContain("cannot replace the scenario");
  });

  it("requires titles to expose the user-facing failure or result", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    expect(capture).toContain("user-facing problem, consequence");
    expect(capture).toContain("修复长请求被固定上限提前截断的问题");
    expect(capture).toContain("实现分层超时与移除静态 agent 限制");
    expect(skill).toContain("user-facing failure, consequence");
    expect(skill).toContain("internal architecture terms");
  });

  it("uses the task description as the factual seed for executable Task Work", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("user-facing factual summary");
    expect(workflow).toContain("starting source for Task Work");
    expect(workflow).toContain("must not invent facts");
    expect(template).toContain("factual seed");
    expect(template).toContain("merely repeats a title");
  });

  it("blocks persistence when the description fails the 30-second recall gate", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    expect(capture).toContain("Description Job: 30-Second Recall");
    expect(capture).toContain("Pre-Write Recall Gate");
    expect(capture).toContain(
      "generic workflow prose that could be pasted onto another task unchanged",
    );
    expect(workflow).toContain("30-second recall gate");
    expect(workflow).toContain("task_description_recall_gate_failed");
    expect(workflow).toMatch(/before upload, active-version selection, or completion/);
    expect(skill).toContain("30-second recall gate");
  });
});
