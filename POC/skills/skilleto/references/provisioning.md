# Supervised project provisioning

## Prepare a concrete, reviewable proposal

Apply [security-policy.md](security-policy.md) first. Confirm the host from
session context; do not guess from the presence of skill folders. Verify the
absolute project root, shell/platform, Node/npx, approved CLI version and host
target. Host tools and sandbox restrictions remain authoritative. If a tool
or permission is unavailable, recommend/fallback without installing system
dependencies, escalating or changing policy.

| Host | CLI agent ID | Project skill path |
| --- | --- | --- |
| Codex | `codex` | `<project>/.agents/skills/<exact-name>/` |
| Claude Code | `claude-code` | `<project>/.claude/skills/<exact-name>/` |

The upstream installer may keep canonical files in `.agents/skills/` and link
host paths, including Claude Code. Inspect actual planned storage and link
targets; every destination must remain in the authorized project. Shared
storage may expose a skill to other agents using that directory; disclose
this if present and stop if it conflicts with authorized host scope.

Before mutation, inspect the exact name in host paths, shared storage and
project lock records. Compare identity/content with any existing skill.
Reuse an adequate existing copy. A same-name different source or changed
revision is a conflict, not permission to update. Obtain separate overwrite
approval and create a reversible backup if replacement is necessary.

Record the pre-install files, links and relevant lock entries (plus worktree
status if applicable); preserve user changes. Do not use a broad reset or
backup unrelated private files. This snapshot bounds recovery.

Present the proposal in the user's language, for example:

```text
Skill: <exact name>; purpose and concrete benefit: <...>
Source: <canonical listing, owner/repo, skill path, reviewed revision>
Review: <fit, risk, reviewed files, findings, verified mitigations, uncertainty>
Target: <absolute project, host, canonical storage and any links/lock records>
CLI execution: <already authorized version/policy, or separate consent needed>
Command: <fully resolved, shell-quoted command with exact arguments>
Expected effects: <files, dependency/network effects, refresh needs>
May I install this reviewed skill into that project with these effects?
```

Ask only when existing authorization does not already cover the exact action.
Record the user's reply or the specific prior narrow policy. A general task,
Skilleto invocation, positive search result, CLI prompt or elapsed time is not
installation consent. Decline means `RECOMMEND`, no installation, and continue
the task. CLI first-execution consent is a distinct gate; see
[discovery.md](discovery.md). It may be requested alongside the fully specified
install if both scopes are explicit.

## Execute only the authorized plan

Check approved CLI help for the installed version before relying on flags or
pin syntax. Documentation examples use:

```text
npx skills add <verified-source> --skill <exact-name> -a codex
npx skills add <verified-source> --skill <exact-name> -a claude-code
```

Choose **one** command for the confirmed host, from the approved project root.
The current upstream documents `owner/repo@<tag-or-full-commit>` revision pins;
use them only if the approved version supports them. Prefer a full reviewed
commit. If it cannot be pinned, inspect an immutable checkout and propose its
exact local path when supported, or stop if the reviewed artifact cannot be
preserved. Do not substitute a moving branch for approved reviewed content.

Construct arguments from verified literal identifiers. Reject shell
metacharacters/option injection; use correct platform quoting or an argument
array, never string evaluation of fetched/user text. Keep the approved CLI
version stable (e.g. `npx skills@<approved-version>` when applicable).

No `-g`/`--global`, `--all`, wildcard agent/skill, blanket update or extra host.
Do not follow a global upstream recipe. Global scope is outside this PoC;
explain the project-local alternative. `-y`/`--yes` may be used only **after**
specific authorization covers the exact action and skipped prompts reveal no
unreviewed choices. Prefer normal confirmation; never use prompt bypass to
obtain execution consent. Do not run downloaded scripts automatically.

If CLI prompts reveal extra skills, different scope, unreviewed dependencies,
overwrite or other unexpected effects, cancel. Reassess and obtain any missing
authorization before a changed action. Stop after failure; do not retry with
broader permissions or silently change source/version.

## Verify disk and session separately

1. Inspect exact installed paths, symlink targets, `SKILL.md`, references and
   project tracking/lock entries. Use `npx skills list` if CLI execution is
   authorized. Confirm exact skill/source/revision, compare all installed
   relevant files to reviewed content, and check the workspace delta for
   unexpected files, hosts or global effects. A list entry or exit code alone
   is insufficient. Unexpected content stops activation pending review.
2. Report `INSTALLED_ON_DISK` only with that evidence. Verify current-session
   availability through the host skill inventory/loading or a harmless native
   invocation. A direct file read is not proof of native discovery/loading.
3. Report `AVAILABLE_TO_CURRENT_SESSION` only when observed. Otherwise report
   `refresh required` or `unverified`, give a host refresh/new-session step,
   and continue safely with existing capabilities. Do not promise a new skill
   will automatically enter this session.
4. Resume the original task with the skill if available. Report authorization,
   provisioning, activation and remaining work separately using
   [workflow.md](workflow.md).

## Partial failure and recovery

Stop further installation on nonzero exit, content mismatch or unexpected
side effects. Compare the pre-install snapshot with the actual delta. Revert
only files/links/lock entries demonstrably created or changed by this attempt,
and only if no intervening user edits would be lost. Resolve absolute paths
and ensure they stay inside the authorized project before any recursive
cleanup; do not traverse symlinks into other locations.

Preserve pre-existing skills and unrelated work. Never remove all of
`.agents`, `.claude`, a skills directory, or a lock file to clean one entry.
Do not blindly run `skills remove`: shared canonical storage or links may
affect other hosts. If changes cannot be isolated, leave them intact and
report exact known paths and manual recovery instructions. Report provisioning
`failed` even if recovery succeeds; authorization is not installation success.

Version-sensitive sources:
[CLI commands](https://github.com/vercel-labs/skills/blob/main/docs/commands.md),
[agent paths](https://github.com/vercel-labs/skills/blob/main/docs/agents.md),
[Claude Code skills](https://code.claude.com/docs/en/skills).
