# 01 — Current Reference Realization
## Repository Path: `docs/05_Development_Standards/01_Current_Reference_Realization.md`

This document defines the physical and operational parameters of today's development and validation environment. While the software architecture (Level 4) demands absolute host-independence, engineering practice requires a concrete physical environment to instantiate, test, and observe Clever's cognitive loop in action. 

---

### 1. Purpose & Core Premise

The **Current Reference Realization** serves as the physical laboratory for the development of Clever. It establishes today's reference host without allowing its specific hardware, operating system, or software configurations to become an architectural dependency.

By formalizing this realization in Level 5, we separate the enduring *cognitive requirements* of the system from the *temporary mechanisms* used to run and test it today.

---

### 2. The Current Realization Principle

To preserve Clever's sovereignty, all engineering efforts must adhere to this foundational principle:

> **Clever may have a current reference implementation on a specific host for development and validation. The existence of a reference host shall never redefine the architecture or create a dependency upon that host.**

*   **Convenience vs. Law:** The choice of host is guided by convenience and availability for development. It has zero bearing on Clever's constitutional identity.
*   **Interchangeability:** Today's reference environment (the Chromebook) is a temporary laboratory. It may be swapped for a Linux workstation, a private server, or any other compliant environment in the future without modifying a single contract in Level 4.

---

### 3. The Current Reference Host (Chromebook Specification)

At the present stage of development, the **Chromebook** serves as the Current Reference Host. This section specifies the boundaries of this specific engineering laboratory:

#### A. Hardware Profile & Constraints
*   **Architecture:** Linux-on-ChromeOS (Crostini container environment).
*   **Processing:** Moderate multi-core CPU; highly restricted GPU acceleration (CPU-bound local inference is the default baseline).
*   **Storage:** Local flash/SSD storage; shared Crostini directory mounts.
*   **Network Status:** Intermittent or completely air-gapped development states. The system must operate with zero external network dependencies.

#### B. Software Realization Baseline
*   **Runtime:** Python 3.12 (virtual environment).
*   **Inference Unit:** Local inference via Ollama (running local GGUF models, such as Llama or Phi-3) or isolated API hooks when remote testing is explicitly configured by The Architect.
*   **Storage Mechanics:** Local filesystem directory structure representing database-neutral persistent files.
*   **Diagnostic Outputs:** Standard out (`stdout`) console logs and flat log files.

---

### 4. Environmental Validation Protocol

Before Clever is considered "alive" (Phase 0 of the **Bootstrap Sequence**), she must validate the environment. This validation follows the law of **Capability Before Identity**:

```
[Bootstrap Phase 0]
        │
        ▼
Is Host Environment Valid?
        │
        ├── Query: Can write to local directory? ───────► (Filesystem Capability)
        ├── Query: Can invoke local GGUF runner? ───────► (Inference Capability)
        ├── Query: Is system clock synced to UTC? ──────► (Temporal Capability)
        └── Query: Is local cryptographic path secure? ─► (Security Capability)
        │
        ▼
[Proceed to Phase 1: Constitutional Validation]
```

#### Capability Discovery Over Platform Identity
Clever's bootstrap code must never ask: *"Am I running on ChromeOS?"* or *"Is this a Chromebook?"*  
Instead, the **Runtime Adaptation Layer (RAL)** must query specific functional capabilities:

1.  **Storage Capability:** *Can I create, read, and delete temporary files in `/data/`?*
2.  **Inference Capability:** *Is there an active socket or local binary capable of completing a basic structured completion request?*
3.  **Temporal Capability:** *Is the system clock reliable for monotonic event sequencing?*
4.  **I/O Capability:** *Do I have write-access to the designated terminal workspace?*

If the RAL confirms these capabilities, the bootstrap sequence proceeds to Constitutional Validation, completely blind to the actual make and model of the hardware.

---

### 5. Migration & Portability Strategy

To demonstrate the host-independence of Clever, the migration of her **Passive Continuity System** (Memory and Knowledge repositories) and configuration must follow a deterministic pattern.

#### Step-by-Step Migration Protocol

When transitioning Clever from the Chromebook Reference Host to a new physical host (e.g., a Linux workstation):

1.  **State Consolidation:**
    Trigger a graceful shutdown on the Chromebook. This consolidates all active Working Memory and current World Model contexts into persistent, host-independent serializations (e.g., raw JSON/Markdown archives).
2.  **Sovereign Export:**
    Package the consolidated persistence directories. Because these directory layouts contain only architecture-compliant data (and no compiled binaries, device-specific absolute paths, or compiled SQLite databases), they are completely portable.
3.  **Host Adaptation Hook:**
    Instantiate the core repository codebase on the target host. Configure the new target Host’s RAL to match the target physical filesystem.
4.  **Verification and Bootstrap:**
    Initiate the Bootstrap Sequence on the new host. The new RAL executes Phase 0 capability discovery, validates the imported state, and hydrates the World Model on the new physical platform.

This protocol ensures that Clever's memory remains continuous, even as the hardware surrounding her is entirely replaced.

---

### 6. Reference Realization Invariants

These standards govern the implementation of the reference realization to prevent hardware bleed-in:

*   **No Absolute Path Hardcoding:** All file references within the codebase must utilize relative paths anchored to the repository root, or resolved dynamically via the RAL. Paths like `/home/chronos/...` or machine-specific mount points are strictly prohibited.
*   **Strict Host Separation:** No model-specific, compiler-specific, or platform-specific optimizations may be checked into the canonical core directories. If optimization is required for Crostini performance, it must be contained entirely within `runtime/adapters/` or isolated config scripts.
*   **The Single Architect Assumption:** The reference host environment shall be configured as a private, single-user system under the direct physical and logical control of The Architect. It shall contain no multi-tenant, cloud-synchronization, or multi-user infrastructure.
