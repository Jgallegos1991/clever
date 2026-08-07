# 03 — Interface Specifications
## Canonical Level 4 Specification

### Chapter 1 — Contract Governance and Invariants
This chapter establishes the absolute physical and legal rules governing Clever's internal data structures, ensuring that loose coupling and technology neutrality are strictly maintained across all boundaries.

*   **Strict Contract Ownership:** Every message payload schema has exactly one designated owner component (e.g., `perception_engine` owns the `PerceptionPayload`). This owner is solely responsible for outbound validation and schema versioning.
*   **Contract Identity Definition:** *Contract identity is defined by its semantic meaning rather than its serialization format.* A contract like `ExecutionRequest` exists as an enduring cognitive definition. It is not defined by `execution_request.json`, `ExecutionRequest.cs`, or `ExecutionRequest.py`—those are merely secondary realizations. The contract itself exists above the implementation layer.
*   **Contract Compatibility Invariant:** A new contract version shall remain backward compatible unless explicitly declared as a constitutional breaking change through the formal Constitutional Amendment Process.
*   **Technology Neutrality:** All contracts are specified using language-agnostic primitives:
    *   `String`: UTF-8 textual data.
    *   `Float`: 64-bit IEEE floating-point values.
    *   `Integer`: 64-bit signed integers.
    *   `Boolean`: True/False flags.
    *   `Map`: Key-value associations where keys are Strings.
    *   `Enum`: Defined sets of unique symbolic names.
*   **Transit-Time Validation:** The **Cognitive Bus** intercepts, inspects, and validates the schema of every message during transit, treating violations as critical system-level faults.

---

### Chapter 2 — Canonical DTO Specifications
*These nine canonical contracts represent the minimum stable vocabulary required to realize the Level 2 Cognitive Cycle and Level 3 subsystem boundaries. Additional contracts may only be introduced through the Constitutional Amendment Process.*

#### 1. Perception Payload
*   **URN:** `urn:clever:contract:cognition:perception-payload:v1`
*   **Owner:** `perception_engine`
*   **Fields:**
    *   `source_id` (String): ID of origin sensor or input.
    *   `raw_content` (String): Unfiltered input text.
    *   `detected_features` (Map of String to String): Recognized patterns or tokens.
    *   `timestamp` (Float): Unix epoch time.
*   **Invariants:** `source_id` must not be empty. `timestamp` must be a positive value.

#### 2. Reasoning Context
*   **URN:** `urn:clever:contract:cognition:reasoning-context:v1`
*   **Owner:** `reasoning_engine`
*   **Fields:**
    *   `active_goal_id` (String): Current operational goal.
    *   `salient_facts` (List of Map): Synthesized observations and verified beliefs.
    *   `uncertainties` (List of String): Explicitly identified gaps in knowledge.
    *   `logical_step_traces` (List of String): Step-by-step deductive or inductive reasoning chain.
*   **Invariants:** `logical_step_traces` must contain at least one step.

#### 3. Goal Stack Update
*   **URN:** `urn:clever:contract:cognition:goal-stack-update:v1`
*   **Owner:** `world_model`
*   **Fields:**
    *   `goals` (List of Map): List of active goals containing `goal_id` (String), `priority` (Integer, 1-100), `parent_id` (String), and `status` (Enum: [Active, Suspended, Completed, Aborted]).
*   **Invariants:** Priority must be strictly between 1 and 100 inclusive.

#### 4. Action Plan
*   **URN:** `urn:clever:contract:cognition:action-plan:v1`
*   **Owner:** `planning_engine`
*   **Fields:**
    *   `plan_id` (String): Globally unique ID for the sequence.
    *   `associated_goal_id` (String): Goal being served.
    *   `steps` (List of Map): Sequential actions containing `step_id` (String), `adapter_target` (String), `action_payload` (Map), and `rollback_payload` (Map).
*   **Invariants:** `steps` must be ordered sequentially. Every step must define an `adapter_target` mapping to a valid RAL capability.

#### 5. Execution Request
*   **URN:** `urn:clever:contract:cognition:execution-request:v1`
*   **Owner:** `execution_engine`
*   **Fields:**
    *   `execution_id` (String): Unique transaction ID.
    *   `step_id` (String): ID of the plan step.
    *   `adapter_target` (String): Target capability adapter.
    *   `parameters` (Map): Run-time parameters.
    *   `timeout` (Integer): Timeout in milliseconds.
*   **Invariants:** `timeout` must be positive and not exceed system configuration bounds.

#### 6. Execution Outcome
*   **URN:** `urn:clever:contract:cognition:execution-outcome:v1`
*   **Owner:** `execution_engine`
*   **Fields:**
    *   `execution_id` (String): Matches request.
    *   `status` (Enum: [Success, Failed, Timeout, Interrupted]).
    *   `observed_result` (String): Realized environment output.
    *   `error_code` (String, Optional): Standardized error label if failed.
    *   `system_metrics` (Map): Resources consumed during execution.
*   **Invariants:** If `status` is `Failed`, `error_code` must not be null.

#### 7. Reflection Trace
*   **URN:** `urn:clever:contract:cognition:reflection-trace:v1`
*   **Owner:** `reflection_engine`
*   **Fields:**
    *   `trace_id` (String): Unique ID of the cognitive cycle trace.
    *   `expected_outcome` (String): Predicted state of the world before action.
    *   `observed_outcome` (String): Actual state of the world after action.
    *   `discrepancy_score` (Float): Quantified difference between expected and observed state (0.0 to 1.0).
    *   `consolidated_learning` (String): Extracted principles to be published to long-term memory.
*   **Invariants:** `discrepancy_score` must lie in the range [0.0, 1.0].

#### 8. Memory Query & Response
*   **URN:** `urn:clever:contract:persistence:memory-query:v1`
*   **Owner:** `memory_engine`
*   **Fields:**
    *   `query_id` (String): Core query identifier.
    *   `query_type` (Enum: [Episodic, Semantic, Archival]).
    *   `filter_criteria` (Map): Key-value filters.
    *   `results` (List of Map): Array of matched historical memory payloads.
*   **Invariants:** `results` must be read-only and preserve temporal ordering.

#### 9. Knowledge Ingestion Contract
*   **URN:** `urn:clever:contract:persistence:knowledge-ingestion:v1`
*   **Owner:** `knowledge_engine`
*   **Fields:**
    *   `document_id` (String): Unique document fingerprint.
    *   `source_uri` (String): Origin path or web URL.
    *   `semantic_embeddings` (List of Float): Agnostic vector array.
    *   `metadata` (Map): Author, dates, verified citations.
*   **Invariants:** Ingested documents must carry a valid cryptographic SHA-256 fingerprint as `document_id`.

---

### Chapter 3 — Reasoning Interpretation of Trust Classifications
This section details how the **Reasoning Engine** dynamically interprets the six trust-level classifications to protect Clever from unverified data or circular logic.

**Trust-to-Value Decoupling Rule:** *Trust classifications describe confidence in information, not its importance.* A low-trust, raw `Observed` signal may carry monumental structural importance to Clever's safety, while a highly `Verified` static fact may be trivial. Value and trust operate on orthogonal axes.

The Six Trust Levels:
1.  `Verified`: Deduced from constitutional axioms or directly authenticated by The Architect. Zero logical validation required.
2.  `Observed`: Collected from physical or local environmental sensors through the RAL. Strictly grounded in physical evidence, superseding all `Assumed` states.
3.  `Inferred`: Deduced or induced from prior observations. Reasoning must constantly audit these traces to prevent circular logic.
4.  `Assumed`: Fallback defaults used when direct observations are temporarily missing. Safely replaced the moment `Observed` information arrives.
5.  `Hypothetical`: Simulated or speculative data used in sandboxed planning spaces. Strictly prohibited from mutating long-term storage or leaving sandbox execution boundaries.
6.  `Untrusted`: Unverified external inputs. Quarantined for deep analysis and prevented from crossing into cognitive evaluation loops without sanitization.
