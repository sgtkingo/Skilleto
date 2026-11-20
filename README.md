<div align="center">

# Skilleto

### The right skills, right when you need them.

**An autonomous skill orchestrator for AI agents.**

Skilleto helps agents recognize when they need new capabilities, discover relevant skills, assess their safety, and acquire them when justified — without turning every task into a manual search-and-install workflow.

[Vision](#the-idea) · [How it works](#how-it-works) · [Roadmap](#roadmap)

</div>

---

## The idea

AI agents can reason, write code, and use tools. But specialized tasks often benefit from reusable **Agent Skills** — and finding, evaluating, and installing those skills is still largely a manual process.

**Skilleto moves skill management into the agent's workflow.** Instead of asking users to browse catalogs, an agent can recognize a capability gap while planning, inspecting code, or executing a task, then use Skilleto to find a suitable solution.

The most important question is not *“Which skill should I install?”* but **“Do I need another skill at all?”**

If the agent already has everything it needs, **NO_INSTALL** is the right answer.

## How it works

**Understand the task** → **Check existing capabilities** → **Discover candidates** → **Match semantically** → **Assess trust & security** → **Provision safely** → **Continue the task**

Skilleto is designed around four principles:

- **Agent-first:** Activate explicitly ("Use Skilleto") or automatically when the host agent detects a capability gap, where supported.
- **Minimal by design:** Prefer existing capabilities and install only what adds meaningful value.
- **Security-aware:** Inspect provenance, content, permissions, and risks before any installation. Approval remains subject to the host's security policy.
- **Ecosystem-friendly:** Build on existing skill registries rather than creating another marketplace.

## Roadmap

| Stage | Goal | Approach |
| --- | --- | --- |
| **PoC** | Validate autonomous skill discovery and decision-making | A standalone **metaskill** powered by the host agent; no MCP server |
| **MVP** | Make orchestration more reliable and portable | A **local MCP server** with a lightweight bootstrap skill, semantic matching, security checks, and controlled provisioning |
| **Future** | Learn and compose capabilities | Feedback-driven evaluation, skill composition, and multiple registries |

The initial discovery ecosystem is [skills.sh](https://skills.sh), leveraging its [find-skills](https://www.skills.sh/vercel-labs/skills/find-skills) workflow. Initial target agents include **Codex** and **Claude Code**.

## What Skilleto is not

Skilleto is **not** a new skill marketplace, a replacement for existing agents, or a mechanism for silently executing untrusted code. It is a **capability-management layer** that helps an agent use the right tools at the right time — and know when not to add more.

---

<div align="center">

**Less skill hunting. More doing.**

*Skilleto is an early-stage project.*

[Project vision](PROJECT.md) · [skille.to](https://skille.to) *(planned website)*

</div>
