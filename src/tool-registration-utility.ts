import { z } from "zod";
import type { ApiRequestOptions } from "./api.js";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowReviewDayShowTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_review_day_show",
    "Show a Granoflow daily review by date.",
    { date: z.string().describe("Date in YYYY-MM-DD format.") },
    async ({ date }) => apiTool({ path: `/v1/reviews/days/${String(date)}` }),
  );
}

function registerGranoflowApiRequestTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, jsonInputSchema } = context;
  registerTool(
    "granoflow_api_request",
    "Run an allowed Granoflow Local HTTP API request. Prefer dedicated tools when available.",
    {
      method: z.enum(["GET", "POST", "PATCH", "DELETE"]).default("GET"),
      path: z
        .string()
        .min(1)
        .refine((path) => path.startsWith("/v1/"), "path must start with /v1/"),
      input: jsonInputSchema.optional(),
      dryRun: z.boolean().default(true).describe("When true, previews write requests."),
    },
    async ({ method, path, input, dryRun }) =>
      apiTool({
        method: method as ApiRequestOptions["method"],
        path: String(path),
        body: input,
        dryRun: method === "GET" ? false : dryRun !== false,
      }),
  );
}

export function registerUtilityTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowReviewDayShowTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowApiRequestTool(registerTool, registerCapabilityTool, context, schemas);
}
