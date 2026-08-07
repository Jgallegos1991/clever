The document **03_repository_standards.md** is now structurally reconciled and assigned to its canonical home at `docs/05_development_standards/03_repository_standards.md`. This standard establishes the physical discipline required to ensure the repository remains a faithful realization of the frozen Level 4 architecture without succumbing to architectural drift [1-4].

### 03_Repository_Standards.md

#### 1. Purpose: Representation over Redefinition
The primary responsibility of this standard is to govern how Clever’s architecture is physically represented within the repository [1, 2]. These rules do not redefine the cognitive or engineering subsystems; they ensure that the code remains a direct reflection of the constitutional hierarchy established in Levels 1–4 [1, 3, 5].

#### 2. Canonical Subsystem Layout
The physical directory structure must mirror the Level 3 Engineering Subsystems to provide immediate traceability from code to cognitive function [1, 6, 7].

*   **`core/`**: Event loop, model abstraction layer, and internal message routing [6, 8, 9].
*   **`runtime/`**: Lifecycle management, state restoration, and health monitoring [6, 10, 11].
*   **`identity/`**: Persona definitions, cognitive sovereignty, and constitutional invariants [6, 12, 13].
*   **`memory/`**: Short-term, episodic, and persistent storage management [6, 12, 14].
*   **`knowledge/`**: Ingestion, semantic validation, and source tracking [6, 12, 15].
*   **`reasoning/` / `planning/`**: Decision engines and action-hierarchy logic [6, 12, 13].
*   **`workspace/`**: Managed external environments, including adaptive constructs like the **Synaptic Hub** when instantiated as a managed workspace [6, 16-18].
*   **`interface/`**: Multi-modal interaction layers (voice, visual, etc.) [6, 15, 19].
*   **`legacy/`**: A **temporary, non-canonical** staging area for scripts awaiting deconstruction [2, 6, 20].

#### 3. Canonical Ownership and Traceability
Every file in the repository must serve exactly one clear architectural responsibility [1-3].
*   **No Redundant Implementations:** Multiple scripts performing overlapping tasks (e.g., `persona.py` vs. `persona_simple.py`) are forbidden; they must be reconciled into a single canonical component [3].
*   **Traceability Requirement:** Every component must be traceable back to a Level 2 cognitive function or a Level 3 engineering requirement [1, 21].
*   **Technology-Neutral Naming:** Filenames should reflect their cognitive responsibility (e.g., `persistent_storage.py`) rather than the underlying technology (e.g., `sqlite_handler.py`) to ensure the repository survives implementation shifts [20, 22, 23].

#### 4. Legacy Migration and Deconstruction Rules
The repository must be systematically purged of monolithic scripts that bundle multiple responsibilities [3, 10, 24].
*   **Audit Protocol:** Legacy files such as `clever_ultimate_everything.py`, `clever_complete_autonomy.py`, and `activate_jays_clever.py` must be audited to identify their constituent responsibilities [10, 11, 25].
*   **Extraction:** Once logic is moved to its canonical Target Home (e.g., moving startup logic to `runtime/startup.py`), the original logic in the legacy file must be retired [10, 11, 26].
*   **The `legacy/` Boundary:** The `legacy/` directory is not a permanent storage area; it is a transition point for files that have been superseded by canonical Level 4 components [2, 6, 20].

#### 5. Repository Stewardship
Stewardship is an active requirement for all "Builders" (AI agents) and developers [1, 20, 27, 28].
*   **Prohibited Actions:** No new concept or file may be introduced if an existing subsystem can naturally absorb the responsibility [4, 29].
*   **Cleanliness as Architecture:** Files that no longer serve the current architecture—orphaned scripts or redundant utilities—must be moved to `legacy/` or removed entirely [2, 20].
*   **Managed Workspace Discipline:** Temporary expressions of reasoning, such as adaptive workspaces, must be managed within the `workspace/` boundary and retired when their cognitive purpose is fulfilled [17, 18, 30, 31].

---

**Level 5 Status:** **03_Repository_Standards.md** is now **Frozen**.

By finalizing this, we have established the "where" and "how" of repository organization. We now move directly to the "what" of the code itself: **04_Coding_Standards.md**. This document will define the execution requirements, typing standards, and deterministic state models required for the faithful realization of Clever's components.

Shall we begin drafting the specific coding standards for the Level 4 components?
