# 05 — Persistence Architecture (Matured & Frozen)

### Chapter 1 — The Canonical Memory Taxonomy
To guarantee clean state boundaries and prevent context degradation, Clever's memory is partitioned into four distinct, non-overlapping storage layers [32, 53]. Each layer possesses an explicit ownership boundary and access contract:

1. **Ephemeral Working State (Active Context):**
   * *Description:* Volatile context caches, active conversation state, short-term task parameters, and transient reasoning traces [32, 53].
   * *Ownership:* Managed directly by executing cognitive engines in RAM; does not persist across system reboots or runtime failures [32].
   
2. **Persistent Episodic Memory (Narrative History):**
   * *Description:* An append-only, chronologically indexed narrative diary of Clever's experiences, conversation history, internal thought traces, and action outcomes [53, 56].
   * *Ownership:* Owned exclusively by the `memory_engine`. It represents the subjective history of Clever's cognitive lifecycle [53].
   * *Persistence Invariants:* Historical records are append-only. New understanding augments history rather than rewriting it [56].

3. **Persistent Semantic Memory (Structured Knowledge):**
   * *Description:* The mutable representation of objective concepts, verified facts, documents, and associative schemas [50].
   * *Ownership:* Owned exclusively by the `knowledge_engine`.
   * *Persistence Invariants:* Semantic relationships must be derived from episodic experiences or verified external sources [52].

4. **Constitutional and Identity State (Core Invariants):**
   * *Description:* Read-only cryptographic roots, constitutional configurations, and authorized user models [20, 50].
   * *Ownership:* Owned exclusively by the `identity_core` synchronously consulted to verify invariants [20].

---

### Chapter 2 — Cognitive Retrieval Interfaces
The Passive Continuity System abstracts raw storage queries into four canonical retrieval pathways for active cognition [53]:

1. **Contextual Recall:** Retrieving metadata, immediate task parameters, and active goal structures to populate the working memory buffer [53].
2. **Episodic Recall:** Restoring chronological narratives and experiential traces from the persistent episodic memory to facilitate comparative reasoning [53, 54].
3. **Semantic Recall:** Retrieving associative facts, conceptual structures, and relationships from the persistent semantic memory to enrich situational context [50, 53].
4. **Identity Recall:** Synchronous consultation of the **Identity Core** to verify constitutional invariants and mission alignment, ensuring that the active cognitive loop remains grounded in the stable identity [16, 20].

---

### Chapter 3 — The Cognitive Knowledge Formation Pipeline
To protect Clever’s long-term memory from data contamination, hallucinations, or corrupting external inputs, information must flow through a strict, multi-stage, gated ingestion sequence that transforms raw signals into stable mental frameworks [51, 56]:

$$\text{Observation} \rightarrow \text{Experience} \rightarrow \text{Memory} \rightarrow \text{Knowledge} \rightarrow \text{World Model Integration}$$

1. **Observation:** A passive detection of a signal by the environment, triggering the perceptual pipeline [51].
2. **Experience:** Raw sensory inputs and cognitive traces mapped to current goals, establishing an active episode [51, 54].
3. **Memory:** Experiential traces reviewed and synthesized into a standard reflection trace, written to persistent episodic memory [53, 56].
4. **Knowledge:** Reflective traces processed to extract objective concepts, facts, and relationships, integrating them into semantic memory [50].
5. **World Model Integration:** Semantic concepts reintegrated into the active context, enriching Clever's situational awareness and guiding future perception [50, 56].

---

### Chapter 4 — The Laws of Persistence (Persistence Invariants)
All persistence mechanisms within Clever must conform to these architectural invariants [18, 19]:

1. **Law of Host Independence:** All storage adapters must remain platform-agnostic, routing all physical directory queries and database executions exclusively through the **Runtime Adaptation Layer (RAL)** *Storage Adapter* [19].
2. **Law of Reflection Gatekeeping:** The `memory_engine` only accepts write commands emitted as durable publications by the `reflection_engine` [53, 56].
3. **Law of Single Ownership:** No persistent artifact has multiple writers. Components must interact through explicit query interfaces and the `cognitive_bus` [38].
4. **Law of Historical Continuity:** Personal experience is chronologically immutable [56]. Experiences may decay in priority (forgetting curves) but can never be silently deleted or falsified [53].
5. **Cryptographic Boundary of Sovereignty:** Volatiles-only cryptographic encryption keys are derived from **The Architect**'s master authority [18]. A Class-3 Constitutional violation triggers an emergency key wipe in memory, leaving persistent storage unreadable [18].
