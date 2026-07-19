import { describe, expect, it } from "vitest";
import { z } from "zod";
import { installToolTestLifecycle } from "./tools-test-harness.js";
import { registerGranoflowTools } from "../src/tools.js";

installToolTestLifecycle();

describe("tools-surface-registration", () => {
  it("registers setup tools on the MCP server surface", () => {
    const names: string[] = [];

    registerGranoflowTools({
      tool: (
        name: string,
        _description: string,
        _schema: Record<string, z.ZodTypeAny>,
        _handler: (args: Record<string, unknown>) => Promise<unknown>,
      ) => {
        names.push(name);
      },
    });

    expect(names).toEqual(
      expect.arrayContaining([
        "granoflow_setup_status",
        "granoflow_agent_workflow_skill",
        "granoflow_daily_review_skill",
        "granoflow_first_run_import_skill",
        "granoflow_gfmcp_runner_skill",
        "granoflow_delegated_authorization_skill",
        "granoflow_task_orchestrator_skill",
        "granoflow_milestone_workflow_skill",
        "granoflow_persistent_milestone_runner_skill",
        "granoflow_project_definition_skill",
        "granoflow_gfmcp_prepare",
        "granoflow_gfmcp_safe_sync",
        "granoflow_gfmcp_candidates",
        "granoflow_setup_detect_local_api",
        "granoflow_setup_write_config",
        "granoflow_setup_open_config",
        "granoflow_setup_open_app",
        "granoflow_version",
        "granoflow_context_pack",
        "granoflow_historical_task_candidates",
        "granoflow_memory_batch_preview",
        "granoflow_context_steward_status",
        "granoflow_project_context_attachments_ensure",
        "granoflow_project_context_attachment_read",
        "granoflow_project_context_attachment_reconcile",
        "granoflow_project_context_attachment_write",
        "granoflow_project_interaction_style",
        "granoflow_project_context_update",
        "granoflow_milestone_context_update",
        "granoflow_milestone_context_archive",
        "granoflow_task_completion_record",
        "granoflow_review_card_record",
        "granoflow_review_card_similar",
        "granoflow_review_card_authoring_preview",
        "granoflow_review_card_authoring_apply",
        "granoflow_evidence_authoring_preview",
        "granoflow_evidence_get",
        "granoflow_evidence_authoring_apply",
        "granoflow_experience_authoring_preview",
        "granoflow_experience_authoring_apply",
        "granoflow_project_experiences",
        "granoflow_milestone_experiences",
        "granoflow_experience_usage_unlink_impact",
        "granoflow_knowledge_assessment_preview",
        "granoflow_knowledge_assessment_apply",
        "granoflow_knowledge_materialization_preview",
        "granoflow_knowledge_materialization_apply",
        "granoflow_task_knowledge_pack",
        "granoflow_task_knowledge_adoption_preview",
        "granoflow_task_knowledge_adoption_apply",
        "granoflow_task_knowledge_audit_preview",
        "granoflow_task_knowledge_audit_apply",
        "granoflow_task_knowledge_usage_preview",
        "granoflow_task_knowledge_usage_apply",
        "granoflow_project_knowledge_usages",
        "granoflow_milestone_knowledge_usages",
        "granoflow_task_create_structured",
        "granoflow_task_update",
        "granoflow_task_update_structured",
        "granoflow_task_attachment_list",
        "granoflow_logical_attachment_replace",
        "granoflow_logical_attachment_read",
        "granoflow_project_design_baseline_import",
        "granoflow_project_design_baseline_read",
        "granoflow_project_work_evaluate",
        "granoflow_project_work_confirm",
        "granoflow_task_attachment_add_markdown",
        "granoflow_task_attachment_delete",
        "granoflow_task_node_list",
        "granoflow_task_node_batch_create",
        "granoflow_task_node_update",
        "granoflow_task_node_delete",
        "granoflow_task_finish",
        "granoflow_task_resolve",
        "granoflow_project_resolve",
        "granoflow_project_create",
        "granoflow_project_update",
        "granoflow_project_delete",
        "granoflow_milestone_list",
        "granoflow_milestone_resolve",
        "granoflow_milestone_create",
        "granoflow_milestone_update",
        "granoflow_milestone_delete",
        "granoflow_api_request",
      ]),
    );
  });
});
