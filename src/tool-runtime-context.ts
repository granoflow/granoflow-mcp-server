import { z } from "zod";

import { requestGranoflowApi } from "./api.js";
import { compactResource, extractItems } from "./tool-runtime-authoring.js";
import { requestPreviewWithMeta, supportsContextSteward } from "./tool-runtime-capabilities.js";
import { listPathFor } from "./tool-task-lifecycle.js";
import { compactRecord } from "./tool-runtime-core.js";
import type { GranoflowRecord, ResourceKind } from "./tools.js";
import { milestoneArchiveClosureSchema } from "./tools.js";

export async function resolveResourceById(kind: ResourceKind, id: string) {
  const result = await requestGranoflowApi({ path: listPathFor(kind) });
  if (!result.ok) {
    return { result, resource: null };
  }
  return {
    result,
    resource: extractItems(result).find((item) => item.id === id) ?? null,
  };
}

export function isArchivedResource(resource: GranoflowRecord): boolean {
  return resource.status === "archived";
}

export async function contextStewardStatus(input: { projectId?: string }) {
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  const projectsResult = await requestGranoflowApi({ path: "/v1/projects" });
  const milestonesResult = await requestGranoflowApi({ path: "/v1/milestones" });
  const projects = projectsResult.ok ? extractItems(projectsResult) : [];
  const milestones = milestonesResult.ok
    ? extractItems(milestonesResult).filter(
        (milestone) => !input.projectId || milestone.projectId === input.projectId,
      )
    : [];
  return {
    ok: toolsResult.ok && projectsResult.ok && milestonesResult.ok,
    code: toolsResult.ok && projectsResult.ok && milestonesResult.ok ? "ok" : "partial",
    data: {
      contextStewardAdvertised: toolsResult.ok && supportsContextSteward(toolsResult),
      archivedMilestoneOrdinaryUpdates: false,
      projectId: input.projectId,
      projects: projects
        .filter((project) => !input.projectId || project.id === input.projectId)
        .map(compactResource),
      activeMilestones: milestones
        .filter((milestone) => !isArchivedResource(milestone))
        .map(compactResource),
      archivedMilestones: milestones.filter(isArchivedResource).map(compactResource),
      policy: {
        projectDescription: "living_context",
        activeMilestoneDescription: "living_context",
        archivedMilestoneDescription: "final_snapshot_for_ordinary_mcp_workflow",
      },
    },
    runtime: toolsResult.runtime,
  };
}

export async function projectContextUpdate(input: {
  projectId: string;
  description: string;
  evidenceSummary: string;
  dryRun?: boolean;
}) {
  const body = { description: input.description };
  const options = {
    method: "PATCH" as const,
    path: `/v1/projects/${input.projectId}`,
    body,
  };
  if (input.dryRun !== false) {
    return requestPreviewWithMeta(options, {
      contextSteward: {
        target: "project",
        evidenceSummary: input.evidenceSummary,
        descriptionPolicy: "living_context",
      },
    });
  }
  return requestGranoflowApi(options);
}

export async function milestoneContextUpdate(input: {
  milestoneId: string;
  projectId?: string;
  description: string;
  evidenceSummary: string;
  dryRun?: boolean;
}) {
  const { result, resource } = await resolveResourceById("milestone", input.milestoneId);
  if (!result.ok) {
    return result;
  }
  if (!resource) {
    return {
      ok: false,
      code: "milestone_not_found",
      error: { message: "Granoflow milestone was not found." },
      runtime: result.runtime,
    };
  }
  if (isArchivedResource(resource)) {
    return {
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
      data: {
        milestone: compactResource(resource),
        policy: "archived_milestone_description_is_final_snapshot",
      },
      error: {
        message: "Archived milestone descriptions are final snapshots for ordinary MCP workflows.",
      },
      runtime: result.runtime,
    };
  }

  const body = compactRecord({
    projectId: input.projectId,
    description: input.description,
  });
  const options = {
    method: "PATCH" as const,
    path: `/v1/milestones/${input.milestoneId}`,
    body,
  };
  if (input.dryRun !== false) {
    return requestPreviewWithMeta(options, {
      contextSteward: {
        target: "active_milestone",
        evidenceSummary: input.evidenceSummary,
        descriptionPolicy: "living_context",
        currentMilestone: compactResource(resource),
      },
    });
  }
  return requestGranoflowApi(options);
}

export async function milestoneContextArchive(input: {
  milestoneId: string;
  projectId: string;
  closure: z.infer<typeof milestoneArchiveClosureSchema>;
  dryRun?: boolean;
  confirmArchive?: boolean;
}) {
  const { result, resource } = await resolveResourceById("milestone", input.milestoneId);
  if (!result.ok) {
    return result;
  }
  if (!resource) {
    return {
      ok: false,
      code: "milestone_not_found",
      error: { message: "Granoflow milestone was not found." },
      runtime: result.runtime,
    };
  }
  if (isArchivedResource(resource)) {
    return {
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
      data: {
        milestone: compactResource(resource),
        policy: "archived_milestone_description_is_final_snapshot",
      },
      error: {
        message: "Archived milestone descriptions are final snapshots for ordinary MCP workflows.",
      },
      runtime: result.runtime,
    };
  }

  const completionSummary = input.closure.completionSummary ?? input.closure.finalOutcome;
  const milestoneDescription =
    input.closure.milestoneDescription ??
    [
      `Final outcome: ${input.closure.finalOutcome}`,
      `Verification: ${input.closure.verification}`,
      `Follow-up moved to: ${input.closure.followUpMovedTo}`,
    ].join("\n");
  const steps = [
    {
      step: "finalize_milestone_context",
      method: "POST",
      path: `/v1/milestones/${input.milestoneId}/archive`,
      body: {
        completionSummary,
        description: milestoneDescription,
      },
      appOwnedArchiveApiAvailable: false,
    },
    {
      step: "update_parent_project_context",
      method: "PATCH",
      path: `/v1/projects/${input.projectId}`,
      body: {
        description: input.closure.projectDescription,
      },
    },
  ];

  if (input.dryRun !== false) {
    return {
      ok: true,
      code: "dry_run",
      data: {
        previewMode: "context_archive_closure",
        milestone: compactResource(resource),
        steps,
        writesPerformed: false,
        nextActions: [
          "Review the final milestone state and parent project description update together.",
          "Do not update an archived milestone through ordinary MCP workflow after archive.",
        ],
      },
      runtime: result.runtime,
    };
  }

  return {
    ok: false,
    code: "milestone_archive_api_unavailable",
    data: {
      steps,
      requiredCapability: "app_owned_milestone_archive_api",
      confirmArchive: input.confirmArchive === true,
      writesPerformed: false,
    },
    error: {
      message:
        "The current Local HTTP API does not expose a safe app-owned milestone archive endpoint for MCP forwarding.",
    },
    runtime: result.runtime,
  };
}
