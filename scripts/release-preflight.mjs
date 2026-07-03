#!/usr/bin/env node
/* global console, process */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const args = new Set(process.argv.slice(2));
const skipCheck = args.has("--skip-check");
const skipPack = args.has("--skip-pack");
const help = args.has("--help") || args.has("-h");

if (help) {
  console.log(`Granoflow MCP release preflight

Usage:
  npm run release:preflight
  node scripts/release-preflight.mjs --skip-check --skip-pack

Checks:
  - npm run check unless --skip-check is set
  - package.json and src/metadata.ts version consistency
  - npm pack --dry-run --json contents unless --skip-pack is set
  - dist/index.js executable mode in the package
  - docs included in the package
  - obsolete CLI references and likely secret patterns in release files
`);
  process.exit(0);
}

const failures = [];

function record(ok, message, detail) {
  const icon = ok ? "ok" : "fail";
  console.log(`[${icon}] ${message}`);
  if (detail) {
    console.log(detail);
  }
  if (!ok) {
    failures.push(message);
  }
}

function run(command, commandArgs, options = {}) {
  return execFileSync(command, commandArgs, {
    encoding: "utf8",
    stdio: options.stdio ?? "pipe",
  });
}

const packageJson = JSON.parse(readFileSync("package.json", "utf8"));
const metadata = readFileSync("src/metadata.ts", "utf8");
const metadataVersion = metadata.match(/SERVER_VERSION\s*=\s*"([^"]+)"/)?.[1];
record(
  packageJson.version === metadataVersion,
  "package.json version matches src/metadata.ts",
  packageJson.version === metadataVersion
    ? undefined
    : `package.json=${packageJson.version} metadata=${metadataVersion ?? "[missing]"}`,
);

if (!skipCheck) {
  try {
    run("npm", ["run", "check"], { stdio: "inherit" });
    record(true, "npm run check passed");
  } catch {
    record(false, "npm run check failed");
  }
} else {
  record(true, "npm run check skipped by flag");
}

if (!skipPack) {
  try {
    const packOutput = run("npm", ["pack", "--dry-run", "--json"]);
    const pack = JSON.parse(packOutput)[0];
    const files = pack.files ?? [];
    const fileNames = new Set(files.map((file) => file.path));
    const binFile = files.find((file) => file.path === "dist/index.js");
    record(Boolean(binFile), "package contains dist/index.js");
    record(binFile?.mode === 493, "dist/index.js is executable in npm package");
    record(fileNames.has("docs/user-install-demo.md"), "package contains user install guide");
    record(fileNames.has("docs/release-checklist.md"), "package contains release checklist");
    record(
      fileNames.has("skills/granoflow-agent-workflow/SKILL.md"),
      "package contains Granoflow agent workflow skill",
    );
    record(
      fileNames.has("skills/granoflow-agent-workflow/agents/openai.yaml"),
      "package contains Granoflow agent workflow agents metadata",
    );
    record(!fileNames.has("dist/cli.js"), "package does not contain obsolete dist/cli.js");
  } catch (error) {
    record(false, "npm pack --dry-run --json failed", error instanceof Error ? error.message : "");
  }
} else {
  record(true, "npm pack dry-run skipped by flag");
}

const scanTargets = [
  "README.md",
  "AGENTS.md",
  "package.json",
  "src/tools.ts",
  "src/setup.ts",
  "src/api.ts",
  "docs/user-install-demo.md",
  "skills/granoflow-agent-workflow/SKILL.md",
];
const existingScanTargets = scanTargets.filter((target) => existsSync(target));
const obsoleteCliHits = [];
const secretHits = [];
for (const target of existingScanTargets) {
  const text = readFileSync(target, "utf8");
  if (/granoflow-cli|GRANOFLOW_CLI_PATH/.test(text)) {
    obsoleteCliHits.push(target);
  }
  if (/(npm_[A-Za-z0-9]{20,}|_authToken\\s*=|recovery code|secret-token)/i.test(text)) {
    secretHits.push(target);
  }
}
record(obsoleteCliHits.length === 0, "release docs/runtime files have no obsolete CLI references");
record(secretHits.length === 0, "release docs/runtime files have no likely secret literals");

const workflowSkillPath = "skills/granoflow-agent-workflow/SKILL.md";
const workflowSkillAgentsPath = "skills/granoflow-agent-workflow/agents/openai.yaml";
if (existsSync(workflowSkillPath)) {
  const skillText = readFileSync(workflowSkillPath, "utf8");
  record(
    /^---\nname: granoflow-agent-workflow\n/m.test(skillText) &&
      /^description: .+/m.test(skillText),
    "Granoflow agent workflow skill has required frontmatter",
  );
  record(
    /## Trigger Conditions/.test(skillText) &&
      /## Connection First/.test(skillText) &&
      /## Completing Tasks/.test(skillText) &&
      /## User Dissatisfaction/.test(skillText) &&
      /Success criteria:/.test(skillText),
    "Granoflow agent workflow skill carries triggers, workflow branches, and success criteria",
  );
  record(
    /wrapper skill/.test(skillText) &&
      /Polite disagreement receives the same care as angry feedback/.test(skillText),
    "Granoflow agent workflow skill covers wrapper-skill feedback guidance",
  );
} else {
  record(false, "Granoflow agent workflow skill exists");
}
record(
  existsSync(workflowSkillAgentsPath),
  "Granoflow agent workflow skill has agents/openai.yaml metadata",
);

if (failures.length > 0) {
  console.error(`\nRelease preflight failed: ${failures.length} issue(s).`);
  process.exit(1);
}

console.log("\nRelease preflight passed.");
