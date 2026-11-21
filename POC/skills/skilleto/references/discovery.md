# Bounded discovery through skills.sh

Use only after the [capability check](workflow.md). The playbook comes from
[find-skills on skills.sh](https://www.skills.sh/vercel-labs/skills/find-skills)
and its [upstream source](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md):
identify domain and task, query specific terms, inspect candidates, and propose
useful installation. An already available `find-skills` may help, but do not
install it as a bootstrap dependency.

## Tool preflight and consent

Check available shell/network permissions and local `node --version`,
`npm --version`, `npx --version` where permitted. These local version checks
do not authorize fetching packages. Do not auto-install prerequisites or
change execution policy. On Windows an approved Node installation may expose
`npm.cmd`/`npx.cmd`; use those entrypoints if allowed instead of changing
PowerShell's script policy.

Running `npx skills`, including `find`, `list` or `--help`, can download and
execute npm code. Before first use of an untrusted CLI, obtain specific consent
for that execution unless prior authorization covers it. State the upstream
package/source, purpose, network/package execution implications and scope.
This is distinct from consent to install a candidate. Do not use `-y` or
another prompt bypass to manufacture consent. If a CLI version was reviewed
and approved, keep that version for search/help/install; a changed version
requires checking the authorization again.

Without CLI execution consent or working tools, do not invoke it. Record
`DISCOVERY_UNAVAILABLE` for the CLI route. A permitted read-only inspection
of verified skills.sh listings and their source repositories can still inform
a recommendation; label it as a web fallback rather than a successful CLI
search. Never fabricate results or present remembered names as verified ones.

## Search and source evidence

For each true gap form 1–3 high-information queries, preferably English
technical terms. Use the host shell with correctly quoted literal arguments:

```text
npx skills find 'python hypothesis stateful testing'
npx skills find 'github actions cache monorepo'
```

These are command shapes, not evidence of results. Upstream `find-skills` may
suggest a leaderboard first; at most use a single relevant look as a weak
discovery hint. The PoC still uses bounded CLI queries when available. Ignore
upstream global/automatic install recipes and popularity thresholds as policy.

Retain at most three promising candidates per gap. For each, record:

- Canonical skills.sh listing URL and actual result/query evidence.
- Exact owner/repository, source URL, skill directory and `name` from the full
  `SKILL.md`; distinguish same-named skills from different sources.
- Revision/commit or tag and retrieval date when verifiable. Prefer immutable
  source links so the eventual install can match the review.
- Required capabilities/tools and relevant referenced content to inspect.

Follow source links only as evidence. Confirm the actual repository identity
and resolved revision, not a similarly named search result or redirect.
Source hosting may be GitHub or another upstream Git host; that is provenance
verification of a skills.sh candidate, not permission to search other registries.

Do not run `add`, `use`, `update`, remote setup commands or downloaded scripts
as a discovery shortcut. Non-installing inspection such as `add --list` still
requires approved CLI execution and must not replace full content review.
If no relevant candidate survives the bounded search, report that observation
and continue the original task. Do not expand into an exhaustive catalog scan.

Next: [semantic matching](semantic-matching.md), followed by
[security review](security-policy.md). The
[CLI command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
is version-sensitive; inspect help only after the CLI execution gate is met.
