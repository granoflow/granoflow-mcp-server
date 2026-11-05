/* global process */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const script = resolve("scripts/release-preflight.mjs");
function fixture(mode) {
  const root = mkdtempSync(join(tmpdir(), "mcp-pack-test-"));
  for (const path of ["src", "docs", "bin", "home"]) mkdirSync(join(root, path));
  writeFileSync(join(root, "package.json"), JSON.stringify({ name: "fixture", version: "1.0.0" }));
  writeFileSync(
    join(root, "server.json"),
    JSON.stringify({
      version: "1.0.0",
      packages: [{ registryType: "npm", identifier: "fixture", version: "1.0.0" }],
    }),
  );
  writeFileSync(join(root, "src/metadata.ts"), 'const SERVER_VERSION = "1.0.0";');
  const names = readdirSync("skills", { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);
  const files = [
    { path: "dist/index.js", mode: 493 },
    { path: "dist/gfmcp-runner-launcher.js", mode: 493 },
    ...[
      "docs/user-install-demo.md",
      "docs/release-checklist.md",
      "docs/directory-listings.md",
      "skills/granoflow-agent-workflow/agents/openai.yaml",
      "skills/granoflow-gfmcp-runner/scripts/gfmcp_runner.py",
    ].map((path) => ({ path })),
  ];
  for (const name of names) {
    mkdirSync(join(root, "skills", name), { recursive: true });
    writeFileSync(
      join(root, "skills", name, "SKILL.md"),
      `---\nname: ${name}\ndescription: Fixture structural metadata\n---\nArbitrary rewritten body with no prescribed workflow phrases.\n`,
    );
    files.push({ path: `skills/${name}/SKILL.md` });
  }
  if (["blank", "empty-folded", "overlong", "folded"].includes(mode)) {
    const description = {
      blank: '""',
      "empty-folded": ">-",
      overlong: "x".repeat(1025),
      folded: ">-\n  Valid folded\n  description",
    }[mode];
    writeFileSync(
      join(root, "skills", names[0], "SKILL.md"),
      `---\nname: ${names[0]}\ndescription: ${description}\n---\nbody\n`,
    );
  }
  mkdirSync(join(root, "skills/granoflow-agent-workflow/agents"));
  writeFileSync(
    join(root, "skills/granoflow-agent-workflow/agents/openai.yaml"),
    "display_name: Fixture\n",
  );
  if (mode === "missing")
    files.splice(
      files.findIndex((file) => file.path === "skills/granoflow-release-all-platforms/SKILL.md"),
      1,
    );
  if (mode === "private") files.push({ path: ".local-ai/private.txt" });
  writeFileSync(join(root, "pack.json"), JSON.stringify([{ files }]));
  writeFileSync(join(root, "bin/npm"), "#!/bin/bash\ncat pack.json\n", { mode: 0o755 });
  return spawnSync(process.execPath, [script, "--skip-check"], {
    cwd: root,
    encoding: "utf8",
    env: { PATH: `${root}/bin:/usr/bin:/bin`, HOME: `${root}/home` },
  });
}

test("preflight checks all packaged skills without freezing prose", () => {
  const result = fixture("valid");
  assert.equal(result.status, 0, result.stdout + result.stderr);
});
for (const mode of ["missing", "private", "blank", "empty-folded", "overlong"])
  test(`preflight rejects ${mode} package contents`, () => {
    const result = fixture(mode);
    assert.equal(result.status, 1);
    assert.match(result.stdout, /\[fail\]/);
  });

test("preflight accepts nonempty folded descriptions", () => {
  const result = fixture("folded");
  assert.equal(result.status, 0, result.stdout + result.stderr);
});
