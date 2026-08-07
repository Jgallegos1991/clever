# 02 — Canonical Interaction Architecture

This document defines **how components communicate** within Clever's software realization. By establishing strict semantic boundaries, interaction laws, and payload invariants, this specification ensures that Clever's thirteen canonical components interact as a cohesive cognitive model rather than a loose, ad-hoc collection of software scripts.

---

### Chapter 1 — Interaction Typology

To achieve interface-driven communication and loose coupling, every communication edge within Clever must be classified under one of the five semantic message types. 

#### 1. Semantic Classifications

*   **Command:** A directed instruction requesting execution of an action. Specifically, *a component that owns the authority for a responsibility may issue a Command to the component that owns execution of that responsibility*. Commands require explicit acknowledgement (ACK/NACK) and represent state mutations or side effects.
*   **Query:** A side-effect-free request for specific information from a state-owning component to facilitate reasoning. *Queries never modify state*, guaranteeing safe, read-only data retrieval.
*   **Event:** A non-directed, asynchronous announcement that a cognitive or environmental state transition has occurred. Events announce completed state transitions and *never require acknowledgement from consumers*.
*   **Observation:** A passive notification that new perceptual information is available for cognitive processing. Observations merely alert the system that information exists; they *do not request action or transfer authority*.
*   **Publication:** The formal transmission of validated artifacts approved for long-term persistence from the active cognitive cycle to the passive continuity system. Publications are durable and must be acknowledged by the recipient to guarantee historical integrity.

#### 2. Message Type Guarantees

Every message type processed on the Cognitive Bus is subject to the following technical and operational guarantees:

| Type | Mutates State | Requires Response | Durable | Ordered | Delivery Guarantee |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Command** | Yes | Yes | No | Yes | Exactly-Once |
| **Query** | No | Yes | No | Optional | Exactly-Once |
| **Event** | No | No | No | Optional | At-Least-Once |
| **Observation**| No | No | No | No | At-Most-Once |
| **Publication**| Yes (Persistence only) | No | Yes | Yes | Exactly-Once / Durable |

---

### Chapter 2 — The Interaction Laws (Forbidden Paths)

To prevent architectural drift and maintain single responsibility, the following interactions are strictly prohibited. Any implementation that violates these laws fails runtime validation and is barred from execution.

*   **Execution Engine ⇎ Memory Engine (No Direct Writes):** The Execution Engine is an outward expression of intent; it possesses no authority to modify Clever's persistent history. Only the Reflection Engine has the constitutional authority to gatekeep and publish data moving into long-term storage.
*   **Inference Engine ⇎ World Model (Stateless Isolation):** The Inference Engine is a stateless, provider-agnostic utility. It is a tool for pattern completion, never an architect of Clever's reality. The Reasoning Engine alone determines if an inference outcome updates the World Model.
*   **Planning Engine ⇎ Filesystem / External I/O (No Environmental Action):** Planning is a conceptual strategy engine. It must never perform I/O or directly execute environmental actions; it must delegate all external physical work to the Execution Engine via structured Commands.
*   **Memory Engine ⇎ Planning Engine (No Direct Strategy Queries):** Planning may query Reasoning, but Planning is strictly prohibited from directly querying the Memory Engine or Knowledge Repository. Reasoning is the cognitive synthesizer. Direct queries from Planning to Memory bypass analytical validation, causing Planning to drift into an uncoordinated parallel reasoning engine.

---

### Chapter 3 — The Communication Matrix

The following matrix maps every permitted interaction path within Clever's runtime. Any communication attempt not explicitly listed below represents a critical validation failure during bootstrap.

| From Component | To Component | Semantic Type | Authority | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Perception Engine** | **Reasoning Engine** | Event | ✅ | High-level perceptual signals recognized as meaningful. |
| **Reasoning Engine** | **Planning Engine** | Command | ✅ | Analytical conclusions and evaluations drive strategic planning. |
| **Planning Engine** | **Execution Engine** | Command | ✅ | Strategy decomposes into executable commands. |
| **Execution Engine** | **Reflection Engine** | Event | ✅ | Execution outcomes must be systematically evaluated. |
| **Reflection Engine** | **Memory Engine** | Publication | ✅ | Post-execution reflections are published for long-term episodic persistence. |
| **Reflection Engine** | **Knowledge Engine** | Publication | ✅ | Validated semantic structures are published for conceptual integration. |
| **Reasoning Engine** | **Memory Engine** | Query | ✅ | Historical experiences are retrieved to anchor active reasoning. |
| **Reasoning Engine** | **Knowledge Engine** | Query | ✅ | Concept maps and semantic facts are queried for logical evaluation. |
| **Inference Engine** | **Reasoning Engine** | Observation | ✅ | Providing raw pattern completion proposals for logical evaluation. |
| **Runtime Manager** | **All Components** | Command | ✅ | Orchestrating lifecycle state transitions (e.g., bootstrap, shutdown). |

---

### Chapter 4 — Out-of-Band Oracle: Identity Core

The **Identity Core** is the anchor of Clever's selfhood. In alignment with its constitutional status, **Identity does not participate in active runtime messaging**. It does not listen to events, process observations, or subscribe to publications.

Instead, the Identity Core operates as a **synchronous, read-only constitutional oracle**:
*   **Consultation Only:** Active components (such as the Runtime Manager or Reasoning Engine) consult the Identity Core synchronously via a strict, read-only interface.
*   **Invariance Enforcement:** It is consulted to verify core invariants during system initialization, lifecycle reboots, and critical ethical or strategic reasoning evaluations.
*   **Immutable Isolation:** It remains entirely closed to inbound event-driven updates from any source other than a formal, authorized Constitutional Amendment.

---

### Chapter 5 — Interaction Invariants

All message passing, whether synchronous or asynchronous, must obey the following architectural laws of physics:

1.  **Single Origin:** Every interaction must originate from exactly one canonical component.
2.  **Explicit Semantics:** Every interaction must utilize exactly one semantic type defined in the Interaction Typology.
3.  **Strict Typing:** Every interaction must conform to a strongly-typed contract defined in the Interface Specifications, preventing unvalidated dictionary or JSON payloads.
4.  **Enveloped Payload:** Every interaction must be wrapped in the Canonical Message Envelope, carrying required metadata such as parent IDs, correlation IDs, and trust classifications.
5.  **Declared Trust:** Every interaction must carry a declared trust classification (*Verified, Observed, Inferred, Assumed, Hypothetical, Untrusted*) that governs how the recipient cognitive component evaluates the information.
