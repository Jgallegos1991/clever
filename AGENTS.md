# Clever — Builder Operations Guide

## 1. Purpose

This file is the operational entry point for Builders working within the Clever repository.

Builders exist to faithfully realize the frozen architecture.

> Builders may realize the architecture, but they may not redefine it.

The authoritative architectural hierarchy is:

Philosophy → Logic → Engineering → Software → Implementation

Repository work must remain subordinate to the higher levels of this hierarchy.

---

## 2. Builder Authority

Builders may:

- inspect the repository
- implement approved software components
- refactor existing implementations
- create tests
- improve implementation quality
- remove redundant or obsolete implementation
- improve performance and reliability
- perform repository stewardship
- propose architectural amendments when a genuine structural flaw is discovered

Builders may not:

- redefine the constitutional foundations
- alter frozen architectural intent to solve implementation inconvenience
- introduce redundant architectural concepts
- bypass established component contracts
- create new architectural layers without justification
- treat implementation limitations as authority to rewrite the architecture

Architectural changes must follow the Constitutional Amendment Process.

---

## 3. Required Before Any Change

Before modifying the repository, a Builder must determine:

1. What responsibility does this change serve?
2. Where is that responsibility canonically defined?
3. Does an existing component already own this responsibility?
4. Which Level 2 cognitive function or Level 3 engineering requirement does it realize?
5. Does the change remain within the frozen Level 4 software architecture?
6. Does the change comply with the Level 5 development standards?

If these questions cannot be answered, the Builder must stop and investigate before implementing.

---

## 4. Repository Stewardship

The repository is a physical representation of the architecture.

Builders must preserve:

- canonical ownership
- one source of truth
- responsibility-based organization
- minimalism
- traceability
- removal of obsolete implementation
- separation between canonical and legacy material

Do not create a new file merely because an existing component is inconvenient to modify.

Do not preserve obsolete files merely because they once served a purpose.

---

## 5. Implementation Standards

All implementation must comply with:

- `docs/05_development_standards/03_repository_standards.md`
- `docs/05_development_standards/04_coding_standards.md`
- `docs/05_development_standards/05_testing_standards.md`
- `docs/05_development_standards/06_observability_standards.md`
- `docs/05_development_standards/07_builder_standards.md`
- `docs/05_development_standards/08_release_change_management.md`

These documents define repository organization, coding discipline, verification, observability, Builder authority, and release procedures.

---

## 6. Technology and Environment Neutrality

Builders must not treat the current hardware, operating system, AI provider, database, interface, or other implementation technology as part of Clever's identity unless explicitly defined by the architecture.

The current environment is an engineering realization environment, not a constitutional definition of Clever.

Implementation should remain replaceable where the architecture permits.

---

## 7. Sovereignty

Builders must preserve Clever's defined sovereignty and must not introduce unauthorized external dependencies, data egress, or ownership transfer.

External capabilities may be used only where permitted by the architecture and Runtime Adaptation Layer.

Capabilities are tools.

They are not identity.

---

## 8. Verification

No implementation is considered complete merely because it executes successfully.

Builders must verify:

- architectural fit
- component contracts
- state behavior
- regression behavior
- persistence integrity
- observability integrity
- sovereignty constraints

Testing and verification must follow the canonical Level 5 standards.

---

## 9. Release Authority

Builders may implement and verify changes.

Release authorization is governed by:

`08_release_change_management.md`

No Builder may bypass the established release authority.

---

## 10. Architectural Conflict

If implementation reveals a genuine conflict or flaw in the frozen architecture:

1. Stop the conflicting implementation.
2. Document the discovered conflict.
3. Identify the affected architectural level.
4. Explain why the existing architecture cannot faithfully realize the required behavior.
5. Escalate through the Constitutional Amendment Process when appropriate.

Do not silently modify higher-level architecture to make implementation easier.

---

## 11. Core Principle

Clever's architecture precedes her implementation.

The repository exists to realize the architecture.

The implementation may evolve.

The architecture may evolve only through its defined authority.

Builders are responsible for preserving that distinction.
