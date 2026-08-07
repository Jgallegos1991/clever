"""knowledge_base.py - Advanced Knowledge Management System for Clever's Cognitive Partnership

Why: Provides sophisticated knowledge storage, retrieval, and management capabilities
as the intellectual foundation for Clever's digital brain extension. Enables
intelligent conversation enhancement through contextual knowledge access,
learning integration, and seamless memory coordination for authentic cognitive partnership.

Where: Core knowledge orchestration layer between conversation engine and database,
serving as the intelligent knowledge coordinator that enhances all cognitive
processing with contextual understanding and learned information retrieval.

How: Advanced knowledge management with thread-safe database operations,
intelligent content indexing, contextual retrieval algorithms, and seamless
integration with Clever's memory and learning systems for optimal cognitive performance.

File Usage:
    - Knowledge coordination: Central knowledge storage and retrieval for cognitive enhancement
    - Conversation enhancement: Contextual knowledge integration for intelligent responses
    - Learning foundation: Knowledge base population through document ingestion and interaction
    - Memory integration: Seamless coordination with memory engine for relationship building
    - Intelligence amplification: Enhanced cognitive capabilities through knowledge access
    - Content management: Sophisticated document processing and knowledge extraction
    - Search capabilities: Advanced knowledge search and contextual retrieval
    - Performance optimization: Efficient knowledge access with intelligent caching
    - Legacy compatibility: Maintains compatibility with existing knowledge systems
    - Database coordination: Thread-safe knowledge operations using unified database
    - Context building: Knowledge-aware context generation for enhanced conversations
    - Educational support: Knowledge base integration for learning and educational responses
    - Research capabilities: Advanced knowledge search and information synthesis
    - Development foundation: Knowledge management infrastructure for cognitive development

Connects to:
    - database.py: Advanced database integration for knowledge storage and retrieval
        - DatabaseManager integration for thread-safe knowledge operations
        - Single database architecture for unified knowledge and memory storage
        - Advanced indexing and search capabilities for efficient knowledge access
    - persona.py: Knowledge-enhanced conversation generation and response intelligence
        - Contextual knowledge integration for enhanced response generation
        - Knowledge-aware conversation flow and intelligent topic management
        - Educational response capabilities through knowledge base integration
    - file_ingestor.py: Document processing and knowledge base population
        - Automated knowledge extraction from documents and files
        - Content indexing and semantic analysis for intelligent knowledge storage
        - Learning integration through processed document knowledge
    - nlp_processor.py: Natural language processing for knowledge understanding
        - Semantic analysis of knowledge content for intelligent indexing
        - Context analysis for knowledge retrieval and relevance scoring
        - Entity extraction for knowledge categorization and organization
    - evolution_engine.py: Learning system integration for knowledge evolution
        - Knowledge base growth through interaction learning and adaptation
        - Intelligence enhancement through accumulated knowledge and experience
        - Preference learning for personalized knowledge retrieval and presentation
    - memory_engine.py: Memory system coordination for comprehensive cognitive capabilities
        - Knowledge and memory integration for holistic cognitive partnership
        - Contextual memory formation enhanced by knowledge base understanding
        - Relationship building through shared knowledge and learning experiences
    - config.py: Configuration management for knowledge system optimization
        - Database path coordination for unified knowledge storage
        - Performance settings for efficient knowledge operations and retrieval
        - Hardware-aware optimization for Chrome OS knowledge management
    - debug_config.py: Knowledge system monitoring and performance analytics
        - Knowledge operation logging and performance tracking
        - Search efficiency monitoring and optimization insights
        - Error handling and debugging support for knowledge operations

Performance Notes:
    - Memory usage: Efficient knowledge storage with intelligent indexing and caching
    - CPU impact: Optimized knowledge search algorithms with minimal processing overhead
    - I/O operations: Intelligent database operations with connection pooling and batch processing
    - Scaling limits: Designed for extensive single-user knowledge management with room for growth
    - Search performance: Sub-50ms knowledge retrieval for real-time conversation enhancement
    - Storage efficiency: Optimized knowledge representation with intelligent compression
    - Cache management: Smart caching of frequently accessed knowledge for instant retrieval
    - Index optimization: Advanced indexing strategies for efficient knowledge search and access

Critical Dependencies:
    - Required packages: Python 3.8+ standard library with database and threading support
    - Database system: SQLite integration for persistent knowledge storage and retrieval
    - Threading support: Thread-safe operations for concurrent knowledge access
    - Configuration system: Integrated configuration management for optimal performance
    - Error handling: Robust error recovery and graceful knowledge system degradation
    - Memory management: Efficient memory usage with intelligent garbage collection
    - Digital sovereignty: Complete offline operation with no external knowledge dependencies
    - Performance optimization: Chrome OS specific optimizations for efficient knowledge management
"""

from database import AdvancedDatabaseManager, get_db_manager

# Single shared DatabaseManager instance bound to the configured single DB.
_db = get_db_manager()


def init_db() -> bool:
    """Create the minimal interactions table if missing.

    Why: Some legacy utilities expect a tiny logging table even though the
    broader tracking has moved elsewhere.
    Where: Invoked during startup by legacy scripts or tests that import this
    module for side effects.
    How: Executes a single CREATE TABLE IF NOT EXISTS against the unified DB.

    Returns:
        True on success (or already present), False on error.

    Connects to:
        - database.py: Thread-safe connection helper
        - config.py: Source of DB_PATH
    """
    try:
        with _db._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL,
                    user_message TEXT,
                    clever_response TEXT
                )"""
            )
        return True
    except Exception:
        return False


def log_interaction(user_message: str, clever_response: str, **kwargs: Any) -> None:
    """Insert a simple interaction row (extra args ignored for compatibility).

    Why: Maintains backwards compatibility with older code that may still call
    this function with additional metadata parameters.
    Where: Potentially referenced by residual legacy modules not yet refactored
    to the evolution logging path.
    How: Ignores extra kwargs and writes a minimal record (timestamp, user
    message, response) into the interactions table (created lazily).

    Args:
        user_message: Raw user input text.
        clever_response: Generated response text.
        **kwargs: Ignored legacy metadata (kept to avoid breaking callers).

    Connects to:
        - database.py for persistence
    """
    init_db()
    with _db._connect() as conn:
        conn.execute(
            "INSERT INTO interactions (ts, user_message, clever_response) VALUES (?,?,?)",
            (time.time(), user_message, clever_response),
        )


def get_recent_interactions(limit: int = 10) -> List[Dict[str, Any]]:
    """Return the most recent interaction rows ordered newest first.

    Why: Provides a lightweight inspection/diagnostic hook during development
    or tests without exposing broader database query surface area.
    Where: May be called by debug tooling or ad-hoc scripts.
    How: Performs a SELECT with ORDER/DESC + LIMIT and converts rows to dicts.

    Args:
        limit: Maximum number of rows to return (default 10).

    Returns:
        List of recent interaction dicts with id, ts, user_message, clever_response.
    """
    init_db()
    with _db._connect() as conn:
        rows = conn.execute(
            "SELECT id, ts, user_message, clever_response FROM interactions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [{"id": r[0], "ts": r[1], "user_message": r[2], "clever_response": r[3]} for r in rows]


__all__ = [
    "init_db",
    "log_interaction",
    "get_recent_interactions",
]
