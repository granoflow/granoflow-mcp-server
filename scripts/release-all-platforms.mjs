#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const cwd = fileURLToPath(new URL("../", import.meta.url));
const flags = new Set(process.argv.slice(2));
const dryRun = flags.has("--dry-run");
const localEnv = existsSync(`${cwd}/.env`)
  ? Object.fromEntries(
      readFileSync(`${cwd}/.env`, "utf8")
        .split(/\r?\n/)
        .filter((line) => /^[A-Z_]+=/.test(line))
        .map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]),
    )
  : {};
const env = { ...process.env, ...localEnv };
let pkg = JSON.parse(readFileSync(`${cwd}/package.json`, "utf8"));
const source = env.RELEASE_SOURCE_BRANCH || "develop";
const target = env.RELEASE_TARGET_BRANCH || "main";
const remote = env.RELEASE_REMOTE || "origin";
let packageName = env.NPM_PACKAGE_NAME || pkg.name;

function command(program, args, { allowFailure = false, commandEnv = env } = {}) {
  console.log(`$ ${program} ${args.join(" ")}`);
  const result = spawnSync(program, args, {
    cwd,
    env: commandEnv,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  if (result.status !== 0 && !allowFailure) {
    // Never forward a child error/output: npm and hooks may echo credentials.
    throw new Error(
      result.status === 43
        ? "npm published; recovery marking failed; inspect private file before reuse"
        : result.status === 42
          ? "npm EOTP: no private recovery code available; request an OTP from the user"
          : `${program} failed; inspect the stage locally without exposing credentials`,
    );
  }
  return result;
}
function git(...args) {
  return command("git", args).stdout.trim();
}
function checkout(branch) {
  const local = command("git", ["show-ref", "--verify", "--quiet", `refs/heads/${branch}`], {
    allowFailure: true,
  });
  if (local.status === 0) git("checkout", branch);
  else {
    git("ls-remote", "--exit-code", "--heads", remote, branch);
    git("checkout", "-b", branch, `${remote}/${branch}`);
  }
}
function verifyRemote(sha) {
  const actual = git("ls-remote", "--exit-code", "--heads", remote, `refs/heads/${target}`).split(
    /\s+/,
  )[0];
  if (actual !== sha) throw new Error("Remote target SHA does not match release candidate");
}
function publishedVersion() {
  const result = command("npm", ["view", `${packageName}@${pkg.version}`, "version", "--json"], {
    allowFailure: true,
  });
  if (result.status === 0) {
    if (JSON.parse(result.stdout) !== pkg.version) throw new Error("npm version readback mismatch");
    return true;
  }
  if (/E404/.test(`${result.stdout}\n${result.stderr}`)) return false;
  throw new Error("npm readback failed; do not retry publication until state is known");
}
function release() {
  if (!dryRun) git("fetch", remote, "--prune", "--tags");
  checkout(source);
  if (!dryRun) {
    const merge = command("git", ["merge", "--ff-only", `${remote}/${source}`], {
      allowFailure: true,
    });
    if (merge.status !== 0) git("merge", "--ff-only", source);
  }
  checkout(target);
  if (dryRun) return;
  if (target !== "main") throw new Error("npm latest releases require main");
  git("merge", "--ff-only", source);
  pkg = JSON.parse(readFileSync(`${cwd}/package.json`, "utf8"));
  packageName = env.NPM_PACKAGE_NAME || pkg.name;
  if (!flags.has("--skip-preflight")) command("npm", ["run", "release:preflight"]);
  const sha = git("rev-parse", "HEAD");
  // A restart reads the remote first. --skip-push still requires an exact readback.
  const before = git("ls-remote", "--heads", remote, `refs/heads/${target}`).split(/\s+/)[0];
  if (before !== sha && !flags.has("--skip-push")) git("push", remote, target);
  verifyRemote(sha);
  if (flags.has("--skip-publish")) return;
  if (!publishedVersion()) {
    if (!env.NPM_TOKEN) throw new Error("NPM_TOKEN is required");
    command("bash", ["scripts/release-npm-publish.sh"], {
      commandEnv: {
        ...env,
        RELEASE_PACKAGE_SPEC: `${packageName}@${pkg.version}`,
        "npm_config_//registry.npmjs.org/:_authToken": env.NPM_TOKEN,
      },
    });
    if (!publishedVersion()) throw new Error("Published npm version is not visible yet");
  }
  const tags = JSON.parse(command("npm", ["view", packageName, "dist-tags", "--json"]).stdout);
  if (tags.latest !== pkg.version) {
    throw new Error(
      "npm exact version exists but latest differs; inspect dist-tags before resuming",
    );
  }
}
try {
  const original = git("branch", "--show-current");
  if (!original || git("--no-optional-locks", "status", "--short")) {
    throw new Error("A clean worktree on a branch is required");
  }
  try {
    release();
  } finally {
    git("checkout", original);
  }
  console.log(
    "npm and Git stages complete when enabled. Before resuming Registry publication, read back its version, active/latest state and npm identity; skip stages already confirmed current.",
  );
  const urls = [
    `https://www.npmjs.com/package/${packageName}`,
    `https://registry.modelcontextprotocol.io/servers/${pkg.mcpName}`,
    "https://glama.ai/mcp/servers",
    "https://mcp.so",
    "https://mcpservers.org",
  ];
  for (const url of urls) {
    console.log(url);
    if (flags.has("--open-platforms")) spawnSync("open", [url], { stdio: "ignore" });
  }
  console.log(
    dryRun
      ? "Dry run complete: branches were switched; missing branches may require remote lookup; pages may open."
      : "Release wrapper complete; Registry and directory follow-up require separate verification.",
  );
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
