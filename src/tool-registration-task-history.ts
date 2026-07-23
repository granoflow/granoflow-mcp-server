import { z } from "zod";

import {
  reviewTaskDescriptionImpact,
  verifyTaskDescriptionImpact,
  type DescriptionImpactGate,
} from "./tool-runtime-task-description-impact.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";

type HistoricalMutation = z.infer<ToolRegistrationContext["historicalTaskMutationSchema"]>;
type ToolTextResult = ReturnType<ToolRegistrationContext["jsonTextResult"]>;
type PreparedImpact = {
  taskId: string;
  gate: DescriptionImpactGate;
  body: Record<string, unknown>;
};

async function prepareHistoricalMutation(
  context: ToolRegistrationContext,
  mutation: HistoricalMutation,
  mutationIndex: number,
): Promise<
  | { ok: true; mutation: HistoricalMutation; impact?: PreparedImpact }
  | { ok: false; response: ToolTextResult }
> {
  const { authoringEvidence, descriptionImpactReview, ...mutationForApi } = mutation;
  if (mutation.op === "create") {
    const fields = context.isObject(mutation.fields) ? mutation.fields : {};
    const issues = context.validateTaskAuthoringQuality(
      fields.title,
      fields.description,
      authoringEvidence,
    );
    if (issues.length > 0) {
      return {
        ok: false,
        response: context.jsonTextResult({
          ok: false,
          code: "task_authoring_quality_failed",
          data: { mutationIndex, clientMutationId: mutation.clientMutationId, issues },
          error: {
            message:
              "Historical create mutations require the shared task authoring quality evidence.",
          },
        }),
      };
    }
    return { ok: true, mutation: mutationForApi };
  }
  if (typeof mutation.taskId !== "string") {
    return {
      ok: false,
      response: context.jsonTextResult({
        ok: false,
        code: "task_description_impact_review_required",
        data: { mutationIndex },
        error: { message: "Historical update/softDelete requires taskId." },
      }),
    };
  }
  const body =
    mutation.op === "softDelete"
      ? { deletedAt: "softDelete" }
      : context.isObject(mutation.fields)
        ? mutation.fields
        : {};
  const gate = await reviewTaskDescriptionImpact(
    {
      taskId: mutation.taskId,
      review: descriptionImpactReview,
      operation: "historical",
      syntheticBody: body,
      verifyFields: mutation.op !== "softDelete",
    },
    body,
    context.validateTaskAuthoringQuality,
  );
  if (!gate.ok) {
    return {
      ok: false,
      response: context.jsonTextResult({
        ...gate,
        data: { ...gate.data, mutationIndex, clientMutationId: mutation.clientMutationId },
      }),
    };
  }
  return {
    ok: true,
    mutation: mutationForApi,
    impact: { taskId: mutation.taskId, gate, body },
  };
}

async function verifyHistoricalImpacts(
  context: ToolRegistrationContext,
  impacts: PreparedImpact[],
): Promise<{ ok: true; results: unknown[] } | { ok: false; response: ToolTextResult }> {
  const results = [];
  for (const item of impacts) {
    const verification = await verifyTaskDescriptionImpact(
      item.taskId,
      item.gate,
      item.body,
      item.gate.changedFields.every((field) => field !== "deletedAt"),
    );
    if (!verification.ok)
      return { ok: false as const, response: context.jsonTextResult(verification) };
    results.push(verification.data);
  }
  return { ok: true as const, results };
}

export function registerTaskHistoryMutationTool(
  registerTool: ToolRegistrar,
  context: ToolRegistrationContext,
): void {
  const { historicalTaskMutationSchema } = context;
  registerTool(
    "granoflow_task_history_mutate",
    "Write evidence-based task timestamps and historical Granoflow facts through the dedicated AI-agent API. AI execution may update startedAt while the task remains pending so it never claims the human doing focus slot; node-managed completion may correct startedAt/endedAt after status=done. Every create mutation requires shared AI/automation authoringEvidence for an action/outcome title, plain language, a real analogy, and a concrete example. Use dryRun first; when dryRun=false, the running app must advertise historical_task_mutations_v1.",
    {
      source: z.record(z.string(), z.unknown()).optional(),
      mutations: z.array(historicalTaskMutationSchema).max(20),
      dryRun: z.boolean().default(true),
    },
    async ({ source, mutations, dryRun }) => {
      const preparedMutations: HistoricalMutation[] = [];
      const impacts: PreparedImpact[] = [];
      for (const [index, mutation] of (mutations as HistoricalMutation[]).entries()) {
        const prepared = await prepareHistoricalMutation(context, mutation, index);
        if (!prepared.ok) return prepared.response;
        preparedMutations.push(prepared.mutation);
        if (prepared.impact) impacts.push(prepared.impact);
      }
      const result = await context.mutateTaskHistory({
        source: context.isObject(source) ? source : undefined,
        mutations: preparedMutations,
        dryRun: dryRun !== false,
      });
      const verification =
        result.ok && dryRun === false
          ? await verifyHistoricalImpacts(context, impacts)
          : {
              ok: true as const,
              results: impacts.map(({ gate }) => ({
                changedFields: gate.changedFields,
                decision: gate.review.decision,
                reasonCode: gate.review.reasonCode,
                readbackStatus: "preview_only",
              })),
            };
      if (!verification.ok) return verification.response;
      return context.jsonTextResult({
        ...result,
        data: {
          ...(context.isObject(result.data) ? result.data : { result: result.data }),
          descriptionImpact: verification.results,
        },
      });
    },
  );
}
