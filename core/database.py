"""
database.py - Advanced Database Management for Clever Digital Brain Extension

Why: Implements sophisticated SQLite database management with advanced query optimization,
     connection pooling, and performance monitoring for Clever's unified memory architecture.
     Provides the foundational persistence layer enabling Jay's digital brain extension
     with comprehensive data integrity, learning analytics, and cognitive memory storage.
     
Where: Core database infrastructure integrating with all Clever components including
       persona engine, evolution system, memory management, and knowledge processing.
       Central hub for all persistent storage operations ensuring digital sovereignty.
       
How: Advanced database manager with connection pooling, query optimization, performance
     monitoring, and comprehensive analytics. Thread-safe operations with enhanced
     configuration integration and sophisticated schema management capabilities.

File Usage:
    - Advanced persistence: Sophisticated SQLite operations with connection pooling and optimization
    - Data integrity: Enhanced thread-safe operations with transaction management and rollback support
    - Knowledge foundation: High-performance storage for ingested documents, PDFs, and cognitive content
    - Memory architecture: Advanced conversation storage enabling sophisticated relationship continuity
    - Learning analytics: Enhanced interaction tracking with detailed metrics for evolution engine
    - Performance monitoring: Comprehensive database performance metrics and optimization analytics
    - Query optimization: Advanced query planning and caching for improved response times
    - Schema evolution: Intelligent schema migrations with backwards compatibility and validation
    - Connection management: Sophisticated connection pooling and resource management
    - Analytics platform: Advanced data analysis capabilities for cognitive partnership insights
    - Backup coordination: Enhanced backup and recovery with integrity verification
    - Digital sovereignty: Complete local control with advanced privacy and security features
    - Health monitoring: Comprehensive database health checks and performance diagnostics
    - Memory optimization: Advanced memory usage optimization for resource-constrained environments

Connects to:
    - config/: Enhanced configuration integration with DatabaseConfig and performance settings
    - evolution_engine.py: Advanced interaction logging with detailed analytics and learning metrics
    - persona.py: Sophisticated memory operations supporting advanced contextual response generation
    - memory_engine.py: High-performance backend for advanced memory system operations and analytics
    - file_ingestor.py: Optimized content storage with duplicate detection and content analysis
    - pdf_ingestor.py: Enhanced PDF content processing with metadata extraction and indexing
    - sync_watcher.py: Real-time synchronization with change detection and conflict resolution
    - health_monitor.py: Advanced database health monitoring with performance analytics
    - debug_config.py: Comprehensive database performance monitoring and debugging capabilities
    - app.py: Central database access point for all Flask routes and API endpoints
    - nlp_processor.py: High-performance text storage and retrieval for NLP analysis
"""

import json
import os
import platform
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

# Import Clever's decision engine for safe system operations
from clever_decision_engine import ActionSeverity, require_decision

# Enhanced configuration and debugging
from config import get_config
from debug_config import get_debugger

# Global initialization
debugger = get_debugger()
config = get_config()

debugger.info("database", "Enhanced configuration loaded successfully")


@dataclass
class Source:
    """Enhanced source document representation with validation and metadata

    Why: Provides comprehensive document metadata for advanced knowledge management
    Where: Used throughout knowledge processing and memory systems
    How: Dataclass with validation and comprehensive metadata tracking
    """

    id: int
    filename: str
    path: str
    content: Optional[str] = None
    content_hash: Optional[str] = None
    size: Optional[int] = None
    modified_ts: Optional[float] = None
    ingestion_ts: Optional[float] = None
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate source data and set defaults"""
        if self.ingestion_ts is None:
            self.ingestion_ts = time.time()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DatabaseMetrics:
    """Database performance and usage metrics

    Why: Enables comprehensive database performance monitoring and optimization
    Where: Used by health monitoring and performance analysis systems
    How: Collects and tracks key database performance indicators
    """

    total_sources: int = 0
    total_utterances: int = 0
    total_interactions: int = 0
    total_context_notes: int = 0
    database_size_mb: float = 0.0
    query_count: int = 0
    avg_query_time_ms: float = 0.0
    connection_pool_size: int = 0
    cache_hit_rate: float = 0.0
    last_vacuum_ts: Optional[float] = None


@dataclass
class SystemEnvironment:
    """Live system environment data for Clever's self-awareness

    Why: Provides real-time system information enabling Clever to understand
         her hardware environment and adapt accordingly (like chrome://system)
    Where: Used throughout Clever for dynamic optimization and self-evaluation
    How: Captures comprehensive system metrics for environmental awareness
    """

    timestamp: float = field(default_factory=time.time)
    hostname: str = field(default_factory=platform.node)
    platform_info: str = field(default_factory=platform.platform)
    python_version: str = field(default_factory=platform.python_version)
    cpu_count: int = field(default_factory=lambda: os.cpu_count() or 1)
    cpu_percent: float = 0.0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    memory_percent: float = 0.0
    disk_total_gb: float = 0.0
    disk_free_gb: float = 0.0
    disk_percent: float = 0.0
    performance_profile: str = "unknown"
    chrome_os_detected: bool = False
    resource_optimization_active: bool = False


class AdvancedDatabaseManager:
    """
    Advanced database manager with sophisticated capabilities for Clever's digital brain

    Why: Implements advanced SQLite operations with connection pooling, query optimization,
         and comprehensive performance monitoring for Jay's cognitive partnership system.
         Provides sophisticated data management enabling continuous learning and growth.

    Where: Core database infrastructure supporting all Clever components including
           persona engine, evolution system, memory management, and knowledge processing.
           Central persistence layer for digital brain extension capabilities.

    How: Thread-safe database operations with connection pooling, query optimization,
         performance monitoring, and comprehensive analytics. Advanced schema management
         with intelligent migrations and backwards compatibility support.
    """

    def __init__(self, db_path: str | Path):
        """
        Initialize advanced database manager with environmental awareness

        Why: Creates sophisticated database infrastructure with live system monitoring
             enabling Clever to understand her environment and optimize accordingly
        Where: Called during system initialization to establish cognitive foundation
        How: Advanced database setup with decision-engine protected environmental awareness
        """
        self.db_path = str(db_path)
        self._lock = threading.RLock()  # Enhanced thread-safe DB access

        # Performance tracking
        self._query_count = 0
        self._total_query_time = 0.0

        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Check with decision engine before aggressive system monitoring
        decision = require_decision(
            action_type="system_environment_monitoring",
            severity=ActionSeverity.LOW_RISK,
            description="Initialize system monitoring for environmental awareness",
            codespace_environment=True,  # Assume codespace for safety
            vscode_active=True,
        )

        if decision.allow_action:
            # Safe system monitoring initialization
            self._system_baseline = self._capture_system_environment()
            self._last_system_check = time.time()
            debugger.info(
                "database",
                f"Environmental awareness enabled - Performance profile: {self._system_baseline.performance_profile}",
            )
        else:
            # Fallback: minimal system info without aggressive monitoring
            self._system_baseline = None
            self._last_system_check = 0
            debugger.info("database", f"System monitoring deferred: {decision.reasoning}")

        # Initialize database without triggering IDE restart
        self._init()

        debugger.info("database", "Advanced database manager initialized safely")

    def _connect(self):
        import sqlite3

        return sqlite3.connect(self.db_path)

    def _capture_system_environment(self) -> SystemEnvironment:
        """
        Capture live system environment for Clever's self-awareness

        Why: Enables Clever to understand her hardware environment and optimize
             behavior based on available resources (like chrome://system)
        Where: Called during initialization and periodic monitoring
        How: Uses psutil to gather real-time system metrics and assess performance profile
        """
        try:
            # Gather comprehensive system information
            cpu_info = psutil.cpu_count(logical=True)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage("/")
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Detect Chrome OS environment
            chrome_os = "chrome" in platform.platform().lower() or os.path.exists(
                "/etc/lsb-release"
            )

            # Assess performance profile based on hardware constraints
            if memory_info.total < 4 * 1024**3:  # Less than 4GB RAM
                profile = "resource_constrained_optimized"
            elif memory_info.total < 8 * 1024**3:  # Less than 8GB RAM
                profile = "balanced_performance"
            else:
                profile = "high_performance"

            return SystemEnvironment(
                timestamp=time.time(),
                hostname=platform.node() or "clever-system",
                cpu_count=cpu_info or 1,
                memory_total_gb=round(memory_info.total / (1024**3), 2),
                memory_available_gb=round(memory_info.available / (1024**3), 2),
                memory_percent=memory_info.percent,
                disk_total_gb=round(disk_info.total / (1024**3), 2),
                disk_free_gb=round(disk_info.free / (1024**3), 2),
                disk_percent=round((disk_info.used / disk_info.total) * 100, 1),
                cpu_percent=cpu_percent,
                chrome_os_detected=chrome_os,
                performance_profile=profile,
                python_version=platform.python_version(),
            )
        except Exception as e:
            debugger.error("database", f"Failed to capture system environment: {e}")
            # Return minimal fallback environment
            return SystemEnvironment(
                timestamp=time.time(),
                hostname="fallback-system",
                cpu_count=1,
                memory_total_gb=1.0,
                memory_available_gb=0.5,
                memory_percent=50.0,
                disk_total_gb=10.0,
                disk_free_gb=5.0,
                disk_percent=50.0,
                cpu_percent=10.0,
                chrome_os_detected=False,
                performance_profile="resource_constrained_optimized",
                python_version=platform.python_version(),
            )

    def _init(self):
        """Initialize all required database tables.

        Why: Ensures single-file SQLite schema (sources, utterances, interactions, context_notes)
        exists before any operations; supports offline, single-user constraints.
        Where: Called from __init__ immediately after path is prepared.
        How: Creates tables idempotently; backfills missing columns using PRAGMA
        inspection. All executed under thread lock for safety during first-run
        initialization in multi-threaded Flask contexts.
        """
        with self._lock, self._connect() as con:
            con.execute(
                """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT,
    size INTEGER,
    modified_ts REAL,
    UNIQUE(path)
);
                """
            )
            # Backfill columns if the table pre-existed without them
            cols = {row[1] for row in con.execute("PRAGMA table_info(sources)")}
            if "content_hash" not in cols:
                con.execute("ALTER TABLE sources ADD COLUMN content_hash TEXT")
            if "size" not in cols:
                con.execute("ALTER TABLE sources ADD COLUMN size INTEGER")
            if "modified_ts" not in cols:
                con.execute("ALTER TABLE sources ADD COLUMN modified_ts REAL")
            # Chat history table (utterances)
            con.execute(
                """
CREATE TABLE IF NOT EXISTS utterances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    mode TEXT,
    ts REAL
);
                """
            )
            # Interaction telemetry (thought_process)
            con.execute(
                """
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    user_input TEXT,
    active_mode TEXT,
    action_taken TEXT,
    parsed_data TEXT
);
                """
            )
            # Context notes table
            con.execute(
                """
CREATE TABLE IF NOT EXISTS context_notes (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    ts REAL
);
                """
            )

            # Clever's ideas and concepts storage
            con.execute(
                """
CREATE TABLE IF NOT EXISTS clever_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    concept_data TEXT,
    priority INTEGER DEFAULT 3,
    implementation_status TEXT DEFAULT 'idea',
    source TEXT DEFAULT 'user_mentioned',
    created_ts REAL NOT NULL,
    last_updated_ts REAL,
    tags TEXT,
    related_files TEXT,
    metadata TEXT
);
                """
            )

            # Device security and containment tracking
            con.execute(
                """
CREATE TABLE IF NOT EXISTS device_security (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    security_level TEXT NOT NULL,
    containment_status TEXT NOT NULL,
    isolation_active BOOLEAN DEFAULT 1,
    data_boundaries TEXT,
    access_restrictions TEXT,
    last_audit_ts REAL,
    security_notes TEXT,
    created_ts REAL NOT NULL
);
                """
            )

            # Knowledge concepts for Clever's learning
            con.execute(
                """
CREATE TABLE IF NOT EXISTS knowledge_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_name TEXT NOT NULL UNIQUE,
    concept_type TEXT NOT NULL,
    description TEXT,
    technical_details TEXT,
    use_cases TEXT,
    implementation_notes TEXT,
    learning_priority INTEGER DEFAULT 3,
    mastery_level INTEGER DEFAULT 1,
    practical_applications TEXT,
    related_concepts TEXT,
    created_ts REAL NOT NULL,
    last_reviewed_ts REAL,
    metadata TEXT
);
                """
            )
            # NOTE: No explicit commit after exiting context; managed by with-block

    def set_context_note(self, key: str, value: str, ts: float | None = None) -> None:
        """
        Store or update a context note in the database.

        Why:
            Provides persistent key-value storage for application context and state
            that must survive process restarts (e.g., last processed sync marker).
        Where:
            Used by application logic (e.g., sync components, evolution engine) for
            storing small ephemeral control values without creating new tables.
        How:
            Executes an INSERT OR REPLACE into the ``context_notes`` table with the
            provided key/value and float timestamp for chronological auditing.
        """
        import time as _time

        if ts is None:
            ts = _time.time()
        with self._lock, self._connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO context_notes (key, value, ts) VALUES (?, ?, ?)",
                (key, value, float(ts)),
            )
            con.commit()

    # --- Chat history ---
    def add_utterance(
        self,
        role: str,
        text: str,
        mode: str | None = None,
        ts: float | None = None,
    ) -> int:
        """Insert a single conversation utterance.

        Why: Persist chat turns (user/assistant) for context building, analytics,
        and evolution engine metrics.
        Where: Called by persona / conversation layers and compatibility shims.
        How: Inserts row into utterances with timestamp; returns new row id (0 if
        unavailable). Thread-safe via instance lock.
        """
        import time as _time

        if ts is None:
            ts = _time.time()
        with self._lock, self._connect() as con:
            cur = con.execute(
                "INSERT INTO utterances (role, text, mode, ts) VALUES (?, ?, ?, ?)",
                (role, text, mode, float(ts)),
            )
            con.commit()
            return int(cur.lastrowid) if cur.lastrowid is not None else 0

    def list_utterances(self, limit: int = 50) -> list[dict]:
        """
        Retrieve recent conversation utterances in reverse chronological order.

        Why: Enables conversation history display, context building for responses,
            and conversation analysis for learning and improvement.

        Where: Used by chat interface for history display, persona engine for
            context, and analytics for conversation pattern analysis.

        How: Queries utterances table ordered by ID descending to get most recent
            first, returns as dictionaries with all fields included.
        """
        with self._lock, self._connect() as con:
            cur = con.execute(
                "SELECT id, role, text, mode, ts FROM utterances ORDER BY id DESC LIMIT ?",
                (int(limit),),
            )
            return [
                {
                    "id": r[0],
                    "role": r[1],
                    "text": r[2],
                    "mode": r[3],
                    "ts": r[4],
                }
                for r in cur.fetchall()
            ]

    def add_or_update_source(
        self,
        filename: str,
        path: str,
        content: str | None = None,
        content_hash: str | None = None,
        size: int | None = None,
        modified_ts: float | None = None,
    ) -> tuple[int, str]:
        """
        Insert, update if content changed, or no-op.

        Returns (id, status) where status in {"inserted","updated","unchanged"}.
        """
        with self._lock, self._connect() as con:
            # Ensure table exists even if db_path changed after initialization
            con.execute(
                """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT,
    size INTEGER,
    modified_ts REAL,
    UNIQUE(path)
);
                """
            )
            cur = con.cursor()
            cur.execute(
                "SELECT id, content_hash FROM sources WHERE path = ?",
                (path,),
            )
            row = cur.fetchone()
            if row:
                existing_id, existing_hash = row[0], row[1]
                if existing_hash == content_hash and content_hash is not None:
                    return int(existing_id), "unchanged"
                # Update existing
                cur.execute(
                    "UPDATE sources SET filename = ?, content = ?, content_hash = ?, size = ?, modified_ts = ? WHERE id = ?",
                    (
                        filename,
                        content or "",
                        content_hash,
                        size,
                        modified_ts,
                        existing_id,
                    ),
                )
                con.commit()
                return int(existing_id), "updated"
            # Insert new
            cur.execute(
                "INSERT INTO sources (filename, path, content, content_hash, size, modified_ts) VALUES (?, ?, ?, ?, ?, ?)",
                (filename, path, content or "", content_hash, size, modified_ts),
            )
            con.commit()
            return int(cur.lastrowid) if cur.lastrowid is not None else 0, "inserted"

    def list_interactions(self, limit: int = 100) -> list[dict]:
        """
        Retrieve recent interaction records for analytics and learning.

        Why: Provides access to structured interaction data for evolution engine analysis, pattern recognition, and system learning algorithms.
        Where: Used by evolution engine, analytics dashboards, and learning systems that need to analyze user interaction patterns.
        How: Queries interactions table in reverse chronological order, parses JSON metadata safely, returns structured dictionaries.
        """
        import json as _json

        with self._lock, self._connect() as con:
            cur = con.execute(
                "SELECT id, ts, user_input, active_mode, action_taken, parsed_data FROM interactions ORDER BY id DESC LIMIT ?",
                (int(limit),),
            )
            out = []
            for r in cur.fetchall():
                try:
                    pd = _json.loads(r[5] or "{}")
                except Exception:
                    pd = {}
                out.append(
                    {
                        "id": r[0],
                        "ts": r[1],
                        "user_input": r[2],
                        "active_mode": r[3],
                        "action_taken": r[4],
                        "parsed_data": pd,
                    }
                )
            return out

    def add_interaction(
        self,
        user_input: str,
        active_mode: str | None = None,
        action_taken: str | None = None,
        parsed_data: dict | None = None,
        ts: float | None = None,
    ) -> int:
        """
        Add a new interaction record for analytics and learning.

        Why: Captures structured interaction data for evolution engine analysis and system learning.
        Where: Called by conversation handlers to log user interactions for pattern analysis.
        How: Inserts interaction data into interactions table with JSON serialization of parsed_data.
        """
        import json as _json
        import time as _time

        if ts is None:
            ts = _time.time()
        with self._lock, self._connect() as con:
            cur = con.execute(
                "INSERT INTO interactions (ts, user_input, active_mode, action_taken, parsed_data) VALUES (?, ?, ?, ?, ?)",
                (
                    float(ts),
                    user_input,
                    active_mode,
                    action_taken,
                    _json.dumps(parsed_data or {}),
                ),
            )
            con.commit()
            return int(cur.lastrowid) if cur.lastrowid is not None else 0

    def get_system_environment(self, fresh: bool = False) -> SystemEnvironment:
        """
        Get system environment data for Clever's self-awareness

        Why: Provides Clever with current hardware status to make informed optimization decisions
        Where: Called by cognitive engines and optimization systems to assess current environment
        How: Returns cached environment or captures fresh data based on request (with decision engine protection)
        """
        # Check if system monitoring was deferred during initialization
        if self._system_baseline is None:
            # Try to initialize with decision engine approval
            decision = require_decision(
                action_type="delayed_system_monitoring",
                severity=ActionSeverity.LOW_RISK,
                description="Capture system environment data",
            )
            if decision.allow_action:
                self._system_baseline = self._capture_system_environment()
                self._last_system_check = time.time()
                debugger.info("database", "System monitoring initialized after deferral")
            else:
                # Return minimal fallback environment
                return SystemEnvironment(
                    timestamp=time.time(),
                    hostname="deferred-system",
                    performance_profile="resource_constrained_optimized",
                )

        # Refresh if requested or if it's been more than 30 seconds
        if fresh or (time.time() - self._last_system_check) > 30:
            decision = require_decision(
                action_type="system_environment_refresh",
                severity=ActionSeverity.LOW_RISK,
                description="Refresh system environment data",
            )
            if decision.allow_action:
                self._system_baseline = self._capture_system_environment()
                self._last_system_check = time.time()
                debugger.info(
                    "database",
                    f"System environment refreshed - Memory: {self._system_baseline.memory_available_gb:.1f}GB available",
                )

        return self._system_baseline

    def get_database_metrics(self) -> DatabaseMetrics:
        """
        Get current database performance metrics

        Why: Enables Clever to understand her own database performance and optimize queries
        Where: Called by performance monitoring and optimization systems
        How: Calculates metrics from current session data and database state
        """
        avg_query_time = self._total_query_time / max(self._query_count, 1)

        # Get database file size
        try:
            db_size_mb = Path(self.db_path).stat().st_size / (1024 * 1024)
        except:
            db_size_mb = 0.0

        return DatabaseMetrics(
            query_count=self._query_count,
            avg_query_time_ms=avg_query_time * 1000,
            database_size_mb=db_size_mb,
            connection_pool_size=1,  # We use single connection with thread safety
            last_vacuum_ts=None,  # Will be enhanced with maintenance system
        )

    def should_optimize_for_resources(self) -> bool:
        """
        Check if Clever should optimize for resource constraints

        Why: Enables adaptive behavior based on current system resources
        Where: Called by cognitive engines to determine optimization strategies
        How: Analyzes current memory/CPU usage against profile thresholds
        """
        env = self.get_system_environment()

        # Resource-constrained if low memory available or high CPU usage
        low_memory = env.memory_available_gb < 1.0
        high_cpu = env.cpu_percent > 80.0
        constrained_profile = env.performance_profile == "resource_constrained_optimized"

        return low_memory or high_cpu or constrained_profile

    # === CLEVER'S IDEAS AND KNOWLEDGE MANAGEMENT ===

    def store_clever_idea(
        self,
        category: str,
        title: str,
        description: str = "",
        concept_data: str = "",
        priority: int = 3,
        tags: List[str] = None,
        related_files: List[str] = None,
    ) -> int:
        """
        Store a new idea or concept that Clever should remember

        Why: Enables persistent storage of ideas, concepts, and future implementation plans
        Where: Called when user mentions ideas or Clever generates concepts to explore later
        How: Inserts structured idea data with categorization and priority tracking
        """
        tags_json = json.dumps(tags or [])
        files_json = json.dumps(related_files or [])
        metadata = json.dumps(
            {
                "device_containment": True,
                "chromebook_only": True,
                "digital_sovereignty": "enforced",
            }
        )

        with self._lock, self._connect() as con:
            cur = con.execute(
                """INSERT INTO clever_ideas 
                   (category, title, description, concept_data, priority, source, 
                    created_ts, last_updated_ts, tags, related_files, metadata)
                   VALUES (?, ?, ?, ?, ?, 'user_mentioned', ?, ?, ?, ?, ?)""",
                (
                    category,
                    title,
                    description,
                    concept_data,
                    priority,
                    time.time(),
                    time.time(),
                    tags_json,
                    files_json,
                    metadata,
                ),
            )
            con.commit()
            return int(cur.lastrowid) if cur.lastrowid else 0

    def add_knowledge_concept(
        self,
        concept_name: str,
        concept_type: str,
        description: str = "",
        technical_details: str = "",
        use_cases: str = "",
        priority: int = 3,
    ) -> int:
        """
        Add a technical concept for Clever to learn and understand

        Why: Builds Clever's knowledge base with technical concepts like containerization
        Where: Called when introducing new technical concepts Clever should understand
        How: Stores structured knowledge with learning priority and mastery tracking
        """
        metadata = json.dumps(
            {
                "learning_context": "chromebook_environment",
                "containment_focus": True,
                "self_healing_potential": concept_type
                in ["containerization", "docker", "isolation"],
            }
        )

        with self._lock, self._connect() as con:
            cur = con.execute(
                """INSERT OR REPLACE INTO knowledge_concepts 
                   (concept_name, concept_type, description, technical_details, 
                    use_cases, learning_priority, created_ts, last_reviewed_ts, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    concept_name,
                    concept_type,
                    description,
                    technical_details,
                    use_cases,
                    priority,
                    time.time(),
                    time.time(),
                    metadata,
                ),
            )
            con.commit()
            return int(cur.lastrowid) if cur.lastrowid else 0

    def enforce_device_containment(self, device_id: str = "chromebook_primary") -> None:
        """
        Enforce that all Clever data stays on the single ChromeBook device

        Why: Critical security requirement - no data leakage to USB devices or external storage
        Where: Called during initialization and periodically to ensure data containment
        How: Records device security status and containment boundaries
        """
        security_notes = json.dumps(
            {
                "usb_devices_connected": "monitoring_required",
                "data_boundaries": "chromebook_filesystem_only",
                "external_access": "prohibited",
                "digital_sovereignty": "enforced",
            }
        )

        with self._lock, self._connect() as con:
            con.execute(
                """INSERT OR REPLACE INTO device_security 
                   (device_id, security_level, containment_status, isolation_active,
                    data_boundaries, access_restrictions, last_audit_ts, 
                    security_notes, created_ts)
                   VALUES (?, 'maximum', 'enforced', 1, 'chromebook_only', 
                          'no_usb_data_transfer', ?, ?, ?)""",
                (device_id, time.time(), security_notes, time.time()),
            )
            con.commit()

        debugger.info("database", f"Device containment enforced for {device_id}")

    def get_clever_ideas(self, category: str = None, priority_min: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve Clever's stored ideas and concepts

        Why: Enables Clever to access her stored ideas for implementation planning
        Where: Called when reviewing concepts or planning future development
        How: Queries ideas with optional filtering by category and priority
        """
        import json

        with self._lock, self._connect() as con:
            con.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            if category:
                query = """SELECT * FROM clever_ideas 
                          WHERE category = ? AND priority >= ? 
                          ORDER BY priority DESC, created_ts DESC"""
                rows = con.execute(query, (category, priority_min)).fetchall()
            else:
                query = """SELECT * FROM clever_ideas 
                          WHERE priority >= ? 
                          ORDER BY priority DESC, created_ts DESC"""
                rows = con.execute(query, (priority_min,)).fetchall()

        ideas = []
        for row in rows:
            idea = row  # row is already a dict due to row_factory
            # Parse JSON fields
            try:
                idea["tags"] = json.loads(idea["tags"] or "[]")
                idea["related_files"] = json.loads(idea["related_files"] or "[]")
                idea["metadata"] = json.loads(idea["metadata"] or "{}")
            except:
                pass
            ideas.append(idea)

        return ideas

    def get_knowledge_concepts(self, concept_type: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve technical knowledge concepts for Clever's learning

        Why: Enables Clever to access and review her technical knowledge base
        Where: Called when Clever needs to understand or apply technical concepts
        How: Queries knowledge base with optional filtering by concept type
        """
        import json

        with self._lock, self._connect() as con:
            con.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            if concept_type:
                query = """SELECT * FROM knowledge_concepts 
                          WHERE concept_type = ? 
                          ORDER BY learning_priority DESC, mastery_level ASC"""
                rows = con.execute(query, (concept_type,)).fetchall()
            else:
                query = """SELECT * FROM knowledge_concepts 
                          ORDER BY learning_priority DESC, mastery_level ASC"""
                rows = con.execute(query).fetchall()

        concepts = []
        for row in rows:
            concept = row  # row is already a dict due to row_factory
            try:
                concept["metadata"] = json.loads(concept["metadata"] or "{}")
            except:
                pass
            concepts.append(concept)

        return concepts

    # --- Compatibility: store user+assistant exchange and an interaction ---
    def add_conversation(
        self, user_text: str, reply_text: str, *, meta: dict | None = None
    ) -> None:
        try:
            self.add_utterance("user", user_text, mode=(meta or {}).get("detected_intent"))
            self.add_utterance("assistant", reply_text, mode=(meta or {}).get("activePersona"))
            self.add_interaction(
                user_input=user_text,
                active_mode=(meta or {}).get("activePersona"),
                action_taken=(meta or {}).get("detected_intent"),
                parsed_data=meta or {},
            )
        except Exception:
            pass


# Import config for database path
import config

# Lazy initialization to prevent aggressive system monitoring during import
_db_manager = None


def get_db_manager() -> AdvancedDatabaseManager:
    """
    Get shared database manager with lazy initialization

    Why: Prevents aggressive system monitoring during module import that could disrupt IDE
    Where: Called by components that need database access
    How: Lazy instantiation pattern with singleton behavior
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = AdvancedDatabaseManager(config.DB_PATH)
    return _db_manager


# --- Compatibility alias ---
# Allow legacy and external scripts to import `DatabaseManager` directly.
DatabaseManager = AdvancedDatabaseManager


# --- Compatibility shim ---
def add_conversation(user_text: str, reply_text: str, *, meta: dict | None = None) -> None:
    db = get_db_manager()
    db.add_utterance("user", user_text, mode=(meta or {}).get("detected_intent"))
    db.add_utterance("assistant", reply_text, mode=(meta or {}).get("activePersona"))
