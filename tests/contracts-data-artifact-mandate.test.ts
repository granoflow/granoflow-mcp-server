import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const workflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
  "utf8",
);
const taskTemplate = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-template.md",
  "utf8",
);
const quality = readFileSync(
  "skills/granoflow-agent-workflow/references/task-authoring-quality-contract.md",
  "utf8",
);
const delivery = readFileSync(
  "skills/granoflow-agent-workflow/references/task-delivery-profile-software-development.md",
  "utf8",
);
const projectTemplate = readFileSync(
  "skills/granoflow-agent-workflow/references/project-work-document-template.md",
  "utf8",
);

describe("data attachment sync mandate contracts", () => {
  it("requires project data attachments and fail-closed stale delivery", () => {
    expect(workflow).toContain("Data Attachment Sync Mandate");
    expect(workflow).toContain("data_artifact_stale");
    expect(workflow).toContain("data_model_attachment");
    expect(workflow).toContain("json_contracts_attachment");
    expect(workflow).toContain("constants_catalog_attachment");
    expect(workflow).toMatch(/data_persistence: none[\s\S]*must not[\s\S]*business database/i);

    expect(taskTemplate).toContain("data_artifact_stale");
    expect(taskTemplate).toMatch(/DB schema, JSON contracts, or shared constants/i);

    expect(quality).toContain("data_artifact_stale");
    expect(quality).toContain("data_model_attachment");
    expect(quality).toContain("json_contracts_attachment");
    expect(quality).toContain("constants_catalog_attachment");

    expect(delivery).toContain("data attachment sync");
    expect(delivery).toContain("data_artifact_stale");

    expect(projectTemplate).toContain("code_must_match_data_attachments: true");
    expect(projectTemplate).toContain("data_artifact_stale");
  });

  it("keeps full schemas out of Project Work body YAML", () => {
    expect(projectTemplate).toMatch(/Do NOT embed[\s\S]*full field schemas/i);
    expect(quality).toMatch(/Do not embed[\s\S]*JSON shapes or constant catalogs/i);
    expect(workflow).toMatch(/Do not embed full schemas/i);
  });

  it("requires Analysis to challenge unreasonable data attachments", () => {
    expect(workflow).toContain("Analysis-time schema challenge");
    expect(workflow).toMatch(
      /During \*\*Analysis\*\*[\s\S]*unreasonable[\s\S]*raise it explicitly/i,
    );
    expect(workflow).toMatch(
      /Analysis Grill[\s\S]*unreasonable project data\s+attachments or dependency selections were challenged/i,
    );
    expect(taskTemplate).toMatch(
      /unreasonable project\s+data attachment or dependency selection was raised/i,
    );
    expect(quality).toMatch(
      /During Task \*\*Analysis\*\*[\s\S]*unreasonable[\s\S]*propose a\s+revision/i,
    );
  });
});
