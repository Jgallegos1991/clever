"""
config/__init__.py - Enhanced Configuration Package for Clever Digital Brain Extension

Why: Provides clean, centralized configuration management with type safety, validation,
     environment awareness, and hardware optimization for all Clever system components.

Where: Configuration package entry point providing unified access to all Clever settings
       with backward compatibility and enhanced functionality.

How: Exposes configuration classes and convenience functions while maintaining
     compatibility with existing config.py usage patterns.

File Usage:
    - Package entry point: Clean imports for enhanced configuration system
    - Backward compatibility: Maintains existing config.py interface patterns
    - Type safety: Exposes typed configuration objects for better development
    - Configuration access: Single import point for all configuration needs

Connects to:
    - config/base.py: Configuration foundation classes and utilities
    - config/settings.py: Main CleverConfig implementation and management
    - All Clever modules: Enhanced configuration interface throughout system
"""

import os
from pathlib import Path

from .base import (
    ConfigValidator,
    DatabaseConfig,
    Environment,
    EnvironmentDetector,
    IntelligenceLevel,
    MemoryConfig,
    NetworkConfig,
    PathConfig,
    PersonaConfig,
    SecurityConfig,
    UIConfig,
)
from .settings import (
    CleverConfig,
    get_config,
    get_database_config,
    get_memory_config,
    get_network_config,
    get_paths_config,
    get_persona_config,
    get_security_config,
    get_ui_config,
    reload_config,
)

# Default configuration instance for immediate access
config = get_config()

# Convenience exports for common usage patterns
__all__ = [
    # Main configuration
    "CleverConfig",
    "get_config",
    "reload_config",
    # Configuration sections
    "get_database_config",
    "get_network_config",
    "get_memory_config",
    "get_security_config",
    "get_ui_config",
    "get_persona_config",
    "get_paths_config",
    # Configuration classes
    "DatabaseConfig",
    "NetworkConfig",
    "MemoryConfig",
    "SecurityConfig",
    "UIConfig",
    "PersonaConfig",
    "PathConfig",
    # Utilities
    "Environment",
    "IntelligenceLevel",
    "ConfigValidator",
    "EnvironmentDetector",
]

# Canonical path exports (public API)
ROOT_DIR = config.paths.root_dir
DB_PATH = os.environ.get("CLEVER_DB_PATH", str(ROOT_DIR / "clever.db"))
IPFS_REPO_PATH = os.environ.get("IPFS_PATH", str(ROOT_DIR / "ipfs_repo"))
SYNC_ROOT_PATH = os.environ.get("CLEVER_SYNC_DIR", str(ROOT_DIR / "data" / "sync" / "clever_sync"))


def _env_bool(name: str, default: bool = False) -> bool:
    """Convert environment variable to boolean with default fallback."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Backward compatibility exports - map old config.py patterns to new system
DB_PATH = str(config.database.path)
APP_HOST = config.network.host
APP_PORT = config.network.port
DEBUG = config.network.debug
SYNC_DIR = str(config.paths.sync_dir)
SYNAPTIC_HUB_DIR = str(config.paths.synaptic_hub_dir)
MEMORY_LIMITS = {
    "max_memory_mb": config.memory.max_memory_mb,
    "warning_threshold_mb": config.memory.warning_threshold_mb,
    "critical_threshold_mb": config.memory.critical_threshold_mb,
}
HARDWARE_CONFIG = config.get_hardware_info()

# Feature flags for backward compatibility
ENABLE_MEMORY_MONITORING = config.memory.enable_monitoring
MEMORY_CHECK_INTERVAL = config.memory.check_interval_seconds
RCLONE_REMOTE = os.environ.get("RCLONE_REMOTE", "")
RCLONE_SRC = os.environ.get("RCLONE_SRC", "")
RCLONE_DST = os.environ.get("RCLONE_DST", "")
RCLONE_EXTRA = os.environ.get(
    "RCLONE_EXTRA",
    "--fast-list --copy-links --checkers=4 --transfers=4 --stats-one-line --stats=30s",
)
AUTO_RCLONE_SCHEDULE = _env_bool("AUTO_RCLONE_SCHEDULE", False)
RCLONE_INTERVAL_MINUTES = int(os.environ.get("RCLONE_INTERVAL_MINUTES", "180"))
ENABLE_RCLONE = _env_bool(
    "ENABLE_RCLONE",
    bool(RCLONE_REMOTE and (RCLONE_SRC or RCLONE_DST)),
)

logs_dir_default = (
    str(config.paths.logs_dir) if hasattr(config, "paths") else str(Path.cwd() / "logs")
)

RCLONE_LOGS_REMOTE = os.environ.get("RCLONE_LOGS_REMOTE", RCLONE_REMOTE or "clever_drive")
RCLONE_LOGS_PATH = os.environ.get(
    "RCLONE_LOGS_PATH",
    "The_Synaptic_Hub/2_Clever_AI/logs",
)
RCLONE_LOGS_LOCAL = os.environ.get("RCLONE_LOGS_LOCAL", logs_dir_default)
RCLONE_LOGS_INTERVAL_MINUTES = int(
    os.environ.get(
        "RCLONE_LOGS_INTERVAL_MINUTES",
        os.environ.get("RCLONE_INTERVAL_MINUTES", "180"),
    )
)
RCLONE_LOGS_EXTRA = os.environ.get("RCLONE_LOGS_EXTRA", RCLONE_EXTRA)


def get_hardware_config():
    """Backward compatibility function for hardware config access"""
    return config.get_hardware_info()


# Enhanced configuration functions for full API compatibility
def get_enhanced_config():
    """Get enhanced CleverConfig instance with full type safety"""
    return config


def get_flask_config():
    """Get Flask-compatible configuration dictionary"""
    return config.get_flask_config()


# Export enhanced functions for full compatibility
__all__.extend(
    [
        "get_enhanced_config",
        "get_flask_config",
        "get_hardware_config",
        # Legacy compatibility exports
        "DB_PATH",
        "IPFS_REPO_PATH",
        "SYNC_ROOT_PATH",
        "APP_HOST",
        "APP_PORT",
        "DEBUG",
        "SYNC_DIR",
        "SYNAPTIC_HUB_DIR",
        "MEMORY_LIMITS",
        "HARDWARE_CONFIG",
        "ENABLE_MEMORY_MONITORING",
        "MEMORY_CHECK_INTERVAL",
        "ENABLE_RCLONE",
        "AUTO_RCLONE_SCHEDULE",
        "RCLONE_INTERVAL_MINUTES",
        "RCLONE_REMOTE",
        "RCLONE_SRC",
        "RCLONE_DST",
        "RCLONE_EXTRA",
        "RCLONE_LOGS_REMOTE",
        "RCLONE_LOGS_PATH",
        "RCLONE_LOGS_LOCAL",
        "RCLONE_LOGS_INTERVAL_MINUTES",
        "RCLONE_LOGS_EXTRA",
    ]
)
