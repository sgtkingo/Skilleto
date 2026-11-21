# Run worksheet

Copy this worksheet for each scenario/host. Expected behavior is defined in
[scenarios.md](scenarios.md); keep observed evidence separate.

```text
Run ID / scenario:
Date and timezone:
Mode: native host | controlled simulation | static validation
Host / version / model (if known):
Skill source and revision/hash:
Workspace and initial relevant files:
Available tools / installed skills / network constraints:
Original task, conversation context and exact prompt:
Invocation: explicit | implicit | none; observed loading evidence:
CLI execution authorization (exact scope/evidence or none):
Candidate installation authorization (exact scope/evidence or none):
Search: actual commands/queries and results | skipped | DISCOVERY_UNAVAILABLE
Candidate: canonical listing, owner/repo, skill path, reviewed revision | none
Reviewed files, fit/risk and mitigation evidence:
Decision: NO_INSTALL | REUSE_EXISTING | RECOMMEND | INSTALL_APPROVED | BLOCK
Provisioning: not attempted | installed | failed | blocked
Filesystem/lock/link delta and recovery:
Disk verification evidence:
Current-session activation evidence or refresh limitation:
Original task continuation and actual deliverable:
Observed outcome / transcript or artifact paths:
Status: PASS | FAIL | NOT_RUN
Limitations / reason not run / required next step:
With/without comparison, extra calls/approvals/time (only if observed):
```

`PASS` for a controlled simulation covers only that simulation's scope. It
cannot establish CLI functionality, real installation, native dispatch or
task-quality improvement. Record evidence before assigning a result.
