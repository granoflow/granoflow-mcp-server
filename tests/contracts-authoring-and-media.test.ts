import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-authoring-and-media", () => {
  it("keeps the initial draft analysis-only and gates attachment on two bundled Grills", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const routing = reference("external-skill-routing.md");
    const combined = `${template}\n${workflow}\n${skill}`;

    expect(combined).toMatch(/initial draft[\s\S]*Analysis.only/i);
    expect(combined).toMatch(/(?:must not|Do not) (?:contain|draft|add)[\s\S]*Execution Plan/i);
    expect(combined).toMatch(/Analysis Grill[\s\S]*before\s+Planning/i);
    expect(combined).toMatch(/automatically tell the user[\s\S]*readiness review/i);
    expect(combined).toMatch(/Execution Readiness Grill[\s\S]*before\s+(?:any\s+)?upload/i);
    for (const readiness of [
      "authorization",
      "login state",
      "credentials",
      "keys",
      "secret availability",
      "required data",
      "source materials",
      "tools and environment",
    ]) {
      expect(combined).toContain(readiness);
    }
    expect(combined).toMatch(/never (?:copy|persist)[\s\S]*secret value/i);
    expect(combined).toMatch(/upload does\s+not authorize execution/i);
    expect(workflow).toMatch(
      /analysis_grill_status=passed[\s\S]*readiness_grill_status=passed[\s\S]*uploaded/i,
    );
    expect(workflow).toMatch(
      /before the first authorized execution action[\s\S]*status=doing[\s\S]*App records/i,
    );
    expect(workflow).toMatch(/Analysis, Planning[\s\S]*must leave the task `pending`/i);
    expect(routing).toMatch(/MCP-bundled[\s\S]*mandatory phase gates/i);
    expect(routing).toMatch(/grill-finalizer[\s\S]*does not replace/i);
    for (const forbiddenHeading of [
      "## Grill Review",
      "## Analysis Grill",
      "## Execution Readiness Grill",
    ]) {
      expect(template).not.toContain(forbiddenHeading);
    }
    expect(combined).toMatch(/Grill[\s\S]*invisible authoring (?:gate|pass)/i);
    expect(combined).toMatch(/findings[\s\S]*revis(?:e|ing)[\s\S]*relevant[\s\S]*section/i);
    expect(combined).toMatch(/standalone Grill (?:heading|section)[\s\S]*forbidden/i);
    expect(combined).toMatch(/phase result[\s\S]*analysis_grill_status/i);
    expect(combined).toMatch(
      /(?:every completed bundled Grill|either bundled Grill)[\s\S]*full[\s-]*clean rewrite/i,
    );
    expect(combined).toMatch(/new versioned local (?:document|path|file)[\s\S]*work_version \+ 1/i);
    expect(combined).toMatch(/validate[\s\S]*delete the prior local file/i);
    expect(combined).toMatch(
      /only[\s\S]*rewritten (?:path|document|file)[\s\S]*hash[\s\S]*upload/i,
    );
    expect(combined).toContain("post_grill_rewrite_failed");
    expect(combined).toContain("post_grill_rewrite_required");
  });

  it("keeps comic as the static default and animation as an explicit extension", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const visualNarrative = reference("visual-narrative-task-work.md");

    expect(template).toContain("domain: <optional domain such as visual_narrative>");
    expect(template).toContain("task_mode: <optional domain mode such as comic | animation>");
    expect(workflow).toContain("visual-narrative-task-work.md");
    expect(workflow).toContain("Visual Narrative Mode");
    expect(visualNarrative).toContain("If the user does not specify a mode, default to `comic`");
    expect(visualNarrative).toContain(
      "Do not add timeline, motion, audio, transition, encoding, or playback nodes",
    );
    expect(visualNarrative).toContain("only after the user explicitly requests");
    expect(visualNarrative).toContain("Analysis confirmation does not authorize Planning");
    expect(visualNarrative).toContain("animation extension must not invalidate");
  });

  it("defines notes as the explanation and cards as study projections", () => {
    const cardSkill = readFileSync("skills/granoflow-review-card-draft/SKILL.md", "utf8");
    const defaults = readFileSync(
      "skills/granoflow-review-card-draft/references/card-quality-defaults.md",
      "utf8",
    );
    const authoring = reference("review-card-authoring.md");

    expect(cardSkill).toContain("one durable Note");
    expect(cardSkill).toContain("more concise front/back Cards");
    expect(defaults).toContain("two explicit components");
    expect(defaults).toContain("canonical explanation");
    expect(defaults).toContain("multiple independent recall units");
    expect(defaults).toMatch(/at least\s+one concrete example/);
    expect(defaults).toContain("plain-language analogy");
    expect(cardSkill).toMatch(/Every Note must contain at\s+least\s+one concrete example/);
    expect(
      readFileSync(
        "skills/granoflow-review-card-draft/references/lifecycle-card-checkpoints.md",
        "utf8",
      ),
    ).toContain("Before preview, validate every proposed Note");
    expect(authoring).toContain("two-part artifact");
  });

  it("defines thread image inspection and destination routing", () => {
    const visualEvidence = reference("thread-visual-evidence.md");
    expect(visualEvidence).toContain("Inventory the images actually present");
    expect(visualEvidence).toContain("task evidence");
    expect(visualEvidence).toContain("Note source/example");
    expect(visualEvidence).toContain("Card");
    expect(visualEvidence).toContain("read back the destination");
    expect(visualEvidence).toContain("visual_evidence: none");
  });
});
