"""app.py - Clever's Digital Brain Extension & Cognitive Partnership System (Main Application)

Why: Central orchestration hub for Jay's digital brain extension & cognitive
partnership system. This is where the magic happens - where all of Clever's
cognitive capabilities, authentic personality, memory systems, and holographic
interface come together to create the seamless digital other half experience.

Where: Core Flask application server that coordinates all components of Clever's
cognitive partnership system. Every conversation, every thought, every particle
of the holographic interface flows through this central nervous system of the
digital brain extension.

How: Flask application with complete digital sovereignty (offline-only), modular
route architecture, hardware optimization, enhanced configuration integration,
and seamless coordination between persona engine, memory system, evolution
engine, and holographic particle interface.

File Usage:
    - Central nervous system: Primary orchestration hub for all Clever cognitive operations
    - Web server foundation: Flask application serving holographic UI and cognitive APIs
    - Route coordination: Modular blueprint system organizing cognitive, creative, and system routes
    - Persona integration: Direct connection to PersonaEngine for authentic conversation generation
    - Memory orchestration: Coordinates memory formation, retrieval, and relationship building
    - Evolution logging: Tracks all interactions for continuous learning and cognitive growth
    - Digital sovereignty: Enforces offline-first operation with no external dependencies
    - Hardware optimization: Chrome OS specific optimizations and memory management
    - Security enforcement: Implements secure access controls and data protection
    - Performance monitoring: Comprehensive telemetry, health checks, and system analytics
    - Network configuration: Manages local and Tailscale remote access capabilities
    - Development support: Debug endpoints and runtime introspection for system transparency
    - Knowledge processing: Document ingestion, search, and intelligent content management
    - Visual cognition: Serves particle engine and holographic cognitive interface
    - Error handling: Comprehensive error recovery with graceful degradation

Connects to:
    - persona.py: Core personality engine integration for authentic conversation
        - PersonaEngine() initialization for cognitive partnership capabilities
        - generate() calls for all user interaction processing and response generation
        - Response mode coordination and personality adaptation
    - evolution_engine.py: Learning system integration for continuous improvement
        - log_interaction() calls for every user conversation to enable learning
        - Performance metrics tracking for system optimization
        - Cognitive growth analytics and behavioral adaptation
    - database.py: Single database coordination for memory and knowledge management
        - All persistence operations flow through unified clever.db database
        - Memory storage, retrieval, and relationship building data
        - Knowledge base management and search capabilities
    - config/: Enhanced configuration system for hardware-aware optimization
        - CleverConfig integration for type-safe configuration management
        - Hardware detection and Chrome OS specific optimizations
        - Network configuration and security settings
    - routes/: Modular blueprint architecture for organized functionality
        - cognitive.py: Core chat and AI interaction endpoints
        - creative.py: Visual cognition and particle system APIs
        - system.py: Health monitoring and system status endpoints
        - core.py: Basic page routes and static file serving
    - debug_config.py: Comprehensive debugging and performance monitoring
        - System-wide logging and error tracking capabilities
        - Performance analytics and optimization insights
        - Runtime introspection and system transparency
    - templates/index.html: Holographic UI template with particle system
        - Main cognitive interface with visual thinking capabilities
        - Particle engine integration for thought visualization
    - static/: Frontend assets for holographic cognitive interface
        - JavaScript engines for particle system and visual cognition
        - CSS styling for dark holographic aesthetic
        - Performance modules for frontend optimization
    - utils/offline_guard.py: Digital sovereignty enforcement
        - Network access control and privacy protection
        - Offline-first operation verification

Performance Notes:
    - Memory usage: Optimized for Chrome OS with configurable memory limits and intelligent caching
    - CPU impact: Efficient Flask serving with hardware-aware optimizations and background processing
    - I/O operations: Minimal database operations with connection pooling and smart batching
    - Scaling limits: Designed for intensive single-user cognitive partnership with room for growth
    - Network efficiency: Local-first with optional Tailscale remote access for multi-device usage
    - Response latency: Sub-200ms conversation response times for natural cognitive flow
    - Resource monitoring: Real-time telemetry and health checks for system optimization
    - Frontend optimization: Efficient static file serving with caching and compression

Critical Dependencies:
    - Required packages: Flask 2.x+ for web framework, Python 3.8+ for language features
    - Core modules: All Clever cognitive modules (persona, evolution, database, nlp_processor)
    - Configuration system: Enhanced config package for hardware-aware settings
    - Debug system: Comprehensive debugging and monitoring capabilities
    - Template engine: Jinja2 for holographic UI rendering and dynamic content
    - Static files: Complete frontend asset system for particle interface
    - Route modules: Modular blueprint system for organized functionality
    - Security modules: Offline guard and access control systems
    - Hardware detection: System capabilities for Chrome OS optimization
    - Network modules: Optional Tailscale integration for secure remote access
"""

import atexit
import os
import sys
import time
from pathlib import Path

from flask import Flask

from config import (  # Enhanced configuration system
    IPFS_REPO_PATH,
    SYNC_ROOT_PATH,
    get_enhanced_config,
    get_flask_config,
)
from database import get_db_manager
from debug_config import get_debugger  # Unified debugger with error/info methods
from hardware_optimizer import (  # Hardware-aware optimization
    get_current_hardware_profile,
    get_hardware_optimizer,
)
from introspection import (  # Runtime introspection utilities
    register_error_handler,
    runtime_state,
    traced_render,
)
# === Self-Introspection Integration (added) ===
from self_introspect import start_background_loop
from user_config import USER_EMAIL, USER_NAME
from utils import offline_guard  # Enforce offline constraints

start_background_loop()
# ==============================================

# Tailscale is an optional environment-specific feature; not required on main.
TAILSCALE_ENABLED = False
TAILSCALE_HOSTNAME = ""
try:
    from tailscale_config import create_remote_access_info, get_tailscale_ip, get_tailscale_status  # type: ignore[import]

    TAILSCALE_AVAILABLE = True
except ImportError:
    TAILSCALE_AVAILABLE = False

    def get_tailscale_ip():  # type: ignore[misc]
        """Stub: returns None when tailscale_config module is not available."""
        return None

    def get_tailscale_status():  # type: ignore[misc]
        """Stub: returns 'unavailable' when tailscale_config module is not available."""
        return "unavailable"

    def create_remote_access_info():  # type: ignore[misc]
        """Stub: no-op when tailscale_config module is not available."""
        pass

# Enforce offline operation immediately (Unbreakable Rule #1)
offline_guard.enable()


def _should_enforce_startup_invariants() -> bool:
    """
    Enforce invariants for real runtime, but avoid killing test collection in CI.
    Default: enforce when running the server directly.
    Override: set CLEVER_ENFORCE_STARTUP_INVARIANTS=1 to force, 0 to disable.
    """
    val = os.getenv("CLEVER_ENFORCE_STARTUP_INVARIANTS")
    if val is not None:
        return val.strip().lower() in ("1", "true", "yes", "on")
    return __name__ == "__main__"


def _require_ipfs_repo() -> None:
    """
    Ensure the canonical IPFS repository directory exists, creating it if needed.

    Why: Clever's brain store lives in an IPFS repo. If the directory is absent at
         startup Jay would see a cryptic error later; we surface it immediately with
         a clear actionable message.
    Where: Called during startup invariant checks (python app.py / direct invocation).
    How: Reads IPFS_REPO_PATH from config and creates the directory tree with
         parents=True so nested paths work on a fresh clone.

    File Usage:
        - Called by: app.py startup invariant block (when CLEVER_ENFORCE_STARTUP_INVARIANTS is on)
        - Data flow: Reads IPFS_REPO_PATH from config/__init__.py; creates directory on filesystem

    Connects to:
        - config/__init__.py: IPFS_REPO_PATH sourced from IPFS_PATH env var or root/ipfs_repo default
        - Makefile: setup-ipfs target also ensures this directory exists for non-__main__ paths
    """
    ipfs_path = Path(IPFS_REPO_PATH)
    if not ipfs_path.exists():
        ipfs_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created IPFS repo directory: {ipfs_path}")
    else:
        print(f"✅ IPFS repo directory present: {ipfs_path}")


def _require_sync_root() -> None:
    """
    Ensure the Clever sync root directory exists, creating it if needed.

    Why: Sync watcher and file ingestor depend on this directory being present.
         Missing it at startup would cause silent failures in background services.
    Where: Called during startup invariant checks alongside _require_ipfs_repo.
    How: Reads SYNC_ROOT_PATH from config and creates the directory tree with
         parents=True so the full data/sync/clever_sync path is created at once.

    File Usage:
        - Called by: app.py startup invariant block (when CLEVER_ENFORCE_STARTUP_INVARIANTS is on)
        - Data flow: Reads SYNC_ROOT_PATH from config/__init__.py; creates directory on filesystem

    Connects to:
        - config/__init__.py: SYNC_ROOT_PATH sourced from CLEVER_SYNC_DIR env var or default
        - sync_watcher.py: start_watchers() expects SYNC_ROOT_PATH directory to exist
        - file_ingestor.py: FileIngestor scans this directory for new documents to ingest
    """
    sync_path = Path(SYNC_ROOT_PATH)
    if not sync_path.exists():
        sync_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created sync root directory: {sync_path}")
    else:
        print(f"✅ Sync root directory present: {sync_path}")


if _should_enforce_startup_invariants():
    _require_ipfs_repo()
    _require_sync_root()

# Apply hardware optimization immediately for memory constraints
try:
    hardware_optimizer = get_hardware_optimizer()
    optimization_result = hardware_optimizer.apply_optimization()
    print(f"🧠 Applied {optimization_result['strategy_applied']} hardware optimization")
    print(f"   Intelligence Level: {optimization_result['intelligence_level']}")
    print(f"   Available Memory: {optimization_result.get('memory_after_mb', 'unknown')}MB")
except Exception as e:
    print(f"⚠️  Hardware optimization failed: {e}")
    # Continue anyway - Clever can still run with defaults

# Create Flask app with enhanced configuration
app = Flask(__name__)
# Apply enhanced configuration
enhanced_config = get_enhanced_config()
app.config.update(get_flask_config())
# Install global error capture for introspection (still lets Flask debug raise)
register_error_handler(app)

# Unified debugger (supports info, debug, warning, error)
debugger = get_debugger()

# Log Tailscale availability now that debugger is initialized
if not TAILSCALE_AVAILABLE:
    debugger.info("tailscale", "Tailscale module not available - install tailscale_config.py")

# Import evolution engine at startup - required for cognitive functionality
from evolution_engine import get_evolution_engine

EVOLUTION_ENGINE_AVAILABLE = True
debugger.info("app", "Evolution engine loaded successfully")


def configure_network():
    """
    Configure network settings using enhanced configuration system.

    Why: Enables secure remote access while maintaining digital sovereignty
    Where: Called during app startup to determine network binding
    How: Uses enhanced config for host/port settings with Tailscale detection

    Returns:
        tuple: (host, port, network_info) for Flask app configuration
    """
    # Get configuration from enhanced config system
    config = get_enhanced_config()
    host = config.network.host
    configured_port = getattr(config.network, "port", 5000) or 5000
    if configured_port != 5000:
        debugger.info(
            "network",
            f"Port override detected ({configured_port}) - forcing 5000 for local UI consistency",
        )
    port = 5000
    network_info = {"mode": "localhost_only", "tailscale": False}

    if TAILSCALE_ENABLED and TAILSCALE_AVAILABLE:
        debugger.info("network", "Tailscale enabled - checking network status...")
        tailscale_ip = get_tailscale_ip()

        if tailscale_ip:
            host = "0.0.0.0"
            network_info = {
                "mode": "tailscale_network",
                "tailscale": True,
                "tailscale_ip": tailscale_ip,
                "hostname": TAILSCALE_HOSTNAME,
            }
            debugger.info("network", f"Tailscale IP detected: {tailscale_ip}")
            debugger.info("network", "Binding to 0.0.0.0 for Tailscale access")
        else:
            debugger.info("network", "Tailscale IP not available - falling back to localhost")
    else:
        debugger.info("network", "Tailscale disabled - using localhost only")

    return host, port, network_info


# Configure network settings
NETWORK_HOST, NETWORK_PORT, NETWORK_INFO = configure_network()

# In-memory telemetry (server-side)
TELEMETRY = {
    "total_chats": 0,
    "avg_latency_ms": 0.0,
    "last_latency_ms": 0.0,
    "last_chat_ts": None,
    "last_error": None,
    "start_ts": time.time(),
}

BACKGROUND_SERVICES = {}


def start_background_services() -> None:
    """Kick off background helpers (sync watcher, etc.) when the app boots."""
    if BACKGROUND_SERVICES.get("sync_watcher"):
        return
    try:
        from sync_watcher import start_watchers

        observer = start_watchers()
        BACKGROUND_SERVICES["sync_watcher"] = observer
        debugger.info("app", "Embedded sync watcher running")
    except Exception as exc:
        debugger.warning("app", f"Sync watcher unavailable: {exc}")


def stop_background_services() -> None:
    """Gracefully tear down background helpers on shutdown."""
    observer = BACKGROUND_SERVICES.pop("sync_watcher", None)
    if observer:
        try:
            observer.stop()
            observer.join(timeout=5)
        except Exception as exc:
            debugger.warning("app", f"Error stopping sync watcher: {exc}")


atexit.register(stop_background_services)

# Initialize persona engine - required for Clever's digital brain
# Register modular routes for additional functionality via explicit blueprints
# Why: Ensure clear, intentional URL structure and avoid hidden registrations
# Where: app.py is the single source of truth for Flask blueprint wiring
# How: Import blueprints from route modules and register with desired prefixes
from routes import register_routes

# Core UI routes (no prefix, serves '/')
register_routes(app)
debugger.info("app", "Blueprints registered centrally via routes.register_routes()")


if __name__ == "__main__":
    debugger.info("app", "Clever AI starting...")
    debugger.info("network", f"Network mode: {NETWORK_INFO['mode']}")
    debugger.info("network", f"Binding to {NETWORK_HOST}:{NETWORK_PORT}")

    if NETWORK_INFO.get("tailscale"):
        debugger.info("network", f"Tailscale hostname: {NETWORK_INFO.get('hostname')}")
        debugger.info("network", "Remote access available via Tailscale network")

        # Create access info file for remote connections
        if TAILSCALE_AVAILABLE:
            try:
                create_remote_access_info()
                debugger.info("network", "Remote access info file created")
            except Exception as e:
                debugger.info("network", f"Could not create access info: {e}")
    else:
        debugger.info("network", "Local access only - Tailscale disabled")

    start_background_services()
    app.run(debug=False, host=NETWORK_HOST, port=NETWORK_PORT)
