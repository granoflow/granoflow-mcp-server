# Git Task Checkpoint Workflow

Use this contract only after `git-capability-detection.md` reports a safe normal
repository. Git is a host execution capability: Granoflow MCP stores and
resolves preferences, while the host Agent runs fixed Git commands in the
authorized repository. MCP must not become a repository automation engine or
call a Granoflow CLI wrapper. Preferences never authorize a commit by
themselves; a local checkpoint also requires current Task Work authorization.

## Checkpoint Gate

Run only when all conditions are true:

1. Git is available and the workspace is a safe normal repository state.
2. Resolved `git.checkpoint.enabled=true`.
3. Current Task Work explicitly authorizes a local commit for this task.
4. The last required test node has deterministic passing evidence.
5. The task has an explicit owned-file set derived from Task Work and actual
   Delivery; no path is inferred from `git status` alone.

Before staging, capture `HEAD`, index entries, worktree status, task-owned
paths, and range-excluded dirty paths. Stop if ownership is ambiguous, an
unrelated path is already staged, a conflict is active, or HEAD changed since
the proposal.

Stage with explicit pathspecs. Never use `git add -A`, `git add .`, automatic
`stash`, `reset`, `clean`, or checkout-based cleanup. Review the staged
name/status and full staged diff. Run:

- the repository's documented full quality gate;
- structural limits and format/type/static checks included by that gate;
- a secret scan over staged content;
- normal repository commit hooks, without `--no-verify`.

Any failure blocks the checkpoint. Do not weaken a gate or expand the staged
set to make a commit succeed.

## Commit And Readback

Use a message that identifies the user outcome or Granoflow task. Create one
local commit, then verify:

- the returned SHA resolves to `HEAD`;
- the commit tree changes exactly the approved task-owned set;
- excluded worktree changes remain untouched;
- hooks passed;
- no remote command ran.

Record the SHA, parent SHA, files, gate commands/results, and remaining worktree
state in Task Delivery. Never push automatically. If commit succeeded but
readback is inconclusive, preserve the candidate SHA and stop; do not create a
second commit.

## Completion Boundary

The checkpoint belongs after deterministic task verification and before the
final Delivery/node completion readback. A missing Git executable is a normal
skip, not a failed task. A configured checkpoint that is blocked by dirty-scope,
secret, hook, conflict, or authorization evidence remains a real task blocker.
