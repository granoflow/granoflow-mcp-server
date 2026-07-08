import { requestGranoflowApi, type ApiResult } from "./api.js";

export const SOURCE_TAG_AI_LABEL = "AI";
export const SOURCE_TAG_HUMAN_LABEL = "人工";
export const SOURCE_TAG_AI_SLUG = "custom_ai";
export const SOURCE_TAG_HUMAN_SLUG = "custom_u4eba5de5";

export type CompletionSource = "ai" | "human" | "unknown";

export type SourceTagCatalog = {
  aiSlug: string;
  humanSlug: string;
  created: string[];
};

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function unwrapItems(value: unknown): Record<string, unknown>[] {
  if (!isObject(value)) {
    return [];
  }
  const outerData = value.data;
  if (isObject(outerData) && Array.isArray(outerData.items)) {
    return outerData.items.filter(isObject);
  }
  if (isObject(outerData) && isObject(outerData.data) && Array.isArray(outerData.data.items)) {
    return outerData.data.items.filter(isObject);
  }
  return [];
}

function tagLabel(item: Record<string, unknown>): string {
  return typeof item.label === "string" ? item.label.trim() : "";
}

function tagSlug(item: Record<string, unknown>): string {
  return typeof item.slug === "string" ? item.slug.trim() : "";
}

function findSourceTag(
  items: Record<string, unknown>[],
  label: string,
  preferredSlug: string,
): string | null {
  const bySlug = items.find((item) => tagSlug(item) === preferredSlug);
  if (bySlug) {
    return tagSlug(bySlug);
  }
  const byLabel = items.find((item) => tagLabel(item) === label);
  if (byLabel) {
    return tagSlug(byLabel);
  }
  return null;
}

export function completionSourceTagSlug(
  source: CompletionSource | undefined,
  catalog: Pick<SourceTagCatalog, "aiSlug" | "humanSlug">,
): string | null {
  if (source === "ai") {
    return catalog.aiSlug;
  }
  if (source === "human") {
    return catalog.humanSlug;
  }
  return null;
}

export function mergeTagSlugs(existing: unknown, additions: string[]): string[] {
  const merged = new Set<string>();
  if (Array.isArray(existing)) {
    for (const tag of existing) {
      if (typeof tag === "string" && tag.trim()) {
        merged.add(tag.trim());
      }
    }
  }
  for (const tag of additions) {
    if (tag.trim()) {
      merged.add(tag.trim());
    }
  }
  return [...merged];
}

export function readSourceTagCatalog(result: ApiResult): SourceTagCatalog | null {
  if (!result.ok || !isObject(result.data)) {
    return null;
  }
  const catalog = result.data.catalog;
  if (
    !isObject(catalog) ||
    typeof catalog.aiSlug !== "string" ||
    typeof catalog.humanSlug !== "string"
  ) {
    return null;
  }
  return {
    aiSlug: catalog.aiSlug,
    humanSlug: catalog.humanSlug,
    created: Array.isArray(catalog.created)
      ? catalog.created.filter((item): item is string => typeof item === "string")
      : [],
  };
}

export async function ensureSourceTags(): Promise<ApiResult> {
  const listResult = await requestGranoflowApi({ method: "GET", path: "/v1/tags" });
  if (!listResult.ok) {
    return listResult;
  }

  const items = unwrapItems(listResult.data);
  let aiSlug = findSourceTag(items, SOURCE_TAG_AI_LABEL, SOURCE_TAG_AI_SLUG);
  let humanSlug = findSourceTag(items, SOURCE_TAG_HUMAN_LABEL, SOURCE_TAG_HUMAN_SLUG);
  const created: string[] = [];

  if (!aiSlug) {
    const createAi = await requestGranoflowApi({
      method: "POST",
      path: "/v1/tags",
      body: { label: SOURCE_TAG_AI_LABEL, slug: SOURCE_TAG_AI_SLUG },
    });
    if (!createAi.ok) {
      return createAi;
    }
    aiSlug = SOURCE_TAG_AI_SLUG;
    created.push(SOURCE_TAG_AI_SLUG);
  }

  if (!humanSlug) {
    const createHuman = await requestGranoflowApi({
      method: "POST",
      path: "/v1/tags",
      body: { label: SOURCE_TAG_HUMAN_LABEL, slug: SOURCE_TAG_HUMAN_SLUG },
    });
    if (!createHuman.ok) {
      return createHuman;
    }
    humanSlug = SOURCE_TAG_HUMAN_SLUG;
    created.push(SOURCE_TAG_HUMAN_SLUG);
  }

  return {
    ok: true,
    code: created.length > 0 ? "source_tags_created" : "source_tags_ready",
    data: {
      catalog: {
        aiSlug,
        humanSlug,
        created,
      },
    },
    runtime: listResult.runtime,
  };
}

export async function applyCompletionSourceToBody(
  body: Record<string, unknown>,
  completionSource: CompletionSource | undefined,
): Promise<Record<string, unknown>> {
  if (!completionSource || completionSource === "unknown") {
    return body;
  }
  const ensured = await ensureSourceTags();
  const catalog = readSourceTagCatalog(ensured);
  if (!catalog) {
    return body;
  }
  const slug = completionSourceTagSlug(completionSource, catalog);
  if (!slug) {
    return body;
  }
  return {
    ...body,
    tags: mergeTagSlugs(body.tags, [slug]),
  };
}
