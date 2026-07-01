import { execFile } from "node:child_process";
import { promisify } from "node:util";

import { describe, expect, it } from "vitest";

const execFileAsync = promisify(execFile);

describe("release preflight script", () => {
  it("runs lightweight checks without invoking npm check or pack", async () => {
    const { stdout, stderr } = await execFileAsync(process.execPath, [
      "scripts/release-preflight.mjs",
      "--skip-check",
      "--skip-pack",
    ]);

    expect(stdout).toContain("[ok] package.json version matches src/metadata.ts");
    expect(stdout).toContain("[ok] npm run check skipped by flag");
    expect(stdout).toContain("[ok] npm pack dry-run skipped by flag");
    expect(stdout).toContain("Release preflight passed.");
    expect(stderr).toBe("");
  });
});
