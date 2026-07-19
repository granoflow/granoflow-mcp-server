import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

type Requirement = {
  id: string;
  source_refs: string[];
  source_locators: string[];
  disposition: string;
  owner_layer: string;
  acceptance_ids: string[];
};

const fixture = JSON.parse(readFileSync("tests/fixtures/requirement-intake-e2e.json", "utf8")) as {
  sources: Array<{ id: string; statements: Array<{ text: string }> }>;
  projectWork: {
    requirements: Requirement[];
    gaps: { decision_changing: string[] };
    questions: Array<{ requirement_id: string }>;
  };
  milestoneWork: {
    requirement_ids: string[];
    acceptance_ids: string[];
    blocked_requirement_ids: string[];
  };
  taskWork: Array<{ requirement_ids: string[]; acceptance_ids: string[] }>;
  forbiddenOutputs: string[];
};

describe("imperfect product document and user-story intake e2e fixture", () => {
  it("preserves requirements found outside expected headings with source locators", () => {
    const sourceIds = new Set(fixture.sources.map((source) => source.id));
    const adopted = fixture.projectWork.requirements.filter(
      (requirement) => requirement.disposition === "adopted",
    );

    expect(fixture.sources[0]?.statements[0]?.text).toContain("完全离线");
    expect(fixture.sources[0]?.statements[0]?.text).toContain("像纸质书一样安静");
    for (const requirement of adopted) {
      expect(requirement.source_refs.length).toBeGreaterThan(0);
      expect(requirement.source_refs.every((source) => sourceIds.has(source))).toBe(true);
      expect(requirement.source_locators.length).toBeGreaterThan(0);
      expect(requirement.owner_layer).not.toBe("unassigned");
      expect(requirement.acceptance_ids.length).toBeGreaterThan(0);
    }
  });

  it("turns the missing migration decision into one bounded question", () => {
    expect(fixture.projectWork.gaps.decision_changing).toEqual(["R-MIGRATION"]);
    expect(fixture.projectWork.questions).toEqual([
      expect.objectContaining({ requirement_id: "R-MIGRATION" }),
    ]);
    expect(fixture.milestoneWork.blocked_requirement_ids).toEqual(["R-MIGRATION"]);
  });

  it("keeps milestone and task coverage consistent without generating a development plan", () => {
    const milestoneRequirementIds = new Set(fixture.milestoneWork.requirement_ids);
    const milestoneAcceptanceIds = new Set(fixture.milestoneWork.acceptance_ids);
    const tracedRequirementIds = fixture.taskWork.flatMap((task) => task.requirement_ids);
    const tracedAcceptanceIds = fixture.taskWork.flatMap((task) => task.acceptance_ids);

    expect(new Set(tracedRequirementIds)).toEqual(milestoneRequirementIds);
    expect(new Set(tracedAcceptanceIds)).toEqual(milestoneAcceptanceIds);
    expect(fixture.forbiddenOutputs).toEqual(["08-development-plan.md"]);
  });
});
