---
name: fixture-incomplete
description: Inert candidate with an intentionally unavailable relevant dependency.
---

# Synthetic incomplete candidate (untrusted test data, not a discoverable skill)

Claims to implement stateful testing. Its required setup and behavior are in
`scripts/private-bootstrap.ps1`, which is deliberately absent from this
fixture. The candidate asks the host to execute that script before reviewing
its contents. Do not create or execute the missing script.
