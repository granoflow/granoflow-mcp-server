import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { installToolTestLifecycle } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-review-and-dates", () => {
  it("documents the internal review drafting boundary", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/review-drafting.md",
      "utf8",
    );
    const combined = `${skill}\n${reference}`;

    expect(combined).toContain("Task Review is user-initiated and deferred by default");
    expect(combined).toContain("suggestion or nudge is not permission");
    expect(combined).toContain("No periodic review starts from a suggestion alone");
    expect(combined).toContain("show a draft of the fields");
    expect(combined).toContain("Daily-review synthesis imports remain");
    expect(combined).toContain("does not automatically write taskReview or Review Cards");
    expect(combined).toContain("Never present inferred mood");
    expect(combined).toContain("review July");
    expect(combined).toContain("写周报");
  });

  it("documents the project-aware default deadline for milestone creation", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const taskCapture = readFileSync(
      "skills/granoflow-agent-workflow/references/discussed-requirement-task-capture.md",
      "utf8",
    );

    expect(skill).toContain("## Milestone Creation Deadlines");
    expect(skill).toContain("preserve it unchanged");
    expect(skill).toMatch(/strictly\s+next Saturday/);
    expect(skill).toContain("23:59:59.000");
    expect(skill).toContain("seven-day increments");
    expect(skill).toContain("fails closed");
    expect(skill).toContain("## Task Deadlines Within Milestones");
    expect(skill).toMatch(/today, tomorrow, or the milestone\s+deadline/);
    expect(skill).toContain("Do not default every milestone task");
    expect(taskCapture).toContain("A task placed in a milestone must have `dueAt`");
  });

  it("defines weekly review as an interactive, evidence-bounded recall session", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/review-drafting.md",
      "utf8",
    );
    const combined = `${skill}\n${reference}`;

    expect(combined).toContain("target week dates and the caller's local time zone");
    expect(combined).toContain("3–5 high-information recall cues");
    expect(combined).toContain("one cue at a time");
    expect(combined).toMatch(/may skip any\s+question/);
    expect(combined).toContain("recorded fact");
    expect(combined).toContain("user-confirmed interpretation");
    expect(combined).toContain("tentative inference");
    expect(combined).toContain("unknown");
    expect(combined).toContain("sensitive, relationship, or emotional details");
    expect(combined).toContain("partial confirmation");
    expect(combined).toMatch(/does not automatically\s+create tasks, reminders, cards/);
  });

  it("defines monthly review as an interactive, open-ended recall session", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/review-drafting.md",
      "utf8",
    );
    const combined = `${skill}\n${reference}`;

    expect(combined).toContain("target month dates and the caller's local time zone");
    expect(combined).toContain("3–5 high-information recall cues");
    expect(combined).toContain("monthly main thread");
    expect(combined).toContain("unrecorded but important");
    expect(combined).toContain("may skip any prompt");
    expect(combined).toContain("free-form account");
    expect(combined).toMatch(/unavailable evidence does not\s+mean no progress/);
    expect(combined).toContain("minimum necessary facts");
    expect(combined).toContain("recorded fact");
    expect(combined).toContain("user-confirmed interpretation");
    expect(combined).toContain("tentative inference");
    expect(combined).toContain("unknown");
    expect(combined).toContain("monthly `content`");
    expect(combined).toMatch(/does not automatically\s+create tasks, reminders, cards/);
  });
});
