# Decision workflow

## Assess before acquiring

Preserve the user's original objective, acceptance criteria, workspace and
authorization. Resolve terse invocation from conversation/project context. If
no objective exists, ask for it only; discovery has nothing to match yet.

List at most 3–5 capability needs, not a multi-agent execution graph. Inspect
the host skill inventory, available tools and relevant repository context.
Inspect project-local skill paths where necessary; use `npx skills list` only
if CLI execution is already authorized (see [discovery.md](discovery.md)). An
installed skill that cannot load is not a currently available capability.

Ask whether existing tools and instructions can meet the acceptance criteria.
A complex task alone is not proof of a gap. State the concrete expected
improvement of any proposed skill. Prefer direct work or an installed
equivalent when benefit is marginal. No online check is needed for this exit.

## Outcomes and stop conditions

Select exactly one **current** decision. Other statuses describe evidence or
execution; they are not additional decisions.

| Decision | Use when | Continue with |
| --- | --- | --- |
| `NO_INSTALL` | Native capabilities suffice, benefit is marginal, or bounded search found no useful match | Original task with available tools |
| `REUSE_EXISTING` | An adequate installed skill exists; acquisition is unnecessary | Use it if available, otherwise give a refresh step and fallback |
| `RECOMMEND` | A useful candidate is identified, but consent, tooling or activation is pending/unavailable, including declined consent | Explain the constraint; do independent work |
| `INSTALL_APPROVED` | Reviewed candidate and exact install are authorized | Scoped provisioning and verification |
| `BLOCK` | Candidate is unsafe, unreviewable, unknown, or violates the policy | Reject that candidate; continue safely |

`INSTALL_APPROVED` records authorization, not success. It may have provisioning
`failed` or activation `refresh required`. `BLOCK` concerns the unsafe
acquisition, not permission to abandon the user's task. If a safe alternative
is selected later, report the new current decision and retain the rejection
reason in candidate evidence.

After assessment, use [discovery.md](discovery.md) only for a true gap. Bound
search to 1–3 queries per gap and up to three shortlisted candidates per gap.
Use [semantic-matching.md](semantic-matching.md), then the
[security gate](security-policy.md), then [provisioning](provisioning.md).
Do not install several skills speculatively; explain why each is necessary.

Stop acquisition when existing capabilities suffice, the search budget is
exhausted, no relevant result exists, content cannot be reviewed, risk blocks
installation, consent is absent/declined, tools are unavailable, or an install
fails. Do not loop through equivalent queries, broaden permissions, switch
registries or treat repeated failures as authorization.

For unavailable discovery record `DISCOVERY_UNAVAILABLE` plus the actual cause.
Use `RECOMMEND` only if a useful candidate really is identified; otherwise use
`NO_INSTALL` with the limitation, not a claim that no suitable skill exists.
If an existing suitable skill is on disk but unavailable to the session, state
`REUSE_EXISTING` with activation `refresh required` and use a safe fallback.

## Observable report

Give a brief report in the user's language. Combine fields into short prose
for routine exits; preserve these facts when applicable:

```text
Original task: <goal>
Capability gap: <specific need or none>
Decision: NO_INSTALL | REUSE_EXISTING | RECOMMEND | INSTALL_APPROVED | BLOCK
Search performed: yes/no; <queries, skipped reason, or DISCOVERY_UNAVAILABLE cause>
Candidate: <exact name, owner/repo, skill path, canonical URL, revision> | none
Fit: HIGH | MEDIUM | LOW | N/A; <reason>
Risk: LOW | MEDIUM | HIGH | UNKNOWN | N/A; <evidence and remaining uncertainty>
Scope: <absolute project, host, target paths> | N/A
Authorization: approved | denied | not requested | not required; <CLI/install scope>
Provisioning: not attempted | installed | failed | blocked
Activation: available now | refresh required | unverified | N/A
Next action: <original task progress and any specific required user action>
```

For a reviewed candidate include the reviewed file/revision evidence and any
mitigations in the proposal or report. Never conceal that no installation
occurred. If a user response is necessary, leave that proposal pending and
continue independent portions of the original task. If none remain, explain
the concrete dependency. A skill search alone is not task completion.
