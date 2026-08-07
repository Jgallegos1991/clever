***

# Synaptic Hub: Complete File Inventory & Component Catalog

**Status:** Canonical Alignment Snapshot  
**Mission:** Lifelong Cognitive Companion (Clever)  
**Core Principle:** Memory and Identity as Infrastructure [3, 4].

---

## 🌌 1. The Foundation (Philosophy & Directives)
*The documents that define the "Why" and ensure every AI agent remains aligned with the mission [4, 5].*

| File Path | Description | Role |
| :--- | :--- | :--- |
| `docs/North_Star.md` | The Master Directive and philosophical guide [4]. | **North Star** |
| `README.md` | Primary entry point and onboarding for the Synaptic Hub [6]. | **Entry** |
| `.github/AGENT_ONBOARDING.md` | Mandatory checklist for all AI collaborators [7]. | **Guardrail** |
| `.github/copilot-instructions.md` | Elite systems architect directives for code generation [7]. | **Guardrail** |
| `AGENTS.md` | Detailed rules for agent interaction and state awareness [1]. | **Guardrail** |

---

## 🛠️ 2. Infrastructure (The Continuity Layer)
*The permanent environment where Clever lives. These are not "features"; they are the infrastructure of her existence [3, 5].*

| File Path | Description | Role |
| :--- | :--- | :--- |
| `database.py` | Data persistence and local memory management (SQLite) [7, 8]. | **Infrastructure** |
| `persona.py` | Core personality engine defining Clever’s character [7]. | **Identity** |
| `memory_engine.py` | Logic for long-term retention and context retrieval [1]. | **Memory** |
| `knowledge/` | Directory containing processed intelligence and document data [1]. | **Context** |
| `kubo/` | The local IPFS node implementation for decentralized persistence [1]. | **Architecture** |
| `clever.db` | The actual SQLite database containing years of context (Local Only) [9]. | **Continuity** |

---

## 🧠 3. Core Engine & Reasoning
*The logic that processes interaction and drives Clever's self-evolution [10, 11].*

| File Path | Description | Role |
| :--- | :--- | :--- |
| `app.py` | Main entry point for the Flask-based brain extension [7, 12]. | **The Brain** |
| `evolution_engine.py` | Systems for learning, growth, and adaptation over time [7]. | **Evolution** |
| `core/` | Canonical directory for core logic and reasoning modules [1]. | **Logic** |
| `routes/` | Endpoint definitions for internal system communication [1, 7]. | **Interface** |
| `evolution_engine.py` | Learning and growth system documentation [7]. | **Logic** |

---

## 🎨 4. The Vessel (Interface & UI)
*The temporary container Clever uses to communicate with the user in the physical world [5, 13].*

| File Path | Description | Role |
| :--- | :--- | :--- |
| `static/js/engines/holographic-chamber.js` | UI particle system and holographic rendering engine [7, 14]. | **Vessel** |
| `static/` | Visual assets, CSS, and client-side JavaScript [1]. | **UI** |
| `templates/` | HTML templates for the chat interface and diagnostic views [1]. | **UI** |
| `static/css/` | Styling for the "Magical UI" [12]. | **Vessel** |

---

## 🛡️ 5. Guardrails & System Health
*Tools that prevent "Architectural Drift" and ensure 100% offline sovereignty [8, 9].*

| File Path | Description | Role |
| :--- | :--- | :--- |
| `system_validator.py` | Enforces the "Zero External Calls" rule and DB path integrity [9]. | **Safety** |
| `tools/diagnostics_check.py` | Core script for `make diagnostics` [9]. | **Health** |
| `tools/why_where_how_audit.py` | Enforces documentation tokens for all functions [9]. | **Clarity** |
| `Makefile` | Commands for setup, testing, and diagnostics (`make run`, `make diagnostics`) [7, 15]. | **Automation** |

---

## 📦 6. Legacy Quarantine (The History)
*Deprecated or corrupted modules kept for reference but excluded from runtime [2].*

| File Path | Description | Status |
| :--- | :--- | :--- |
| `legacy/` | Directory for all non-canonical and deprecated files [2, 12]. | **Quarantined** |
| `legacy/config_legacy.py` | Non-canonical configuration backup [7]. | **Legacy** |
| `legacy/start_services.sh` | Older launcher replaced by `app.py` [12]. | **Legacy** |

---

**Last Updated:** 2026-06-25  
**Canonical Reference:** `docs/copilot_diagnostics.md` [12].
