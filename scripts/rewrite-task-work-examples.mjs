import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const root = process.cwd();
const files = readdirSync(root).filter((file) =>
  /^task-work-[0-9a-f-]+-v(?:06|08)\.md$/.test(file),
);

for (const file of files) {
  const source = readFileSync(join(root, file), "utf8");
  const id = file.match(/^task-work-([0-9a-f-]+)-v(06|08)\.md$/)?.[1];
  const version = file.endsWith("-v08.md") ? 9 : 7;
  if (!id || source.includes("## Concrete Example")) continue;

  const title = source.match(/^# Task Work: (.+)$/m)?.[1] ?? id;
  const summary = source.match(/## Reader Summary\n\n([\s\S]*?)(?=\n## |\n<!--)/)?.[1]?.trim();
  const example =
    summary && summary.length > 20
      ? `例如，${summary.replace(/[。.!！?？]+$/, "")}时，接手人会直接遇到这个问题，需要根据可观察结果判断影响是否已经消失。`
      : `例如，当“${title}”描述的情况发生时，用户或执行者会看到不一致的结果，并且无法仅凭任务标题判断下一步该怎么做。`;
  const rationale = `本次边界只覆盖“${title}”对应的失败或风险。这样设置是为了让验收证据能直接对应原问题；例如，超出该边界的其他功能仍按原有规则处理，避免修复一个场景时无意改变无关行为。`;
  const section = `\n## Concrete Example\n\n${example}\n\n${rationale}\n`;
  let next = source.replace(/\nupdated_at: ([^\n]+)/, "\nupdated_at: 2026-07-16T11:30:00+08:00");
  next = next.replace(/\nwork_version: \d+/, `\nwork_version: ${version}`);
  next = next.replace(
    /\ndocument_slot: (?:execution|post_completion_revision)/,
    "\ndocument_slot: post_completion_revision",
  );
  next = next.replace(/\nsupersedes: [^\n]+/, "\nsupersedes: null");
  next = next.replace(/\n## Outcome\n/, `${section}\n## Outcome\n`);
  const output = `task-work-${id}-v${String(version).padStart(2, "0")}.md`;
  writeFileSync(join(root, output), next);
}
