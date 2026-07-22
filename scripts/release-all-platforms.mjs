#!/usr/bin/env node

import { execSync, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const cwd = resolve(__dirname, "..");

function run(command, { inherit = false } = {}) {
  const output = execSync(`bash -lc ${JSON.stringify(command)}`, {
    cwd,
    stdio: inherit ? "inherit" : ["ignore", "pipe", "pipe"],
    encoding: "utf8",
  });
  if (output === undefined || output === null) {
    return "";
  }
  return output.toString().trim();
}

function runCapture(command) {
  return run(command, { inherit: false });
}

function redactCommand(command) {
  if (npmToken) {
    command = command.replaceAll(npmToken, "***NPM_TOKEN***");
  }
  if (npmOtp) {
    command = command.replaceAll(npmOtp, "***NPM_OTP***");
  }
  return command;
}

function runEcho(command) {
  console.log(`$ ${redactCommand(command)}`);
  return run(command, { inherit: true });
}

function parseEnv(content) {
  const vars = {};
  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }
    const [key, ...rest] = line.split("=");
    if (!key || rest.length === 0) {
      continue;
    }
    vars[key] = rest.join("=");
  }
  return vars;
}

function loadEnv() {
  const envFile = resolve(cwd, ".env");
  if (!existsSync(envFile)) {
    return {};
  }
  const data = readFileSync(envFile, "utf8");
  return parseEnv(data);
}

function assert(message, predicate) {
  if (!predicate()) {
    throw new Error(`发布中断：${message}`);
  }
}

const args = new Set(process.argv.slice(2));
const isDryRun = args.has("--dry-run");
const skipPreflight = args.has("--skip-preflight");
const skipPublish = args.has("--skip-publish");
const skipPush = args.has("--skip-push");
const openPlatforms = args.has("--open-platforms");

const env = loadEnv();
const packageJson = JSON.parse(readFileSync(resolve(cwd, "package.json"), "utf8"));
const packageName = env.NPM_PACKAGE_NAME || process.env.NPM_PACKAGE_NAME || packageJson.name;
const sourceBranch = env.RELEASE_SOURCE_BRANCH || "develop";
const targetBranch = env.RELEASE_TARGET_BRANCH || "main";
const remote = env.RELEASE_REMOTE || "origin";
const version = packageJson.version;
const npmToken = env.NPM_TOKEN || process.env.NPM_TOKEN;
const npmOtp = env.NPM_OTP || process.env.NPM_OTP;

const options = [
  "release:all-platforms",
  `package=${packageName}`,
  `version=${version}`,
  `source=${sourceBranch}`,
  `target=${targetBranch}`,
  `remote=${remote}`,
  `dryRun=${isDryRun}`,
].join(" ");

console.log(`开始执行 Granoflow MCP 发布技能: ${options}`);

const originalBranch = runCapture("git branch --show-current");
assert("无法读取当前分支", () => Boolean(originalBranch));

const status = runCapture("git status --short");
assert("工作区必须先清洁", () => !status);

if (!isDryRun) {
  runEcho(`git fetch ${remote} --prune --tags`);
}

function checkoutOrFail(branchName) {
  const localExists =
    runCapture(
      `git show-ref --verify --quiet refs/heads/${branchName} && echo true || echo false`,
    ) === "true";
  if (localExists) {
    runEcho(`git checkout ${branchName}`);
    return;
  }

  const remoteExists =
    runCapture(
      `git ls-remote --exit-code --heads ${remote} ${branchName} >/dev/null 2>&1 && echo true || echo false`,
    ) === "true";
  assert(`${branchName} 分支不存在`, () => remoteExists);
  runEcho(`git checkout -b ${branchName} ${remote}/${branchName}`);
}

checkoutOrFail(sourceBranch);

if (!isDryRun) {
  runEcho(
    `git merge --ff-only ${remote}/${sourceBranch} 2>/dev/null || git merge --ff-only ${sourceBranch}`,
  );
}

checkoutOrFail(targetBranch);

if (!isDryRun) {
  console.log(`合并 ${sourceBranch} 到 ${targetBranch}`);
  runEcho(`git merge --ff-only ${sourceBranch}`);

  if (!skipPreflight) {
    runEcho("npm run release:preflight");
  }

  if (!skipPublish) {
    assert("未提供 NPM_TOKEN，请先在 .env 或环境变量中设置", () => Boolean(npmToken));
    const escapedToken = npmToken.replaceAll("'", "'\\''");
    runEcho(`npm config set --location project //registry.npmjs.org/:_authToken '${escapedToken}'`);
    try {
      const otpSuffix = npmOtp ? ` --otp ${JSON.stringify(npmOtp)}` : "";
      runEcho(`npm publish --access public${otpSuffix}`);
    } finally {
      runEcho("npm config delete --location=project //registry.npmjs.org/:_authToken");
    }

    const verify = runCapture(`npm view ${packageName}@${version} version dist-tags --json`);
    console.log("发布结果校验:");
    console.log(verify);
  }

  if (!skipPush) {
    runEcho(`git push ${remote} ${targetBranch}`);
  }
}

runEcho(`git checkout ${originalBranch}`);

console.log("其他平台发布（手动确认）:");
console.log(
  "1) 官方 MCP Registry: 检查 com.granoflow/mcp-server 是否已同步为当前版本与 latest 状态。",
);
console.log(
  "2) Glama / mcp.so / mcpservers.org / Awesome MCP Servers / Smithery-MCPB: 逐一核对仓库、安装命令和描述一致性。",
);
console.log("3) 如平台信息变更，请提交更新并保留审核状态记录后再关闭发布。");

const platformUrls = {
  npm: `https://www.npmjs.com/package/${packageName}`,
  mcpRegistry: `https://registry.modelcontextprotocol.io/servers/${packageJson.mcpName}`,
  glama: "https://glama.ai/mcp/servers",
  mcps: "https://mcp.so",
  mcpservers: "https://mcpservers.org",
};

for (const [platform, url] of Object.entries(platformUrls)) {
  console.log(`${platform}: ${url}`);
}

if (openPlatforms) {
  for (const url of Object.values(platformUrls)) {
    spawnSync("open", [url], { stdio: "ignore" });
  }
}

if (!isDryRun) {
  console.log("发布流程已完成。");
} else {
  console.log("发布预演完成。执行实际发布请移除 --dry-run。\n");
}
