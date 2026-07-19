# Git Capability Detection

Use this contract when a software project may use Git. Git is a host execution
capability: Granoflow MCP stores and resolves preferences, while the host Agent
runs fixed read-only Git commands in the authorized workspace. MCP must not
become a repository automation engine or call a Granoflow CLI wrapper.

## Resolve Preferences First

Call `granoflow_agent_preferences_get` with the current `projectId`. Values
resolve field by field in this order:

1. current same-run or durable task authorization;
2. project `agent_preferences` in `project_rules.yaml`;
3. MCP-local `agentPreferences` defaults;
4. newcomer-safe defaults.

Preferences reduce repeated choices. They never authorize push, publish,
deploy, deletion, login, secret access, branch history changes, or a commit by
themselves.

## Read-only Detection

Use fixed arguments and an explicit workspace. Do not interpolate user text
into a shell command.

1. Resolve whether `git` is installed with the host's normal executable lookup.
2. If unavailable, inspect the resolved `git.missingNotice` value:
   - `once`: if the local marker is false, say one newcomer-friendly sentence
     and call `granoflow_git_missing_notice_record`; later runs stay silent.
   - `always`: report one sentence on each new project initialization.
   - `never`: stay silent.
3. Never ask the user to install Git, never permanently label them as a
   beginner, and never create an interaction node for missing Git. Skip every
   Git checkpoint and continue the non-Git task workflow. Missing Git is a
   normal skip, not a failure.
4. If Git exists, use read-only commands such as `git -C <workspace>
rev-parse --is-inside-work-tree`, `git -C <workspace> status
--porcelain=v1 -z`, and `git -C <workspace> symbolic-ref --short -q HEAD`.
5. Distinguish executable available, non-repository, unborn repository, normal
   branch, detached HEAD, merge/rebase conflict, and command failure. Detection
   must not change refs, index, worktree, config, hooks, remotes, or credentials.

For a Git executable outside a repository, report the fact once during project
initialization and continue. Do not run `git init` unless the user explicitly
requests it.

## Project Workflow

`git.workflow` uses these values:

- `current_branch`: use the existing branch as the project progress line. This
  is the default recommendation for a small, single-person project.
- `develop`: use an existing `develop` branch. Creating or switching branches
  remains a separately authorized action.
- `git_flow`: follow the repository's documented Git Flow conventions.
  Initializing Git Flow or creating branches remains separately authorized.
- `ask`: unresolved. In interactive project definition, show the current branch
  and the three choices above once. In unattended project definition, recommend
  `current_branch` unless repository evidence already proves a documented
  develop/Git-Flow convention, then save the evidence-backed result to the
  project YAML and report it as a notice.

Never infer `develop` or `git_flow` merely because a branch with that name
exists. Repository documentation and current project preference are stronger
evidence.
