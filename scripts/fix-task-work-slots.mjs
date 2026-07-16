import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const root = process.cwd();
for (const file of readdirSync(root).filter((name) =>
  /^task-work-[0-9a-f-]+-v(?:07|09)\.md$/.test(name),
)) {
  const path = join(root, file);
  const source = readFileSync(path, "utf8");
  if (source.includes("document_slot:")) continue;
  const next = source.replace(
    /\nwork_version: (?:7|9)\n/,
    (match) => `${match}document_slot: post_completion_revision\n`,
  );
  writeFileSync(path, next);
}
