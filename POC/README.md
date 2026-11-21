# Skilleto PoC

**The right skills, right when you need them.**

A single portable Agent Skill for Codex and Claude Code. The host checks its
existing capabilities, discovers skills.sh candidates only for a real gap,
reviews fit and risk, obtains any required authorization, installs into the
project, verifies availability and resumes the original task. `NO_INSTALL`
is an intended successful decision.

## Layout and design

```text
POC/
  docs/PLAN.md, DEPLOY.md        specification and deployment runbook
  skills/skilleto/SKILL.md      portable entrypoint (name + description)
  skills/skilleto/references/  workflow, discovery, matching, security, provisioning
  tests/                      fixed scenarios, inert fixtures and observed results
```

The plan's illustrative `skilleto-poc/` root is this repository's existing
`POC/`; planning documents stay in `docs/`. Only `SKILL.md` loads initially;
references are read as needed. There is no runtime script, MCP server, backend,
database, Skilleto npm package, paid API or mandatory `find-skills` dependency.
The MCP-backed MVP remains separate.

## Quick start

Review [the skill](skills/skilleto/SKILL.md) and its references. Copy the
**whole** `POC/skills/skilleto/` directory to one project target:

| Host | Destination |
| --- | --- |
| Codex | `<project>/.agents/skills/skilleto/` |
| Claude Code | `<project>/.claude/skills/skilleto/` |

Do not overwrite an existing skill. Start a new host session or refresh its
skill inventory. Give the agent a task, then say:

```text
Použij Skilleto.
```

Or give an ordinary specialist task, such as:

```text
Prozkoumej tento repozitář a navrhni strategii property-based testování.
```

The host may choose Skilleto during planning or code inspection. Native
`$skilleto` (Codex) and `/skilleto` (Claude Code) are optional diagnostics.
Without task context, Skilleto asks for the objective only.

See [DEPLOY.md](docs/DEPLOY.md) for PowerShell/POSIX copy instructions,
optional authorized CLI installation, verification and smoke tests. From this
repository root the CLI source is `./POC`, not `.`. Skilleto has not been
published to skills.sh by this implementation.

## Guarantees and limits

Decisions are `NO_INSTALL`, `REUSE_EXISTING`, `RECOMMEND`, `INSTALL_APPROVED`
or `BLOCK`. Authorization, install success and session activation are separate.
Third-party CLI first execution may fetch/run npm code and requires consent;
candidate installation needs its own exact authorization or a prior narrow
policy. Project-local scope is mandatory. HIGH/UNKNOWN risks block acquisition;
MEDIUM requires verified mitigation and informed approval.

The instructions preserve host permissions; they cannot enforce sandboxing,
certify supply-chain integrity, or force model-selected invocation. Installing
files does not establish current-session availability. Offline/declined paths
continue with available tools. No automatic updates, global installation,
feedback service, composition or host configuration edits are included.

## Verification

[Scenarios](tests/scenarios.md) define P01–P21, including explicit/implicit
invocation and negative safety cases. [Results](tests/results.md) distinguish
actual runs, controlled simulations and `NOT_RUN`. Use the
[per-run worksheet](tests/results-template.md) for additional host testing.
Full PoC acceptance requires observed native host behavior and approved real
provisioning; documentation and simulated decisions alone do not establish it.
