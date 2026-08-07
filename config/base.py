"""
config/base.py - Base Configuration Classes for Clever Digital Brain Extension

Why: Provides structured, validated configuration management with environment-aware
     settings, hardware optimization, and centralized control over all Clever
     system parameters. Ensures consistent configuration across all modules.

Where: Foundation configuration system imported by enhanced config.py and used
       throughout Clever for type-safe, validated configuration management.

How: Object-oriented configuration with validation, environment detection,
     hardware awareness, and dynamic reloading capabilities.

File Usage:
    - Configuration foundation: Base classes for all Clever configuration objects
    - Type safety: Pydantic-like validation without external dependencies
    - Environment management: Automatic environment detection and adaptation
    - Hardware awareness: Dynamic configuration based on device capabilities
    - Validation framework: Ensures all configuration values are valid and safe
    - Hot reloading: Support for configuration changes without restart
    - Security enforcement: Validates offline-first and privacy settings
    - Performance optimization: Hardware-aware configuration tuning

Connects to:
    - config.py: Enhanced configuration system using these base classes
    - hardware_optimizer.py: Hardware-aware configuration management
    - app.py: Type-safe configuration access throughout Flask application
    - All Clever modules: Consistent configuration interface across system
"""

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class Environment(Enum):
    """Environment types for Clever configuration"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class IntelligenceLevel(Enum):
    """Intelligence levels for hardware-aware optimization"""

    MINIMAL = "minimal"
    ADAPTIVE = "adaptive"
    BALANCED = "balanced"
    HIGH = "high"
    MAXIMUM = "maximum"


class ConfigValidator:
    """Configuration validation utilities"""

    @staticmethod
    def validate_path(path: Union[str, Path]) -> Path:
        """Validate and convert path to Path object"""
        if isinstance(path, str):
            path = Path(path)
        return path.resolve()

    @staticmethod
    def validate_port(port: int) -> int:
        """Validate network port number"""
        if not (1 <= port <= 65535):
            raise ValueError(f"Port must be between 1-65535, got {port}")
        return port

    @staticmethod
    def validate_memory_mb(memory_mb: int) -> int:
        """Validate memory size in MB"""
        if memory_mb < 0:
            raise ValueError(f"Memory must be positive, got {memory_mb}")
        return memory_mb

    @staticmethod
    def validate_boolean_env(value: str) -> bool:
        """Convert environment variable string to boolean"""
        return str(value).lower() in {"1", "true", "yes", "on"}


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    path: Path
    backup_interval_hours: int = 24
    max_backup_count: int = 7
    connection_timeout: int = 30
    enable_wal_mode: bool = True

    def __post_init__(self):
        self.path = ConfigValidator.validate_path(self.path)


@dataclass
class NetworkConfig:
    """Network and server configuration"""

    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    enable_external_access: bool = False
    tailscale_enabled: bool = False
    tailscale_hostname: Optional[str] = None

    def __post_init__(self):
        self.port = ConfigValidator.validate_port(self.port)

        # Enforce digital sovereignty - external access only via Tailscale
        if self.enable_external_access and not self.tailscale_enabled:
            self.host = "127.0.0.1"  # Force localhost if no secure tunnel


@dataclass
class MemoryConfig:
    """Memory management configuration"""

    max_memory_mb: int = 200
    warning_threshold_mb: int = 150
    critical_threshold_mb: int = 100
    conversation_history_limit: int = 50
    cache_size_limit: int = 1000
    enable_monitoring: bool = True
    check_interval_seconds: int = 30

    def __post_init__(self):
        self.max_memory_mb = ConfigValidator.validate_memory_mb(self.max_memory_mb)
        self.warning_threshold_mb = ConfigValidator.validate_memory_mb(self.warning_threshold_mb)
        self.critical_threshold_mb = ConfigValidator.validate_memory_mb(self.critical_threshold_mb)


@dataclass
class SecurityConfig:
    """Security and privacy configuration"""

    offline_only: bool = True
    enable_offline_guard: bool = True
    allowed_networks: List[str] = field(default_factory=lambda: ["127.0.0.1", "localhost"])
    enable_file_validation: bool = True
    max_upload_size_mb: int = 50
    allowed_file_types: List[str] = field(default_factory=lambda: ["txt", "md", "pdf"])

    def __post_init__(self):
        # Enforce digital sovereignty
        if not self.offline_only:
            self.offline_only = True  # Force offline operation

        self.max_upload_size_mb = ConfigValidator.validate_memory_mb(self.max_upload_size_mb)


@dataclass
class UIConfig:
    """User interface configuration"""

    particle_count: int = 300
    max_particle_count: int = 1000
    enable_3d_effects: bool = True
    animation_quality: str = "balanced"  # minimal, balanced, high
    theme: str = "dark"
    enable_debug_overlay: bool = False

    def __post_init__(self):
        if self.particle_count > self.max_particle_count:
            self.particle_count = self.max_particle_count


@dataclass
class PersonaConfig:
    """Personality and response configuration"""

    default_mode: str = "Auto"
    available_modes: List[str] = field(
        default_factory=lambda: [
            "Auto",
            "Creative",
            "Deep Dive",
            "Support",
            "Quick Hit",
        ]
    )
    response_timeout_seconds: int = 30
    enable_proactive_suggestions: bool = True
    memory_enabled: bool = True
    learning_enabled: bool = True


@dataclass
class PathConfig:
    """File system paths configuration"""

    root_dir: Path
    sync_dir: Path
    synaptic_hub_dir: Path
    backup_dir: Path
    logs_dir: Path
    upload_dir: Path

    def __post_init__(self):
        # Validate and resolve all paths
        self.root_dir = ConfigValidator.validate_path(self.root_dir)
        self.sync_dir = ConfigValidator.validate_path(self.sync_dir)
        self.synaptic_hub_dir = ConfigValidator.validate_path(self.synaptic_hub_dir)
        self.backup_dir = ConfigValidator.validate_path(self.backup_dir)
        self.logs_dir = ConfigValidator.validate_path(self.logs_dir)
        self.upload_dir = ConfigValidator.validate_path(self.upload_dir)

        # Create directories if they don't exist
        for path in [self.sync_dir, self.backup_dir, self.logs_dir, self.upload_dir]:
            path.mkdir(parents=True, exist_ok=True)


class BaseConfig(ABC):
    """Base configuration class with environment awareness"""

    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self._load_config()
        self._validate_config()

    @abstractmethod
    def _load_config(self) -> None:
        """Load configuration from various sources"""
        pass

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate configuration values"""
        pass

    def reload(self) -> None:
        """Hot reload configuration"""
        self._load_config()
        self._validate_config()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            if hasattr(value, "__dict__"):
                result[key] = value.__dict__
            else:
                result[key] = value
        return result

    def save_to_file(self, path: Path) -> None:
        """Save configuration to JSON file"""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class EnvironmentDetector:
    """Detects current environment and hardware capabilities"""

    @staticmethod
    def detect_environment() -> Environment:
        """Detect current environment from various indicators"""
        env_var = os.environ.get("CLEVER_ENVIRONMENT", "").lower()

        if env_var in ["prod", "production"]:
            return Environment.PRODUCTION
        elif env_var in ["test", "testing"]:
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT

    @staticmethod
    def detect_hardware_profile() -> Dict[str, Any]:
        """Detect hardware capabilities for optimization"""
        try:
            import psutil

            # Get system memory
            memory = psutil.virtual_memory()
            total_mb = memory.total // (1024 * 1024)
            available_mb = memory.available // (1024 * 1024)

            # Determine intelligence level based on available memory
            if available_mb > 2000:
                intelligence = IntelligenceLevel.MAXIMUM
                particle_count = 1000
            elif available_mb > 1500:
                intelligence = IntelligenceLevel.HIGH
                particle_count = 800
            elif available_mb > 1000:
                intelligence = IntelligenceLevel.BALANCED
                particle_count = 500
            elif available_mb > 500:
                intelligence = IntelligenceLevel.ADAPTIVE
                particle_count = 300
            else:
                intelligence = IntelligenceLevel.MINIMAL
                particle_count = 100

            return {
                "total_memory_mb": total_mb,
                "available_memory_mb": available_mb,
                "intelligence_level": intelligence,
                "recommended_particle_count": particle_count,
                "cpu_count": psutil.cpu_count(),
                "has_gpu": False,  # Conservative assumption for Chrome OS
            }

        except ImportError:
            # Fallback when psutil not available
            return {
                "total_memory_mb": 3772,  # Chrome OS baseline
                "available_memory_mb": 1000,  # Conservative estimate
                "intelligence_level": IntelligenceLevel.BALANCED,
                "recommended_particle_count": 300,
                "cpu_count": 4,
                "has_gpu": False,
            }
