# Device Specifications (Canonical)

**Last updated:** 2026-05-04  

Why: Clever is offline-first and performance-sensitive; this document defines the **real hardware + OS constraints** that shape safe architectural decisions (NLP load, UI effects, caching, sync behavior).

Where: Referenced by:
- `.github/AGENT_ONBOARDING.md` (MANDATORY GATE)
- `docs/architecture.md` (System constraints layer)
- Performance tuning for `static/js/engines/*` and local NLP startup behavior

How: Keep this document factual and measurable. Update it whenever the primary device, storage headroom, or OS/runtime changes.

---

## 1) Primary Device (Current)

> This is the **authoritative** environment Clever must run on.

- **Device class:** Chromebook (ChromeOS) with Linux (Crostini) enabled
- **Operating system:** ChromeOS + Debian-based Linux container
- **Runtime target:** Local-only (no required internet)

### CPU
- **CPU model:** Intel Jasper Lake (Chromebook-class, low-power)
- **Expected characteristics:** Limited sustained multi-core throughput; avoid heavy parallelism and long-running high-CPU loops.

### Memory (RAM)
- **Constraint:** Limited RAM typical of Chromebook devices.
- **Design implication:** Prefer streaming + incremental processing; avoid loading large corpora/models unless explicitly needed.

### Storage
- **Storage type:** eMMC
- **Constraint:** Low free space can occur.
- **Design implication:**
  - Avoid uncontrolled cache growth
  - Ensure DB + ingestion artifacts have clear retention policies
  - Prefer append-only logs with rotation

### Display
- **Typical resolution:** 1366×768 (baseline for UI scaling)

---

## 2) Secondary / Optional Device Profiles

If Clever is run on other hardware (e.g., Linux workstation), document it here.

- **Status:** Not canonical unless explicitly promoted to "Primary Device".

---

## 3) Performance Budgets (Guiding Limits)

These are *guiding* budgets to prevent regressions.

- **UI frame-rate target:** 45–60 FPS (adaptive quality permitted)
- **Startup time target:** Fast enough for interactive use; defer expensive NLP model loads when possible
- **Ingestion:** Prefer bounded, resumable operations (never unbounded scans)

---

## 4) Offline-First / Network Rules (Device-Level)

- **Default:** Offline-only operation.
- **Never required:** External API calls at runtime.
- **Sync systems (Drive/IPFS):** Must be explicitly enabled and must be loop-safe (no blind overwrite, no duplication).

---

## 5) Observability Requirements (Device Constraints)

Because Chromebook environments can mask failures (sleep, container restarts):

- Logs must be **local**, **rotated**, and **human-readable**
- Any background watcher must:
  - handle restarts
  - back off on errors
  - never spin at 100% CPU

---

## 6) TODO (Fill with measured values)

When available, replace estimates with measured values:

- `lscpu` output summary
- `free -h` (RAM)
- `df -h` (disk)
- Linux container version

