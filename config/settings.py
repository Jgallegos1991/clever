"""
config/settings.py - Enhanced Configuration Management for Clever Digital Brain Extension

Why: Provides comprehensive, validated, and environment-aware configuration management
     for all Clever system components. Centralizes settings with hardware optimization,
     security enforcement, and hot-reload capabilities.

Where: Enhanced configuration system providing type-safe, validated settings for
       all Clever modules with environment detection and hardware awareness.

How: Uses structured configuration classes with validation, environment detection,
     hardware optimization, and dynamic reloading for robust configuration management.

File Usage:
    - Centralized settings: Single source of truth for all Clever configuration
    - Type safety: Validated configuration objects with proper typing
    - Environment awareness: Automatic adaptation to dev/prod/test environments
    - Hardware optimization: Dynamic settings based on device capabilities
    - Security enforcement: Validates privacy and offline-first requirements
    - Performance tuning: Memory-aware configuration for Chrome OS constraints
    - Hot reloading: Configuration updates without system restart
    - Module coordination: Consistent configuration interface for all components

Connects to:
    - config/base.py: Configuration foundation classes and validation utilities
    - config.py: Legacy configuration compatibility and migration bridge
    - app.py: Enhanced Flask configuration through CleverConfig
    - hardware_optimizer.py: Hardware-aware configuration optimization
    - All Clever modules: Type-safe configuration access via settings objects
"""

import os
from pathlib import Path
from typing import Any, Dict

from .base import (
    BaseConfig,
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


class CleverConfig(BaseConfig):
    """Main Clever configuration with all subsystem settings"""

    def __init__(self, environment: Environment = None):
        # Auto-detect environment if not specified
        if environment is None:
            environment = EnvironmentDetector.detect_environment()

        super().__init__(environment)

    def _load_config(self) -> None:
        """Load configuration from environment, files, and hardware detection"""

        # Get root directory
        root_dir = Path(__file__).resolve().parent.parent

        # Detect hardware profile for optimization
        hardware_profile = EnvironmentDetector.detect_hardware_profile()

        # Load user configuration with fallback
        try:
            import user_config

            user_host = getattr(user_config, "CLEVER_HOST", "127.0.0.1")
            user_port = getattr(user_config, "CLEVER_PORT", 5000)
            user_debug = getattr(user_config, "DEBUG_MODE", False)
            user_external = getattr(user_config, "CLEVER_EXTERNAL_ACCESS", False)
            tailscale_enabled = getattr(user_config, "TAILSCALE_ENABLED", False)
            tailscale_hostname = getattr(user_config, "TAILSCALE_HOSTNAME", None)
        except ImportError:
            user_host = "127.0.0.1"
            user_port = 5000
            user_debug = False
            user_external = False
            tailscale_enabled = False
            tailscale_hostname = None

        # Database configuration
        db_path = os.environ.get("CLEVER_DB_PATH", str(root_dir / "clever.db"))
        self.database = DatabaseConfig(
            path=Path(db_path),
            backup_interval_hours=int(os.environ.get("CLEVER_BACKUP_INTERVAL", "24")),
            max_backup_count=int(os.environ.get("CLEVER_MAX_BACKUPS", "7")),
            connection_timeout=int(os.environ.get("CLEVER_DB_TIMEOUT", "30")),
            enable_wal_mode=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_DB_WAL", "true")
            ),
        )

        # Network configuration with security enforcement
        self.network = NetworkConfig(
            host=user_host if user_external and tailscale_enabled else "127.0.0.1",
            port=user_port,
            debug=user_debug and self.environment == Environment.DEVELOPMENT,
            enable_external_access=user_external and tailscale_enabled,
            tailscale_enabled=tailscale_enabled,
            tailscale_hostname=tailscale_hostname,
        )

        # Memory configuration based on hardware
        intelligence_level = hardware_profile["intelligence_level"]
        available_memory = hardware_profile["available_memory_mb"]

        # Adaptive memory limits based on available memory
        if available_memory > 2000:
            max_memory = 500
            warning_threshold = 400
            conversation_limit = 100
            cache_limit = 2000
        elif available_memory > 1500:
            max_memory = 300
            warning_threshold = 250
            conversation_limit = 75
            cache_limit = 1500
        elif available_memory > 1000:
            max_memory = 200
            warning_threshold = 150
            conversation_limit = 50
            cache_limit = 1000
        else:
            max_memory = 150
            warning_threshold = 100
            conversation_limit = 25
            cache_limit = 500

        self.memory = MemoryConfig(
            max_memory_mb=max_memory,
            warning_threshold_mb=warning_threshold,
            critical_threshold_mb=max_memory // 2,
            conversation_history_limit=conversation_limit,
            cache_size_limit=cache_limit,
            enable_monitoring=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_MEMORY_MONITORING", "true")
            ),
            check_interval_seconds=int(os.environ.get("CLEVER_MEMORY_CHECK_INTERVAL", "30")),
        )

        # Security configuration with privacy enforcement
        self.security = SecurityConfig(
            offline_only=True,  # Enforced for digital sovereignty
            enable_offline_guard=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_OFFLINE_GUARD", "true")
            ),
            allowed_networks=(
                ["127.0.0.1", "localhost", "100.0.0.0/8"]
                if tailscale_enabled
                else ["127.0.0.1", "localhost"]
            ),
            enable_file_validation=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_FILE_VALIDATION", "true")
            ),
            max_upload_size_mb=int(os.environ.get("CLEVER_MAX_UPLOAD_MB", "50")),
            allowed_file_types=os.environ.get("CLEVER_ALLOWED_TYPES", "txt,md,pdf,json").split(","),
        )

        # UI configuration based on hardware capabilities
        particle_count = hardware_profile["recommended_particle_count"]

        self.ui = UIConfig(
            particle_count=particle_count,
            max_particle_count=min(1000, particle_count * 3),
            enable_3d_effects=intelligence_level not in [IntelligenceLevel.MINIMAL],
            animation_quality=(
                "high" if intelligence_level == IntelligenceLevel.MAXIMUM else "balanced"
            ),
            theme=os.environ.get("CLEVER_THEME", "dark"),
            enable_debug_overlay=user_debug and self.environment == Environment.DEVELOPMENT,
        )

        # Persona configuration
        self.persona = PersonaConfig(
            default_mode=os.environ.get("CLEVER_DEFAULT_MODE", "Auto"),
            available_modes=os.environ.get(
                "CLEVER_MODES", "Auto,Creative,Deep Dive,Support,Quick Hit"
            ).split(","),
            response_timeout_seconds=int(os.environ.get("CLEVER_RESPONSE_TIMEOUT", "30")),
            enable_proactive_suggestions=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_SUGGESTIONS", "true")
            ),
            memory_enabled=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_MEMORY", "true")
            ),
            learning_enabled=ConfigValidator.validate_boolean_env(
                os.environ.get("CLEVER_LEARNING", "true")
            ),
        )

        # Path configuration
        default_sync_dir = root_dir / "data" / "sync" / "clever_sync"
        sync_dir = Path(os.environ.get("CLEVER_SYNC_DIR", str(default_sync_dir))).resolve()
        synaptic_dir = Path(os.environ.get("CLEVER_SYNAPTIC_DIR", "synaptic_hub_sync")).resolve()

        self.paths = PathConfig(
            root_dir=root_dir,
            sync_dir=sync_dir,
            synaptic_hub_dir=synaptic_dir,
            backup_dir=root_dir / "backups",
            logs_dir=root_dir / "logs",
            upload_dir=root_dir / "uploads",
        )

        # Store hardware profile for reference
        self.hardware_profile = hardware_profile

        # Environment-specific overrides
        self._apply_environment_overrides()

    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides"""

        if self.environment == Environment.PRODUCTION:
            # Production overrides for security and performance
            self.network.debug = False
            self.network.host = "127.0.0.1"  # Force localhost in production
            self.ui.enable_debug_overlay = False
            self.security.enable_file_validation = True

        elif self.environment == Environment.TESTING:
            # Testing overrides for isolation and predictability
            self.database.path = self.paths.root_dir / "test_clever.db"
            self.memory.enable_monitoring = False
            self.persona.response_timeout_seconds = 5  # Faster tests
            self.ui.particle_count = 50  # Minimal particles for tests

        elif self.environment == Environment.DEVELOPMENT:
            # Development overrides for debugging and flexibility
            self.ui.enable_debug_overlay = True
            self.memory.check_interval_seconds = 10  # More frequent monitoring

    def _validate_config(self) -> None:
        """Validate complete configuration"""

        # Validate critical paths exist or can be created
        critical_paths = [
            self.paths.root_dir,
            self.paths.sync_dir,
            self.paths.backup_dir,
        ]

        for path in critical_paths:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    raise ValueError(f"Cannot create critical path {path}: {e}")

        # Validate database can be created/accessed
        db_dir = self.database.path.parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)

        # Validate memory configuration
        if self.memory.critical_threshold_mb >= self.memory.warning_threshold_mb:
            raise ValueError("Critical memory threshold must be less than warning threshold")

        if self.memory.warning_threshold_mb >= self.memory.max_memory_mb:
            raise ValueError("Warning threshold must be less than max memory")

        # Validate network configuration
        if self.network.enable_external_access and not self.security.offline_only:
            raise ValueError("External access requires offline_only mode for digital sovereignty")

    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask-compatible configuration dictionary"""
        return {
            "DEBUG": self.network.debug,
            "SECRET_KEY": os.environ.get("CLEVER_SECRET_KEY", "dev-key-change-in-production"),
            "MAX_CONTENT_LENGTH": self.security.max_upload_size_mb * 1024 * 1024,
            "UPLOAD_FOLDER": str(self.paths.upload_dir),
            "DATABASE_PATH": str(self.database.path),
            "MEMORY_LIMIT_MB": self.memory.max_memory_mb,
            "PARTICLE_COUNT": self.ui.particle_count,
            "ENABLE_CORS": False,  # Disabled for security
            "JSONIFY_PRETTYPRINT_REGULAR": self.network.debug,
        }

    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware profile information"""
        return {
            "environment": self.environment.value,
            "intelligence_level": self.hardware_profile["intelligence_level"].value,
            "total_memory_mb": self.hardware_profile["total_memory_mb"],
            "available_memory_mb": self.hardware_profile["available_memory_mb"],
            "particle_count": self.ui.particle_count,
            "max_particle_count": self.ui.max_particle_count,
            "memory_limit_mb": self.memory.max_memory_mb,
            "conversation_limit": self.memory.conversation_history_limit,
        }


# Global configuration instance
_config: CleverConfig = None


def get_config() -> CleverConfig:
    """Get global Clever configuration instance"""
    global _config
    if _config is None:
        _config = CleverConfig()
    return _config


def reload_config() -> CleverConfig:
    """Reload global configuration"""
    global _config
    _config = CleverConfig()
    return _config


# Convenience functions for backward compatibility
def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().database


def get_network_config() -> NetworkConfig:
    """Get network configuration"""
    return get_config().network


def get_memory_config() -> MemoryConfig:
    """Get memory configuration"""
    return get_config().memory


def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return get_config().security


def get_ui_config() -> UIConfig:
    """Get UI configuration"""
    return get_config().ui


def get_persona_config() -> PersonaConfig:
    """Get persona configuration"""
    return get_config().persona


def get_paths_config() -> PathConfig:
    """Get paths configuration"""
    return get_config().paths
