import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";

function registerProjectDesignBaselineTools(
  registerTool: ToolRegistrar,
  context: ToolRegistrationContext,
): void {
  const {
    basename,
    createHash,
    readFileSync,
    validatedProjectDesignBaselinePath,
    jsonTextResult,
    apiTool,
  } = context;
  registerTool(
    "granoflow_project_design_baseline_import",
    "Import one validated high-fidelity Design Baseline package as the App-owned project visual/IA authority for later milestones, task prototypes, and code. Package should include Design Tokens and landscape/portrait App Shell. The App owns validation, immutable versions, project linking, deduplication, and exact SHA-256 readback.",
    {
      projectId: z.string().min(1),
      filePath: z.string().min(1).describe("Absolute path to a local .zip package."),
      prototypeId: z.string().min(1).optional(),
      idempotencyKey: z.string().min(1),
      dryRun: z.boolean().default(true),
    },
    async ({ projectId, filePath, prototypeId, idempotencyKey, dryRun }) => {
      let file: string;
      try {
        file = validatedProjectDesignBaselinePath(String(filePath));
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "unsafe_project_design_baseline_path",
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
      const bytes = readFileSync(file);
      const packageSha256 = createHash("sha256").update(bytes).digest("hex");
      return apiTool({
        method: "POST",
        path: "/v1/ai-agent/project-design-baseline/import",
        body: {
          projectId: String(projectId),
          displayName: basename(file),
          packageBase64: bytes.toString("base64"),
          expectedPackageSha256: packageSha256,
          idempotencyKey: String(idempotencyKey),
          ...(prototypeId ? { prototypeId: String(prototypeId) } : {}),
        },
        dryRun: dryRun !== false,
      });
    },
  );
  registerTool(
    "granoflow_project_design_baseline_read",
    "Read back one exact App-owned project Design Baseline reference (authority for later UI work). Never guesses the latest version; require exact prototypeId, versionId, and packageSha256.",
    {
      projectId: z.string().min(1),
      prototypeId: z.string().min(1),
      versionId: z.string().min(1),
      expectedPackageSha256: z.string().regex(/^[a-f0-9]{64}$/),
    },
    async ({ projectId, prototypeId, versionId, expectedPackageSha256 }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/project-design-baseline/read",
        body: {
          projectId: String(projectId),
          prototypeId: String(prototypeId),
          versionId: String(versionId),
          expectedPackageSha256: String(expectedPackageSha256),
        },
      }),
  );
}

function registerTaskPrototypeTools(
  registerTool: ToolRegistrar,
  context: ToolRegistrationContext,
): void {
  const {
    basename,
    createHash,
    readFileSync,
    validatedTaskPrototypePath,
    jsonTextResult,
    apiTool,
  } = context;
  registerTool(
    "granoflow_task_prototype_import",
    "Import one validated .granoprototype package through the App-owned task Prototype/Version/Link aggregate and return exact SHA-256 readback.",
    {
      taskId: z.string().min(1),
      filePath: z.string().min(1).describe("Absolute path to a local .granoprototype package."),
      prototypeId: z.string().min(1).optional(),
      idempotencyKey: z.string().min(1),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, filePath, prototypeId, idempotencyKey, dryRun }) => {
      let file: string;
      try {
        file = validatedTaskPrototypePath(String(filePath));
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "unsafe_task_prototype_path",
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
      const bytes = readFileSync(file);
      const packageSha256 = createHash("sha256").update(bytes).digest("hex");
      return apiTool({
        method: "POST",
        path: "/v1/ai-agent/task-prototype/import",
        body: {
          taskId: String(taskId),
          displayName: basename(file),
          packageBase64: bytes.toString("base64"),
          expectedPackageSha256: packageSha256,
          idempotencyKey: String(idempotencyKey),
          ...(prototypeId ? { prototypeId: String(prototypeId) } : {}),
        },
        dryRun: dryRun !== false,
      });
    },
  );
  registerTool(
    "granoflow_task_prototype_read",
    "Read one exact task-owned Prototype/Version/Link reference. Never guesses a current or latest version.",
    {
      taskId: z.string().min(1),
      prototypeId: z.string().min(1),
      versionId: z.string().min(1),
      expectedPackageSha256: z.string().regex(/^[a-f0-9]{64}$/),
    },
    async ({ taskId, prototypeId, versionId, expectedPackageSha256 }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/task-prototype/read",
        body: {
          taskId: String(taskId),
          prototypeId: String(prototypeId),
          versionId: String(versionId),
          expectedPackageSha256: String(expectedPackageSha256),
        },
      }),
  );
}

export function registerPrototypeTools(
  registerTool: ToolRegistrar,
  _registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
): void {
  registerProjectDesignBaselineTools(registerTool, context);
  registerTaskPrototypeTools(registerTool, context);
}
