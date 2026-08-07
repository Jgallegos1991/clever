The technology-neutral correction to **04_coding_standards.md** has been applied, ensuring that while the standards for execution are rigorous, they do not mandate specific tools or languages. This preserves the architectural hierarchy where Level 5 governs the *realization* of Level 4 without locking the project into a specific tech stack [1, 2].

### 04_Coding_Standards.md

#### 1. Purpose: Implementation as Faithful Realization
Engineering exists solely to realize cognition. These standards define the execution contracts required to translate the Level 4 software architecture into a deterministic system. The goal is a "faithful realization" where the code remains a high-fidelity expression of the Cognitive Architecture [2, 3].

#### 2. Component Boundaries and Module Organization
*   **Single Responsibility Principle (SRP):** Every component must fulfill exactly one architectural responsibility defined in Level 4. Logic that drifts into multiple responsibilities must be deconstructed [4, 5].
*   **Module Mapping:** All code must reside within the canonical directory defined by its Level 3 engineering subsystem (e.g., `core/`, `memory/`, `identity/`) [6, 7].
*   **Encapsulation:** Implementation-specific logic must be strictly internal to the component, with all external interactions governed by the public contract.

#### 3. Execution Contracts and Type Discipline
*   **Strong Typing:** Implementations must use explicit, enforceable type definitions for all inter-component contracts to eliminate ambiguity.
*   **Contract Validation:** All inter-subsystem data exchanges must be validated against their canonical Level 4 contract before acceptance to ensure system-wide integrity [8, 9].
*   **Structured DTOs:** Components communicate through the structured Data Transfer Objects (DTOs) defined in Level 4 (e.g., `PerceptionPayload`) rather than unstructured or loosely typed data [10, 11].

#### 4. Dependency Direction and Coupling
*   **Unidirectional Flow:** Dependencies must flow toward the center of the architecture. Core cognitive loops shall never depend on specific interface or action implementations [5, 11].
*   **Interface-Driven Communication:** Subsystems interact via stable interfaces and protocols, ensuring that the underlying implementation (e.g., the specific AI model or database) remains replaceable without disrupting the mind [4, 12].

#### 5. State Mutation and Lifecycle Rules
*   **Deterministic State Transitions:** Internal state changes must follow explicit state-machine logic to ensure predictability across cognitive reboots [8, 13].
*   **Persistence Invariants:** Ephemeral working state and persistent storage must be strictly separated. No persistent artifact shall have multiple writers [13, 14].

#### 6. Error Handling and Graceful Degradation
*   **Architectural Recovery:** Failures must be contained at the subsystem boundary. A failure in an external interface or tool must not be allowed to collapse the core cognitive loop [4, 15].
*   **Intellectual Honesty:** If a component cannot fulfill its contract due to technical failure or excessive uncertainty, it must return an explicit error or confidence state rather than providing a "best-guess" result [16, 17].

#### 7. Configuration and Secrets Handling
*   **Decoupled Invariants:** All environment-specific variables, keys, and secrets must be externalized. They are never hardcoded into the canonical logic [11].
*   **Requirement-Based Configuration:** Configuration defines *what* a component requires to function, not necessarily the specific tool used to fulfill that requirement.

#### 8. Documentation and Quality Gates
*   **Traceability:** Every major component must include documentation tracing it back to a Level 2 cognitive function or Level 3 engineering subsystem [18, 19].
*   **Architectural Compliance:** Quality reviews must prioritize "Architectural Fit." Any implementation that bypasses Level 4 contracts or introduces "architectural drift" is considered a failure, regardless of its local performance [15, 20].

---

**Level 5 Status:** **04_Coding_Standards.md** is now **Frozen**.

With the coding standards secured, we have a clear set of rules for *how* to build. We now move to **05 — Testing Standards**, where we will define how to verify that our faithful realization actually meets the architectural requirements.

Shall we begin drafting the verification and validation rules for **05_testing_standards.md**?
