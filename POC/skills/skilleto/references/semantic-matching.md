# Match capabilities, not names

For the shortlist from [discovery](discovery.md), read actual skill contents
and compare them to the user's acceptance criteria. A title or listing summary
alone cannot establish suitability.

| Dimension | Evidence to collect |
| --- | --- |
| Functional fit | Which specific need is covered, relevant instructions/examples, exclusions and unresolved requirements |
| Host compatibility | Codex/Claude Code support, Windows/POSIX assumptions, required shell, language, framework and tools |
| Added value | Concrete improvement over native reasoning, tools and installed equivalents |
| Footprint | Extra packages, scripts, services, access, setup and maintenance burden |
| Provenance/maintenance | Verified source identity, revision, relevant history, stale or incompatible instructions |

Record evidence or `unknown` for each dimension; do not invent maintenance
history or numeric semantic similarity. Popularity can break a tie between
otherwise suitable candidates, but does not prove fit, security or quality.

- `HIGH`: covers the material need, fits the environment, and adds clear value.
- `MEDIUM`: partially covers the need or needs a known, feasible adaptation;
  specify the uncovered portion and cost.
- `LOW`: name-only match, incompatible workflow, major exclusions, duplication,
  or little benefit. Reject even if popular.

Prefer one focused skill over a broad pack. Recommend multiple skills only
when their distinct necessary benefits justify each addition; assess and
authorize every one. Do not generate executable chains or a composition graph.
If all candidates are LOW, choose `NO_INSTALL` and continue with available
tools. An adequate installed equivalent yields `REUSE_EXISTING`.

Keep fit separate from risk: a HIGH-fit candidate can still be blocked by
[security-policy.md](security-policy.md). Complete that review before presenting
an installation proposal; an unreviewed candidate is only a lead pending review.
