/* global process */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, copyFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const source = resolve("scripts");
function fixture(options = {}) {
  const root = mkdtempSync(join(process.env.TMPDIR || tmpdir(), "mcp-release-test-"));
  const repo = join(root, "repo");
  const bin = join(root, "bin");
  mkdirSync(join(repo, "scripts"), { recursive: true });
  mkdirSync(bin);
  mkdirSync(join(root, "home"));
  for (const file of ["release-all-platforms.mjs", "release-npm-publish.sh"]) {
    copyFileSync(join(source, file), join(repo, "scripts", file));
  }
  writeFileSync(
    join(repo, "package.json"),
    JSON.stringify({ name: "fixture-package", version: "1.0.0", mcpName: "fixture/server" }),
  );
  writeFileSync(join(repo, ".gitignore"), ".npm*\n.local-ai/\n");
  const env = {
    PATH: `${bin}:/usr/bin:/bin:/usr/sbin:/sbin`,
    HOME: join(root, "home"),
    GIT_CONFIG_NOSYSTEM: "1",
    GIT_CONFIG_GLOBAL: "/dev/null",
    npm_config_userconfig: join(root, "empty-npmrc"),
    npm_config_cache: join(root, "npm-cache"),
    NPM_TOKEN: "FAKE-TOKEN-ONLY",
    LOG: join(root, "calls"),
    STATE: join(root, "published"),
    MODE: options.mode || "success",
    EXPECT_VERSION: options.version || "1.0.0",
  };
  function git(...args) {
    const result = spawnSync("/usr/bin/git", args, { cwd: repo, env, encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr);
    return result.stdout.trim();
  }
  git("init", "-b", "develop");
  git("config", "user.name", "Fixture");
  git("config", "user.email", "fixture@example.invalid");
  git("add", ".");
  git("commit", "-m", "fixture");
  git("branch", "main");
  if (options.version) {
    writeFileSync(
      join(repo, "package.json"),
      JSON.stringify({
        name: "fixture-package",
        version: options.version,
        mcpName: "fixture/server",
      }),
    );
    git("add", "package.json");
    git("commit", "-m", "version");
    git("checkout", "main");
  }
  const remote = join(root, "remote.git");
  const bare = spawnSync("/usr/bin/git", ["init", "--bare", remote], { env });
  assert.equal(bare.status, 0);
  git("remote", "add", "origin", remote);
  git("push", "origin", "develop", "main");
  if (options.ahead) {
    writeFileSync(join(repo, "candidate"), "next");
    git("add", "candidate");
    git("commit", "-m", "next");
  }
  if (options.code !== false)
    writeFileSync(join(repo, ".npm_recovery_codes.txt"), "FAKE-CODE-ONLY\n");
  writeFileSync(
    join(bin, "git"),
    `#!/bin/bash\nprintf 'git %s\\n' "$*" >> "$LOG"\nif [ "$MODE" = pushfail ] && [ "$1" = push ]; then exit 1; fi\nif [ "$MODE" = mismatch ] && [ "$1" = ls-remote ]; then echo 'deadbeef refs/heads/main'; exit 0; fi\nexec /usr/bin/git "$@"\n`,
    { mode: 0o755 },
  );
  writeFileSync(
    join(bin, "npm"),
    `#!/bin/bash
printf 'npm %s\\n' "$*" >> "$LOG"
case "$1" in
view) if [ "$3" = dist-tags ]; then
  if [ "$MODE" = oldtag ]; then echo '{"latest":"0.0.1"}'; else printf '{"latest":"%s"}\n' "$EXPECT_VERSION"; fi
  exit 0
fi
if [ -f "$STATE" ]; then printf '"%s"\n' "$EXPECT_VERSION"; else echo E404 >&2; exit 1; fi ;;
publish)
  if [ "$MODE" = failure ]; then echo "$NPM_TOKEN $npm_config_otp" >&2; exit 1; fi
  if [ "$MODE" = otp ] || [ "$MODE" = otpfail ] || [ "$MODE" = markfail ]; then
    if [ -z "$npm_config_otp" ]; then echo EOTP >&2; exit 1; fi
    if [ "$MODE" = otpfail ]; then echo "$npm_config_otp" >&2; exit 1; fi
  fi
  touch "$STATE"
  if [ "$MODE" = ambiguous ]; then echo EOTP >&2; exit 1; fi
  ;;

*) exit 99 ;;
esac
`,
    { mode: 0o755 },
  );
  writeFileSync(join(bin, "open"), '#!/bin/bash\necho open >> "$LOG"\n', { mode: 0o755 });
  if (options.mode === "markfail")
    writeFileSync(join(bin, "mktemp"), "#!/bin/bash\nexit 1\n", { mode: 0o755 });
  return {
    repo,
    env,
    git,
    run(args = []) {
      return spawnSync(
        process.execPath,
        [join(repo, "scripts/release-all-platforms.mjs"), "--skip-preflight", ...args],
        { env, encoding: "utf8", timeout: 10000 },
      );
    },
    log() {
      return readFileSync(env.LOG, "utf8");
    },
    codes() {
      return readFileSync(join(repo, ".npm_recovery_codes.txt"), "utf8");
    },
  };
}

test("push and SHA readback precede npm; restart skips accepted stages", () => {
  const f = fixture({ ahead: true });
  assert.equal(f.run().status, 0);
  const log = f.log();
  assert.ok(log.indexOf("git push origin main") < log.indexOf("npm view"));
  assert.ok(log.indexOf("git ls-remote --exit-code") < log.indexOf("npm publish"));
  assert.equal(f.codes(), "FAKE-CODE-ONLY\n");
  assert.equal(f.run().status, 0);
  assert.equal(f.log().match(/npm publish/g).length, 1);
  assert.equal(f.log().match(/git push origin main/g).length, 1);
  assert.equal(f.git("branch", "--show-current"), "develop");
});
for (const mode of ["pushfail", "mismatch"])
  test(`${mode} blocks npm`, () => {
    const f = fixture({ mode, ahead: true });
    assert.equal(f.run().status, 1);
    assert.ok(!f.log().includes("npm "));
    assert.equal(f.git("branch", "--show-current"), "develop");
  });
for (const mode of ["otp", "otpfail", "failure"])
  test(`${mode} preserves secrets and consumes only successful recovery`, () => {
    const f = fixture({ mode });
    const result = f.run();
    assert.equal(result.status, mode === "otp" ? 0 : 1);
    assert.ok(!`${result.stdout}${result.stderr}`.includes("FAKE-TOKEN-ONLY"));
    assert.ok(!`${result.stdout}${result.stderr}`.includes("FAKE-CODE-ONLY"));
    assert.equal(f.codes(), mode === "otp" ? "# USED\n" : "FAKE-CODE-ONLY\n");
    if (mode !== "failure") assert.equal(f.log().match(/npm publish/g).length, 2);
  });
test("missing recovery code requests OTP only after EOTP", () => {
  const f = fixture({ mode: "otp", code: false });
  const result = f.run();
  assert.equal(result.status, 1);
  assert.match(result.stderr, /request an OTP/);
});
test("dry run switches branches and opens pages, skipping fetch/push/npm", () => {
  const f = fixture();
  const result = f.run(["--dry-run", "--open-platforms"]);
  assert.equal(result.status, 0);
  assert.match(f.log(), /git checkout main/);
  assert.match(f.log(), /open/);
  assert.ok(!/git fetch|git push|npm /.test(f.log()));
  assert.equal(f.codes(), "FAKE-CODE-ONLY\n");
});
test("skip-push refuses unpushed candidate", () => {
  const f = fixture({ ahead: true });
  assert.equal(f.run(["--skip-push"]).status, 1);
  assert.ok(!f.log().includes("npm "));
});

test("re-reads merged package when invoked from older main", () => {
  const f = fixture({ version: "1.0.1" });
  assert.equal(f.run().status, 0);
  assert.match(f.log(), /npm view fixture-package@1.0.1 version/);
  assert.equal(f.git("branch", "--show-current"), "main");
});
test("published exact version with stale latest is actionable failure", () => {
  const f = fixture({ mode: "oldtag" });
  const result = f.run();
  assert.equal(result.status, 1);
  assert.match(result.stderr, /latest differs/);
});
test("failed recovery marking reports published state without exposing code", () => {
  const f = fixture({ mode: "markfail" });
  const result = f.run();
  assert.equal(result.status, 1);
  assert.match(result.stderr, /recovery marking failed/);
  assert.equal(f.codes(), "FAKE-CODE-ONLY\n");
  assert.ok(!result.stderr.includes("FAKE-CODE-ONLY"));
});
test("private recovery is preferred over supplied OTP", () => {
  const f = fixture({ mode: "otp" });
  f.env.NPM_OTP = "FAKE-SUPPLIED-OTP";
  assert.equal(f.run().status, 0);
  assert.equal(f.codes(), "# USED\n");
});

test("ambiguous accepted publish is read back before a second attempt", () => {
  const f = fixture({ mode: "ambiguous" });
  assert.equal(f.run().status, 0);
  assert.equal(f.log().match(/npm publish/g).length, 1);
  assert.equal(f.codes(), "FAKE-CODE-ONLY\n");
});
for (const scenario of ["normal", "existing", "dry"])
  test(`recovery FIFO is never read during ${scenario}`, () => {
    const f = fixture({ code: false });
    assert.equal(spawnSync("/usr/bin/mkfifo", [join(f.repo, ".npm_recovery_codes.txt")]).status, 0);
    if (scenario === "existing") writeFileSync(f.env.STATE, "published");
    const result = f.run(scenario === "dry" ? ["--dry-run"] : []);
    assert.equal(result.status, 0, result.stderr);
  });
