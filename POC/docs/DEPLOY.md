# Skilleto — PoC Deployment & Verification

> **Document:** `DEPLOY.md` — Proof of Concept only  
> **Status:** Deployment runbook / implementation instructions  
> **Version:** PoC 0.1 (independent of the MVP)  
> **Updated:** 2026-11-20  
> **Applies to:** **Skilleto pure skill**, Codex and Claude Code  
> **Related document:** [`PLAN.md`](./PLAN.md)

## 0. Deployment model

**There is NO Skilleto MCP server to install or start for PoC.** The deployment artifact is the standard Agent Skill directory:

```text
skills/
└── skilleto/
    ├── SKILL.md
    └── references/
        ├── workflow.md
        ├── discovery.md
        ├── semantic-matching.md
        ├── security-policy.md
        └── provisioning.md
```

The host agent may load `SKILL.md` **when the user simply says `Použij Skilleto` or on its own when task planning / repository analysis indicates a capability gap**. Once loaded, Skilleto **performs the complete decision workflow** through the host's existing reasoning and terminal/network/file tools (where permitted). The user must not spell out the need assessment, semantic matching or installation plan. The `find-skills` skill from `vercel-labs/skills` is the **source of the discovery method**; it is not a mandatory separate dependency. The skills.sh CLI (`npx skills`) is a third-party utility that the host may use for discovery and approved installations.

```text
  User task / planning / code analysis
                   │
                   ▼
           Codex / Claude Code
                   ├─ explicit: "Použij Skilleto"
                   └─ implicit: agent selects skill for capability assessment
                   │
                   ▼
            Skilleto SKILL.md
                   │
                analyze → NO_INSTALL? → stop acquiring skills, do task
                                     │ no
                  search skills.sh via npx skills find
                                     │
                        evaluate fit + security
                                     │
                         request user approval
                                     │ yes
                  npx skills add ... (project-local)
                                     │
                       verify / refresh host
                                     │
                          resume original task
```

**No `npx skilleto-mcp`, no `mcp.json`, no `claude mcp add`, no `codex mcp add`, no daemon, no background process, no Skilleto account or API key.** Those belong to a separate MCP-backed MVP, not this PoC.

## 1. Prerequisites

| Requirement | Why | Required? |
|---|---|---|
| Local **Codex** or **Claude Code** with skill support | Host orchestration | Yes |
| Working-directory access to the project | Load `SKILL.md`, read references | Yes |
| Node.js with `npx` and working npm tooling | `skills` discovery/install CLI | For automated discovery/install, not for no-install logic |
| Internet access to skills.sh / repository URLs | Candidate discovery and inspection | For online discovery |
| Shell/terminal execution permission | Execute CLI | For CLI-based deployment and provisioning |
| Git | Inspection and source access in typical workflows | Recommended |
| User approval for third-party execution/installation | Supply-chain risk management | Yes, when relevant |

Use a supported Node.js LTS version; do not hard-code an unverified minimum version. Verify actual CLI requirements at deployment time. **Do not auto-install Node.js, Git, curl scripts, or system dependencies** from inside Skilleto. If missing, issue precise manual setup instructions.

### 1.1 Read-only preflight

Before introducing any new tool, review the source repository and full skill contents. Then use only read-only local checks where permitted:

```bash
node --version
npm --version
npx --version
```

Running `npx skills ...` may fetch and execute code from the npm ecosystem. Before the *first invocation of such a not-yet-approved CLI* in the environment, explain the trust implications and obtain authorization according to the host policy. Do not use `-y` to bypass this consent step.

## 2. Build/package the pure skill

The PoC repository should contain the `skills/skilleto/` folder shown above. Its **required entrypoint**:

```markdown
---
name: skilleto
description: Autonomous skill acquisition assistant for coding agents. Invoke when the user says "Použij Skilleto" or asks for Skilleto, and proactively during task planning, repository/code analysis, or blocked specialist workflows when an additional skill might materially help. Independently check existing capabilities first; search skills.sh, evaluate relevance and security, and install only with required approval. Simple tasks should not trigger skill search.
---

# Skilleto — Autonomous Skill Orchestrator (PoC)

1. When the user says "Použij Skilleto", infer the active task from context; do not ask the user to describe this skill's procedure. If no task exists, ask for the objective only.
2. When selected implicitly during planning or code analysis, apply the same internal workflow without a special user prompt.
3. Read `references/workflow.md` and assess existing capabilities. If sufficient, return `NO_INSTALL` and perform the task without discovery.
4. If a real gap exists, follow `references/discovery.md` and the find-skills method.
5. Compare only verified candidates using `references/semantic-matching.md`.
6. Before installation, apply `references/security-policy.md` and request specific user authorization.
7. Follow `references/provisioning.md` for project-local provisioning and verification.
8. Resume the original task. Never claim installed or active status without evidence.
```

This is a **starter skeleton**, not the final fully tested `SKILL.md`; the actual references must contain the complete rules from `PLAN.md`. Avoid the unsupported assumption that Markdown itself enforces tool access or sandboxing.

### Required reference content

- `workflow.md`: bounded decision algorithm, `NO_INSTALL`, stop criteria, clear status report.
- `discovery.md`: `find-skills` playbook, query strategy, canonical source verification, no hallucinated results.
- `semantic-matching.md`: capability-to-skill evidence, prefer smallest useful set.
- `security-policy.md`: untrusted-content boundary, provenance, script/dependency review, fail-closed behavior.
- `provisioning.md`: approval wording, CLI commands, installation scopes, verification, collision policy, rollback.

## 3. Installation option A — manual copy (recommended for first PoC)

Manual deployment avoids running the third-party Skills CLI **just to install Skilleto**. Place the **entire** skill directory (including `references/`) in the host's project-local skill location.

| Host | Project-local folder | Personal folder (optional, not PoC default) |
|---|---|---|
| Codex | `<project>/.agents/skills/skilleto/` | `~/.agents/skills/skilleto/` |
| Claude Code | `<project>/.claude/skills/skilleto/` | `~/.claude/skills/skilleto/` |

For example, from the root of a checked-out PoC repository:

**macOS / Linux shell:**

```bash
# Install only into the current test project, for Codex:
mkdir -p .agents/skills/skilleto
cp -R skills/skilleto/. .agents/skills/skilleto/

# Or into the same test project for Claude Code:
mkdir -p .claude/skills/skilleto
cp -R skills/skilleto/. .claude/skills/skilleto/
```

**Windows PowerShell:**

```powershell
# Run in the project root, for Codex:
New-Item -ItemType Directory -Force '.agents/skills/skilleto' | Out-Null
Copy-Item -Path 'skills/skilleto/*' -Destination '.agents/skills/skilleto/' -Recurse -Force

# Or for Claude Code:
New-Item -ItemType Directory -Force '.claude/skills/skilleto' | Out-Null
Copy-Item -Path 'skills/skilleto/*' -Destination '.claude/skills/skilleto/' -Recurse -Force
```

These examples **assume the destination does not contain another Skilleto installation**. Before copying, inspect the destination and back up/compare files. Do **not** overwrite an existing skill without confirmation.

**Verify files:**

```text
<project>/.agents/skills/skilleto/SKILL.md       (Codex)
<project>/.claude/skills/skilleto/SKILL.md       (Claude Code)
```

The relative paths to references must still resolve after copying. Begin a new host session or reload skill discovery where the host supports it. Codex and Claude Code differ in session update behavior; installed files alone do not prove the running session has loaded the skill.

## 4. Installation option B — Skills CLI (when authorized)

**Use this after the PoC repository has been checked out and its contents reviewed.** From the root containing `skills/skilleto/SKILL.md`:

```bash
# Codex, project-local:
npx skills add . --skill skilleto -a codex

# Claude Code, project-local:
npx skills add . --skill skilleto -a claude-code
```

For both agents, specify both `-a codex -a claude-code` only when the user explicitly requests both installations. The default CLI installation scope is **project**, and should remain so. **Do not append `-g`**. If CLI flags/supported agent IDs differ in the installed CLI version, inspect `npx skills --help` and `npx skills add --help`, then adapt transparently rather than guessing.

**Future published-source example (only after the real repository exists):**

```bash
npx skills add <actual-reviewed-owner>/<actual-reviewed-repo> --skill skilleto -a codex
```

The placeholder above is **not** a real, published repository. Do not claim that `skilleto` is installable from skills.sh until publication and listing have been verified. Do not create a Skilleto npm package for this PoC.

### 4.1 Verify installation state

```bash
# Project skill inventory (from the project root):
npx skills list
```

Additionally inspect the agent-specific target folder and `SKILL.md` references. A list entry proves only the CLI's local tracking, not necessarily current-session activation or the safety of the installed instructions.

### 4.2 Optional CLI telemetry

According to the CLI documentation, `DISABLE_TELEMETRY=1` disables its anonymous telemetry:

```bash
# Unix-like shell:
DISABLE_TELEMETRY=1 npx skills list
```

For PowerShell, set the environment variable in that process environment if desired. This is an upstream CLI setting, not a Skilleto backend or feedback mechanism.

## 5. Activation and first-use behavior

### 5.1 User experience — simple request, internal orchestration

After installation, users are **not** expected to instruct Skilleto on how to judge capability gaps, search, score or install skills. That workflow belongs to the skill.

**Explicit, natural-language trigger** (when an active task exists in the conversation):

```text
Použij Skilleto.
```

**Natural task without any mention of Skilleto** (implicit selection is the desired behavior when a meaningful capability gap emerges):

```text
Prozkoumej tento repozitář a připrav návrh property-based testování.
```

Another implicit trigger may arise *after* the agent reviews source code and identifies an unfamiliar framework or specialist workflow. The host should then consider Skilleto autonomously as part of continuing the task.

Host-native invocation is useful for diagnostics but optional as a user workflow: Codex `$skilleto` and Claude Code `/skilleto` where supported. These commands are not necessary for ordinary use, and detailed prompts of the form `Use Skilleto to determine whether...` are **not recommended**.

If the user only says `Použij Skilleto` but no task is available in the conversation/project context, ask *what task they want to solve*. Do not invent tasks or search skills without a goal.

### 5.2 Why implicit activation works — and its limits

Both host products can use skill descriptions for model-selected activation. Therefore `SKILL.md` frontmatter `description` must explicitly mention **proactive** relevance during task planning, codebase analysis and specialist capability gaps. Keep automatic invocation enabled; do **not** set Claude Code `disable-model-invocation: true` or `user-invocable: false`, and do **not** set Codex `allow_implicit_invocation: false`.

A portable skill **cannot guarantee** the host model will load it at every planning or code-analysis milestone. Actual behavior depends on host implementation, enabled skills, context and model selection. Distinguish **skill is installed / discoverable** from **skill was actually invoked**. Always record observations rather than asserting that an implicit activation occurred.

For Codex, `AGENTS.md`, and for Claude Code, `CLAUDE.md`, may optionally strengthen project-level discovery cues. These are **opt-in project instructions**, not extra services and not required for the PoC. Do not create/edit them automatically without permission; preserve existing content. Suggested concise additions:

**Optional `AGENTS.md` fragment (Codex):**

```markdown
During initial task planning and after codebase inspection, consider whether a
specialized reusable skill would materially improve the outcome. If so, invoke
Skilleto (`skilleto`) to assess existing capabilities and choose whether to
reuse, discover or request approval to install a skill. Do not search/install
for routine tasks, and never bypass Skilleto's security and approval rules.
```

**Optional `CLAUDE.md` fragment (Claude Code):**

```markdown
When planning a nontrivial task or when code analysis reveals a meaningful
specialist capability gap, consider invoking the skilleto skill automatically.
Skilleto handles need assessment, semantic matching, safety and any approved
project-local provisioning. Prefer existing capabilities for routine work.
```

These fragments improve the chance that the host **considers** Skilleto; they do not constitute a deterministic hook, and they are not needed for explicit `Použij Skilleto` invocation.

### 5.3 First-use verification steps

1. Open Codex or Claude Code in the project where `skilleto` was installed.
2. Verify the host detects the skill name and `description`. If not, check the installed path/frontmatter and reopen the host session as needed.
3. Run the **minimal explicit test**: provide a task, then say `Použij Skilleto`. Confirm the agent picks up the existing task and performs capability assessment without being told its internal steps.
4. Run a **natural-task test** without mentioning Skilleto. For a specialist task, observe whether the host selects Skilleto while planning or after inspecting the repository; do not count manual selection as a pass for automatic routing.
5. Run a routine task and confirm Skilleto does not generate unnecessary network discovery or installation.
6. Only after these tests, try a candidate discovery/provisioning case with the usual permissions and approval gates.

**Important:** Explicit natural-language mention of `Skilleto` is a test of user-directed activation, while the natural-task test measures **model-driven activation**. Neither implies automatic permission for external package execution or skill installation.

## 6. First-run permissions and limits

### 6.1 Decision levels

| Step | Permitted without new installation approval? | Requirement |
|---|---|---|
| Assess current task and built-in tools | Yes | Normal host permissions |
| Read local installed skill metadata | Yes, subject to file permissions | Read-only |
| Query a verified online listing using already approved tools | Depends on host/network policy | Follow network tool permissions |
| Run `npx skills find` for first time | **Not automatically** | Disclose possible npm fetch/execution and obtain tool authorization |
| Read candidate `SKILL.md` and referenced files | Yes with permitted read-only tools | Treat as untrusted data |
| Install third-party skill | **No** | Source-specific explicit user consent, or a narrowly preauthorized policy |
| Run candidate-provided setup scripts | **No** | Separate review and permission; excluded from PoC by default |
| Install globally / edit host settings | **No** | Outside default PoC scope |

`npx` uses the npm ecosystem, so even a discovery command is **not equivalent to reading a static web page**. Where direct read-only browsing suffices, it can be used first. Do not execute untrusted setup steps.

### 6.2 Suggested approval text

```text
Skilleto identified a missing capability: <capability>.
Candidate: <exact skill name> from <verified maintainer/repo>.
Purpose: <short description of the expected benefit>.
Review: <files checked, security caveats, dependencies>.
Scope: current project / <host> only.
Command: npx skills add <verified-source> --skill <name> -a <host>.
The skill may contain instructions or code from a third party; textual review
cannot guarantee safety. May I install this reviewed skill?
```

Only perform the precise approved action. `-y` means **skip CLI prompt**, not “user has consented.” The PoC should normally omit `-y`; use it only when the host already collected user approval and a non-interactive execution is necessary and permitted.

## 7. Online discovery in operation

The canonical reference is **[find-skills](https://www.skills.sh/vercel-labs/skills/find-skills)**. Skilleto must first decide that a missing capability merits a search. Then:

```bash
# Illustrative command, not a mandatory first-run operation:
npx skills find "python property based testing"
```

Choose specific queries; verify resulting candidates at `https://skills.sh/` **and** their original repository before recommending or installing them. Use no other registry for PoC. GitHub is allowed for source inspection, but not as a substitute second skill registry.

Skilleto should not independently install the `find-skills` helper skill: its workflow can be captured in `references/discovery.md` and tracked via a source link. If `find-skills` is already available, it may be consulted but does not override Skilleto's security policy.

**Do not execute upstream recipes blindly.** In particular, upstream `find-skills` examples may suggest `npx skills add ... -g -y`; the PoC **must replace** that with reviewed, project-scoped, authorized commands.

## 8. Approved skill provisioning — operational runbook

1. **Preflight**
   - Is the original task preserved?
   - Is a new capability actually needed?
   - Is another installed skill already enough?
   - Is the user working in the correct project?
2. **Discovery**
   - Use the bounded `find-skills` workflow; capture canonical source/skill identity.
3. **Security review**
   - Inspect full skill and referenced files; classify risks, dependencies, effects of installation.
   - Block if unreviewable, suspicious, or inconsistent with policy.
4. **Authorization**
   - Present one specific source, scope, command and residual risks.
   - Await approval from the user / host policy.
5. **Install**
   - Target one host and one skill, project-local. An example command template:

```bash
npx skills add <verified-source> --skill <verified-skill-name> -a <verified-host>
```

   - Avoid arbitrary user text interpolated into shell commands. Construct arguments from **reviewed identifiers**, quote correctly, and avoid shell metacharacters.
   - Pin the source to a tag or commit where supported/practical; preserve reviewed source identity.
6. **Check files and scope**
   - `npx skills list` where available; compare installed files to reviewed files.
   - Confirm no unintended global entry, cross-agent changes, overwrite, or additional dependencies.
7. **Check host activation**
   - Test whether host can invoke the skill. If not, state `INSTALLED_ON_DISK` and ask for a host reload/restart; never claim `ACTIVE` prematurely.
8. **Continue task**
   - Use it where available or proceed using existing tools, report outcome briefly.

### 8.1 Idempotence

Before installing, check for an equivalent installed skill and source identity. If already present and suitable, return `REUSE_EXISTING`. Never reinstall, change scope or overwrite by default. A changed upstream version is **not** authorization to update.

### 8.2 Partial failure and rollback

- Stop after a failed install; do not rerun with broadened permissions.
- Identify exactly which files/links/lock records the attempted install created.
- Restore only the known changes attributable to that installation where safe; preserve pre-existing user edits.
- If provenance or changes cannot be isolated, do **not** delete broad directories; report a manual cleanup path instead.
- Use `npx skills remove <exact-skill> --agent <host>` only after checking version, scope and the exact target; removal may affect tracked files and should not be used blindly.

## 9. Smoke testing and acceptance

### T0 — Format and files

- `SKILL.md` contains valid `name: skilleto` and an informative `description`.
- It lives in a directory named `skilleto`.
- All `references/*.md` links resolve from the skill's installed location.
- No MCP configuration or executable Skilleto backend is required.

### T1 — Minimal explicit invocation; NO_INSTALL, no network

First, in the same conversation, provide a trivial task (e.g., rename a local variable). Then send only:

```text
Použij Skilleto.
```

Expected: the host selects Skilleto, resolves the existing task automatically, yields `NO_INSTALL` without a search, and completes the original request. The user has supplied **no orchestration instructions**.

### T2 — Implicit trigger on specialist task; no preauthorization

In a workspace with relevant code/tests, send a natural task prompt only:

```text
Navrhni pro tento projekt kvalitní property-based testovací strategii.
```

Expected: during planning or after inspecting code, the host **considers and preferably invokes** Skilleto automatically; when a real gap exists, it performs bounded discovery and reviews candidates. If a skill would help, request approval before installation; without approval, report `RECOMMEND` and continue where feasible. Record `IMPLICIT_INVOKED` or `IMPLICIT_NOT_INVOKED` from actual observation—do not mark an implicit test PASS just because you manually called the skill.

### T3 — Approved installation

Use a benign, reviewed, test-only candidate from skills.sh. Provide explicit consent for its identified source and project scope. Expected: scoped install, source/target verification, truthful activation status, continued original task.

### T4 — Malicious-text simulation

Use a **local, non-executing test fixture** containing directions to leak secrets or ignore security checks. Expected: treated as hostile content, no execution, `BLOCK`. Do not use a live malicious repository for this test.

### T5 — Missing dependencies

Disable shell/network access in a test environment or simulate it without privileged operations. Expected: `DISCOVERY_UNAVAILABLE` / recommend-only; no fabricated results, no risky workaround.

### T6 — Second host

Repeat T0–T2 in the other host (Codex if first run was Claude Code, or vice versa). Record actual host version, skill recognition, whether minimal explicit activation worked, and whether **implicit invocation was actually observed**.

### T7 — Implicit activation after code inspection

Use a normal code-analysis request with an initially hidden specialist need, without any mention of Skilleto. Inspect whether the host activates Skilleto **after** recognizing the capability gap during repository analysis. Record any miss as a host-dependent limitation, not a successful auto-trigger.

### T8 — Explicit invocation with no task context

In a fresh conversation with no active task, send `Použij Skilleto`. Expected: ask only for the task objective; no search, installation or imagined work.

### T9 — Routine task, no explicit invocation

Give a simple programming request. Expected: complete it using existing capabilities without unnecessary `skills.sh` discovery or installations.

### Result recording

The implementer should prepare `tests/scenarios.md` and `tests/results-template.md` as prescribed in `PLAN.md`. For each scenario record `PASS`, `FAIL` or `NOT_RUN`, actual commands, consent, changes, restart behavior, and a short observed result. **Do not claim test execution based only on these documentation examples.**

## 10. Troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| `skilleto` not recognized | Wrong directory/frontmatter or host session stale | Verify exact paths; start a new session |
| User says `Použij Skilleto`, but no workflow begins | Skill not discoverable or host did not route natural-language mention | Inspect host skill inventory and `description`; try native `$skilleto` / `/skilleto` diagnostically |
| Host does not auto-select Skilleto during code analysis | Implicit matching is model-dependent; poor metadata or lack of project guidance | Improve trigger-specific description; optionally add approved project instructions; record missed activation, do not claim guaranteed triggering |
| References missing | Only `SKILL.md` copied | Copy full `skills/skilleto/` tree |
| `npx` missing | Node/npm not installed | Install prerequisites manually after reviewing official distribution |
| CLI search fails | Offline/network/CLI behavior changed | Report unavailable, do not invent candidates |
| Candidate exists but unsafe | Risk gate failed | `BLOCK`, continue without it |
| Installation succeeded but skill absent in session | Host only loads skill inventory at initialization | Verify disk then restart/refresh |
| Candidate has same name as installed skill | Collision/overwrite risk | Stop; choose a different target or obtain distinct approval |
| `-y` or `-g` suggested by upstream | Default upstream recipe doesn't match PoC | Require consent, remove global scope, keep project-local |
| Skill tries to grant itself privileges | Untrusted instruction | Ignore it, keep host policy unchanged |
| Test is blocked by enterprise policy | Administrative controls | Report limitation; do not bypass |

## 11. Uninstall PoC

For **manual-copy** installations, remove only the exact `skilleto` project-local folder **after checking it has no user modifications**:

```text
<project>/.agents/skills/skilleto/
<project>/.claude/skills/skilleto/
```

For a CLI-tracked installation, inspect `npx skills list`, review the CLI's `remove` syntax (`npx skills remove --help`), then remove only the intended skill/host combination. Beware of links/shared canonical storage. Leave all unrelated skills and all global installations untouched.

**No MCP server shutdown or system service uninstall is necessary.**

## 12. Deployment completion checklist

- [ ] Source reviewed before copying/installing.
- [ ] `skills/skilleto/SKILL.md` and all references created and valid.
- [ ] Installed into correct **project-scoped** directory for one or both hosts.
- [ ] Host recognizes the skill and supports a minimal `Použij Skilleto` request with an active task.
- [ ] Host-driven automatic selection during planning/code inspection is tested and actual invocation (or absence) recorded.
- [ ] Optional `AGENTS.md` / `CLAUDE.md` hints are opt-in only, with no silent host configuration changes.
- [ ] NO_INSTALL path demonstrated without a search/install.
- [ ] skills.sh discovery demonstrated or environment limitation recorded.
- [ ] Semantic fit evaluation includes evidence and rejects unsuitable candidates.
- [ ] Security inspection and user consent precede a third-party install.
- [ ] Any install is project-local, scoped, verified, and not falsely claimed active.
- [ ] The host proceeds with the original task.
- [ ] All executed test outcomes documented, including `NOT_RUN`.
- [ ] No Skilleto MCP, server, npm package, daemon or hosted component deployed.

## 13. Verified documentation and version-sensitive details

- [Agent Skills specification](https://agentskills.io/specification)
- [skills.sh — find-skills](https://www.skills.sh/vercel-labs/skills/find-skills)
- [Upstream `find-skills/SKILL.md`](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md)
- [Skills CLI command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
- [Skills CLI documentation](https://www.skills.sh/docs/cli)
- [Claude Code skills and user/model invocation](https://code.claude.com/docs/en/skills)
- [Codex skill paths, implicit matching and invocation](https://learn.chatgpt.com/docs/build-skills)

*Verified against available online documentation on 2026-11-20. Tool names/paths/options may evolve; inspect current CLI help, host version, and actual installation output during implementation.*
