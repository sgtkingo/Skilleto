# Skilleto

> **The right skills, right when you need them.**

**Skilleto** is an autonomous capability orchestrator for AI agents. It helps an agent recognize when a task would benefit from an additional skill, find relevant skills, evaluate their suitability and trustworthiness, and make them available in a controlled way.

Skilleto is not intended to be another skill marketplace. Its purpose is to connect existing skill ecosystems with agents' real work: **the agent should discover and acquire capabilities when they are needed—not require the user to search for and install them manually.**

- **Project:** Skilleto
- **Planned website:** [skille.to](https://skille.to) (domain reported as available; not assumed registered or live)
- **Initial ecosystem:** [skills.sh](https://skills.sh), especially the [find-skills](https://www.skills.sh/vercel-labs/skills/find-skills) workflow
- **Target hosts:** coding and general-purpose AI agents capable of using Agent Skills, initially Codex and Claude Code
- **Development tracks:** skill-only proof of concept (**PoC**) and local MCP-based minimum viable product (**MVP**)

## 1. The problem

AI agents can perform many tasks using their built-in reasoning and tools, but they cannot always know or access the most effective domain-specific workflows. Agent Skills can supply reusable instructions and resources, yet today the user often needs to:

1. Recognize that a suitable skill exists.
2. Search the ecosystem and compare candidates.
3. Inspect the skill's source and risks.
4. Install and activate it in the correct environment.
5. Return to the original task.

This manual cycle interrupts the workflow, favors skills that users already know, and may lead to unnecessary or unsafe installations.

## 2. The idea

Skilleto shifts capability management from the user to the agent. It operates as a **metaskill / capability-management layer** that evaluates the task and the environment before deciding whether external skills are useful.

The central decision is not simply **“Which skill should I install?”** but **“Does this task require an additional skill at all?”**

A valid, preferred outcome is **NO_INSTALL** when built-in capabilities, existing tools, or already installed skills are sufficient.

### Conceptual workflow

```text
User request / agent plan / code analysis
                  |
                  v
       Skilleto activation
        (explicit or implicit)
                  |
                  v
       Task decomposition
                  |
                  v
     Existing capability check
             /          \
       sufficient      gap found
           |               |
           v               v
       NO_INSTALL     Skill discovery
           |               |
           |               v
           |        Semantic matching
           |               |
           |               v
           |        Trust & security
           |               |
           |               v
           |       Controlled provisioning
           |               |
           |               v
           |       Availability validation
           \               /
             v           v
           Continue original task
```

Skilleto may evaluate several sub-tasks independently, recommending a skill for one and **NO_INSTALL** for another. It should prefer the *smallest justified set* of additions, not install skills merely because they are available.

## 3. How users interact with it

Skilleto is designed to be **low-friction and agent-driven**.

- **Explicit activation:** the user says **“Use Skilleto”** or **“Použij Skilleto.”** Skilleto then determines autonomously whether anything needs to be installed; the user does not have to prescribe the discovery algorithm.
- **Implicit activation:** the host agent invokes Skilleto when task planning, repository inspection, or execution reveals a potential capability gap.
- **Ordinary workflow:** the user simply assigns a task. Where the host supports skill discovery and activation, Skilleto can participate without being mentioned.

Automatic activation is dependent on the host's skill-selection behavior and configuration; it cannot be guaranteed by SKILL.md metadata alone. **Discovering a skill is not permission to install or execute it.** Provisioning follows the host's permissions and Skilleto's security policy.

### Example

A user asks an agent to analyze an unfamiliar repository, update its API, and create an automated test suite. The agent checks its existing capabilities, identifies any workflow-specific gaps, searches a supported registry if necessary, assesses relevant candidates, and requests approval for any operation that requires it. If no addition offers meaningful value, it continues without installing anything.

The user delegates the **task**, not the process of browsing a skill catalog.

## 4. Core capabilities

### Capability awareness and task decomposition

Break complex requests into meaningful work units. Compare each unit with the host's built-in capabilities, tools, and installed skills before attempting discovery.

### Semantic matching

Assess candidates by meaning, intended use, prerequisites, compatibility, and expected contribution to the task—not by name or keyword similarity alone. Initial implementations may rely on the host LLM for semantic reasoning.

### Trust & security

Treat skills and registry content as **untrusted external input**. Check provenance, inspect instructions and executable content, identify risky behaviors and dependencies, and apply least-privilege principles. Registry ranking or popularity is not a substitute for trust verification.

### Autonomous provisioning

Where needed and authorized, install a selected skill in a host-compatible location, check that it becomes discoverable, and recover cleanly if installation fails. Automation must not bypass host permission prompts, approval requirements, or security boundaries.

### Minimalism and NO_INSTALL

Avoid redundant, overlapping, incompatible, or low-value skills. Declining installation is a first-class decision, not a failure.

## 5. Architecture and delivery tracks

Skilleto has **one product vision** and two deliberately separate implementation tracks.

| | **PoC — skill-only** | **MVP — local MCP + bootstrap skill** |
|---|---|---|
| Goal | Validate agent-driven skill orchestration | Deliver a reusable, more reliable capability-management service |
| Runtime | Host agent executes instructions from `SKILL.md` | Local MCP server implements orchestration operations |
| Entry point | `skilleto` skill | `skilleto` bootstrap skill and MCP tools |
| Discovery | Agent-guided `find-skills` workflow on skills.sh | Server-integrated discovery, initially skills.sh |
| Semantic matching | Host LLM reasoning | Explicit resolver workflow, potentially using host reasoning |
| Security | Prompt-level checks and host approvals | Policy enforcement and programmatic checks where feasible |
| Provisioning | Host-mediated commands, with approvals | Controlled local provisioning adapters |
| Infrastructure | No separate server, service, or API | MCP server launched locally, potentially via `npx` |
| Primary output | Feasibility findings and observed failure modes | Usable product for supported agent hosts |

### PoC: prove the mechanism

The **PoC** consists of a standalone Skilleto Agent Skill (`SKILL.md` and optional supporting references). Its instructions guide the host agent through task decomposition, capability assessment, skills.sh / `find-skills` discovery, semantic selection, risk review, and authorized provisioning.

The PoC intentionally does **not** require an MCP server, resident background process, paid API, or proprietary model. This makes it inexpensive to deploy and useful for testing the central hypothesis before implementing a backend.

Because instruction-based controls are not a security sandbox, its claims about security and reliability must remain limited. It should demonstrate the workflow, document what works across hosts, and expose what requires stronger implementation.

**PoC success means:** the host can invoke Skilleto explicitly (and, where supported, implicitly), recognize unnecessary installations, identify appropriate skills when needed, and use approved capabilities without losing sight of the original task.

### MVP: make orchestration robust

The **MVP** adds a **local MCP server** responsible for more repeatable discovery, evaluation, policy checks, provisioning, and validation. A lightweight **bootstrap skill** serves as the agent-facing entry point and can help initialize or register the MCP server with the host, subject to user approval.

The intended onboarding uses a versioned `npx`-launched local MCP package. The host manages the server lifecycle; a permanently running daemon is not a requirement. Host configuration and possible session restart are implementation-specific.

For the initial MVP, **skills.sh remains the only skill registry**. Its `find-skills` workflow is the reference discovery mechanism. Additional registries are deliberately outside the first MVP.

### Long-term direction

Skilleto can evolve toward a registry-agnostic capability layer with richer policy enforcement, host adapters, and reusable capability intelligence:

- **Feedback Loop:** assess whether acquired skills actually helped and use measured outcomes to improve future recommendations (post-MVP).
- **Skill Composition:** coordinate complementary skills across multi-step workflows, manage compatibility, and minimize redundancy (future research/development).
- **Federated Discovery:** support multiple public, private, and organizational registries after the initial single-registry implementation.

These capabilities are **roadmap items, not claims about the PoC or initial MVP**.

## 6. Design principles

1. **Agent-first, user-light.** Users describe objectives; agents manage optional skills.
2. **No installation by default.** A capability gap and a meaningful expected benefit must justify each addition.
3. **Trust before execution.** External instructions and code require scrutiny and applicable approval.
4. **Host-agnostic by design.** Keep behavior portable across hosts, with small adapters where necessary.
5. **Use existing ecosystems.** Build orchestration rather than duplicate skill catalogs.
6. **Progressive autonomy.** Automate safe evaluation; respect approvals and host security boundaries for changes.
7. **Transparent decisions.** Explain why a skill was selected, rejected, or deemed unnecessary.
8. **Return to the task.** Discovery is a supporting step, not the user's ultimate goal.

## 7. Intended value

**For users:** less manual skill research and configuration; fewer interruptions while solving complex tasks.

**For developers:** reusable capability-management behavior across projects and agents; less repeated tooling setup.

**For organizations:** a path toward governed, auditable acquisition of external agent capabilities rather than ad hoc installations.

**For research:** a practical platform for studying whether dynamic capability acquisition improves agent task completion, efficiency, and reliability compared with fixed configurations. Such improvements are hypotheses to evaluate, not assumed results.

## 8. Boundaries and non-goals

Skilleto is **not** an LLM, a general app store, a replacement for the host agent, or a guarantee that third-party skills are safe. It does not require every task to use an external skill. It does not grant itself elevated privileges or bypass required user approvals.

The first versions are not intended to create new skills automatically, train models, run an independent agent runtime, or support every possible registry and host.

## 9. Project documentation

- **`PROJECT.md` (this document):** product vision, purpose, boundaries, PoC/MVP distinction, and roadmap.
- **PoC `PLAN.md`:** functional scope, skill behavior, validation scenarios, and acceptance criteria.
- **PoC `DEPLOY.md`:** installing and activating the standalone skill in supported hosts.
- **MVP `PLAN.md`:** architecture and implementation specification of the MCP-based product.
- **MVP `DEPLOY.md`:** bootstrap, local MCP registration, installation, validation, and recovery.

Implementation details may evolve independently, but both tracks should remain consistent with the product principles in this document.

---

**Skilleto helps AI agents acquire only the capabilities they genuinely need—at the moment they need them, with deliberate attention to relevance, trust, and control.**
