import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";

type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};

export function registerGranoflowReviewNoteFieldMediaUploadTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { basename, createHash, readFileSync, jsonTextResult, resourceCapabilityApiTool } = context;
  registerTool(
    "granoflow_review_note_field_media_upload",
    "Read local image bytes at the MCP boundary, upload them through Local HTTP as Base64 onto a persisted review note image field (App compresses to WebP ≤300KB). Optionally place the field on a card front/back layout via cardId+layoutSide. The file path is not sent to or opened by the Granoflow app.",
    {
      noteId: z.string().min(1),
      filePath: z.string().min(1),
      fieldKey: z.string().min(1).default("custom_uit_screenshot"),
      fieldType: z.enum(["image", "image_grid"]).default("image"),
      slot: z.number().int().min(0).default(0),
      fieldLabel: z.string().min(1).default("UIT screenshot"),
      ensureField: z.boolean().default(true),
      cardId: z.string().min(1).optional(),
      layoutSide: z.enum(["front", "back"]).default("back"),
      dryRun: z.boolean().default(true),
    },
    async ({
      noteId,
      filePath,
      fieldKey,
      fieldType,
      slot,
      fieldLabel,
      ensureField,
      cardId,
      layoutSide,
      dryRun,
    }) => {
      let bytes: Buffer;
      try {
        bytes = readFileSync(String(filePath));
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "unsafe_attachment_path",
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
      const contentSha256 = createHash("sha256").update(bytes).digest("hex");
      const body: Record<string, unknown> = {
        contentBase64: bytes.toString("base64"),
        fileName: basename(String(filePath)),
        fieldKey: String(fieldKey),
        fieldType: fieldType ?? "image",
        slot: slot ?? 0,
        fieldLabel: fieldLabel ?? "UIT screenshot",
        ensureField: ensureField !== false,
        expectedContentSha256: contentSha256,
      };
      if (cardId) {
        body.cardId = String(cardId);
        body.layoutSide = layoutSide ?? "back";
      }
      return resourceCapabilityApiTool("review-note", ["field-media.upload"], {
        method: "POST",
        path: `/v1/review-notes/${String(noteId)}/field-media`,
        body,
        dryRun: dryRun !== false,
      });
    },
  );
}
