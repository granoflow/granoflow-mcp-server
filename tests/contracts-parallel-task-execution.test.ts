import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const read = (path: string) => readFileSync(path, "utf8");

describe("parallel AI task execution contract", () => {
  const contract = read("skills/granoflow-agent-workflow/references/parallel-task-execution.md");

  it("requires evidence-backed pairwise conflict decisions", () => {
    for (const decision of [
      "parallel_safe",
      "ordered_dependency",
      "write_conflict",
      "side_effect_conflict",
      "unknown",
    ]) {
      expect(contract).toContain(decision);
    }
    expect(contract).toContain("An unknown material write surface is a serialization reason");
    expect(contract).toMatch(/dispatch every task[\s\S]*concurrently/i);
    expect(contract).toContain("host_capacity_limited");
  });

  it("keeps AI work pending and preserves exact execution times", () => {
    expect(contract).toMatch(/`doing` is a human focus state/i);
    expect(contract).toContain("Never set `doing` for AI execution");
    expect(contract).toContain("granoflow_task_history_mutate");
    expect(contract).toContain("granoflow_task_finish");
    expect(contract).toMatch(/Re-read `status=done`, `startedAt`, `endedAt`/);
  });

  it("is consumed by task, milestone, and orchestration owners", () => {
    for (const path of [
      "skills/granoflow-agent-workflow/SKILL.md",
      "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
      "skills/granoflow-agent-workflow/references/task-work-document-template.md",
      "skills/granoflow-milestone-coordination/SKILL.md",
      "skills/granoflow-milestone-coordination/references/milestone-collaboration-workflow.md",
      "skills/granoflow-milestone-coordination/references/milestone-work-document-template.md",
      "skills/granoflow-task-orchestrator/references/end-to-end-orchestration.md",
    ]) {
      expect(read(path)).toContain("parallel-task-execution");
    }
  });
});
