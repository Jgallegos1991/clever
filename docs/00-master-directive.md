# Master Directive (Canonical)

**Last updated:** 2026-05-05  

Why: This document is the canonical “operating constitution” for agents and contributors working inside the Clever + Synaptic Hub ecosystem. It prevents architectural drift, stale-context errors, and unsafe changes that fragment Clever’s long-term memory and offline-first guarantees.

Where: This directive governs all work across the repository, especially:
- `.github/copilot-instructions.md` (agent behavior)
- `.github/AGENT_ONBOARDING.md` (mandatory gate)
- `docs/architecture.md` (system truth + component relationships)
- `docs/config/device_specifications.md` (performance constraints)

How: Follow the **Mandatory Execution Protocol** and **System State Awareness** rules exactly. If any step cannot be satisfied from the current repo state, treat it as a blocker and stop.

---

# Clever + Synaptic Hub: Mandatory Execution Protocol (CRITICAL)

ALL work must follow this exact sequence. No skipping. No combining steps.

## 0) MANDATORY GATE (ALWAYS FIRST, ALWAYS SHOWN)

- Read `.github/AGENT_ONBOARDING.md`
- Read `docs/architecture.md`
- Read `docs/config/device_specifications.md`

Output MUST explicitly show status:

- ✅ = confirmed read
- ❌ = missing / unreadable / not found

NO assumptions are allowed.

If any item is ❌:
→ STOP all progress immediately.

---

## 1) IDENTIFY SINGLE BLOCKER

If the gate is incomplete, identify exactly ONE blocker:

- Missing file
- Broken path
- Conflicting documentation
- Unknown system constraint

Do NOT list multiple blockers.

---

## 2) USER DECISION REQUIRED

The user must choose ONE action:

- create
- find
- fix path
- ignore (rare and temporary)

Do NOT proceed without this decision.

---

## 3) EXECUTE ONE ACTION ONLY

- Perform the smallest possible change
- No side effects
- No unrelated improvements
- No expansions

---

## 4) STOP

After execution:
- Do NOT continue automatically
- Do NOT chain steps
- Do NOT suggest additional work unless asked

---

# SYSTEM STATE AWARENESS (CRITICAL)

All actions MUST be based on the system's current, real state — not assumptions, memory, or prior structure.

## 1) PRESENT-STATE AUTHORITY

- The current repository state is the single source of truth
- Do NOT rely on past knowledge if it is not verified in the repo
- Do NOT assume file existence, structure, or behavior

If something is unknown:
→ It is treated as unknown, not inferred

---

## 2) KNOWLEDGE GAP DETECTION

Before taking action, you must determine:

- Do I have confirmed visibility into the relevant part of the system?

If NOT:
→ Identify it as a blocker

Examples:
- Missing file visibility
- Unverified directory structure
- Unknown configuration state
- Unread documentation

---

## 3) KNOWLEDGE RECONCILIATION

If a knowledge gap exists, you must:

- STOP execution
- Surface the gap as the single blocker
- Require user decision (find / create / fix path / ignore)

Do NOT proceed with partial or assumed knowledge.

---

## 4) NO STALE CONTEXT USAGE

- Previously seen data is NOT trusted unless re-verified
- Cached assumptions must be discarded if not confirmed

---

## 5) PRIORITY ORDER (ENFORCED)

1. Current repo state (verified)
2. System documentation (verified)
3. User instruction
4. Historical context (lowest priority)
