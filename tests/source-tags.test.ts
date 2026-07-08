import { describe, expect, it } from "vitest";

import { completionSourceTagSlug, mergeTagSlugs } from "../src/source-tags.js";

describe("source-tags", () => {
  it("merges tag slugs without duplicates", () => {
    expect(mergeTagSlugs(["urgent", "custom_ai"], ["custom_ai", "custom_u4eba5de5"])).toEqual([
      "urgent",
      "custom_ai",
      "custom_u4eba5de5",
    ]);
  });

  it("maps completion source to frozen slugs", () => {
    const catalog = { aiSlug: "custom_ai", humanSlug: "custom_u4eba5de5" };
    expect(completionSourceTagSlug("ai", catalog)).toBe("custom_ai");
    expect(completionSourceTagSlug("human", catalog)).toBe("custom_u4eba5de5");
    expect(completionSourceTagSlug("unknown", catalog)).toBeNull();
  });
});
