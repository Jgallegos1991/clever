#!/usr/bin/env python3
"""
hardware_optimizer.py - Hardware-Aware System Optimization for Clever

Why: Creates a revolutionary AI system (Clever) within severe hardware constraints by
     implementing intelligent resource management that transforms limitations into
     competitive advantages. Ensures every byte of the 3.7GB RAM is optimized for
     maximum cognitive capabilities while maintaining VS Code functionality.

Where: Core optimization layer that coordinates between Clever's AI engine, VS Code,
       and system resources to create a symbiotic relationship where all components
       work together efficiently within the hardware boundaries.

How: Multi-layered approach combining real-time memory monitoring, intelligent process
     optimization, adaptive resource allocation, and revolutionary techniques like
     memory pressure responsiveness and cognitive scaling based on available resources.

Hardware Environment:
    - Total RAM: 3.7GB (3862416 kB)
    - Available: ~530MB (current constraint)
    - VS Code: ~1.3GB (multiple processes)
    - Pylance: 912MB (heaviest consumer)
    - Chrome OS: Additional overhead
    - Storage: 114GB eMMC (84GB free)

Connects to:
    - config.py: Hardware-aware configuration and performance limits
    - debug_config.py: Performance monitoring and system health tracking
    - app.py: Flask server optimization based on memory pressure
    - persona.py: Response generation limits guided by available memory
    - memory_engine.py: Intelligent memory allocation for AI operations
    - nlp_processor.py: Model selection based on memory constraints
    - static/js/engines/holographic-chamber.js: Particle limits for GPU memory
    - .vscode/settings.json: VS Code optimization settings
    - revolutionary_memory_strategy.py: Advanced memory management techniques
"""

import gc
import json
import os
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from debug_config import get_debugger

debugger = get_debugger()


@dataclass
class HardwareProfile:
    """
    Comprehensive hardware profile for optimization decisions.

    Why: Centralized hardware state tracking enables intelligent resource allocation
         and optimization decisions based on real-time system conditions.
    Where: Used throughout Clever ecosystem for performance-conscious implementations.
    How: Real-time system monitoring with cached values for performance efficiency.
    """

    total_memory_mb: int
    available_memory_mb: int
    free_memory_mb: int
    memory_pressure_level: str  # "low", "medium", "high", "critical"
    cpu_count: int
    cpu_usage_percent: float
    disk_free_gb: float
    disk_total_gb: float
    vscode_memory_mb: int
    clever_memory_mb: int
    optimization_level: str  # "maximum", "balanced", "aggressive", "emergency"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class OptimizationStrategy:
    """
    Hardware-specific optimization strategy.

    Why: Defines actionable optimization steps based on current hardware constraints
         to maximize Clever's cognitive capabilities within available resources.
    Where: Applied by HardwareOptimizer to implement memory-conscious configurations.
    How: Structured approach with specific actions, thresholds, and intelligence levels.
    """

    name: str
    memory_threshold_mb: int
    actions: List[str]
    vscode_settings: Dict[str, Any]
    clever_config: Dict[str, Any]
    intelligence_level: str
    description: str


class HardwareOptimizer:
    """
    Intelligent hardware-aware optimization system for Clever.

    Transforms memory constraints into competitive advantages through:
    - Real-time hardware monitoring and adaptation
    - VS Code optimization for cognitive partnership
    - Memory pressure responsive AI scaling
    - Intelligent resource allocation
    - Revolutionary memory management techniques
    """

    def __init__(self):
        """
        Initialize hardware optimizer with device-specific configurations.

        Why: Establishes baseline hardware understanding and optimization strategies
             tailored to the Chrome OS / GitHub Codespaces environment.
        Where: Called at Clever startup to enable hardware-aware operations.
        How: Discovers system capabilities and defines optimization strategies.
        """
        self.debugger = get_debugger()
        self.root_dir = Path(__file__).parent
        self.vscode_settings_path = self.root_dir / ".vscode" / "settings.json"

        # Hardware baseline from device specifications
        self.baseline_memory_mb = 3862416 / 1024  # From device specs

        # Initialize optimization strategies
        self.strategies = self._define_optimization_strategies()

        # Cache for performance
        self._last_profile_time = 0
        self._cached_profile: Optional[HardwareProfile] = None
        self._profile_cache_seconds = 5  # Update every 5 seconds

        self.debugger.info(
            "hardware_optimizer",
            f"Initialized for {self.baseline_memory_mb:.0f}MB baseline",
        )

    def _define_optimization_strategies(self) -> List[OptimizationStrategy]:
        """
        Define hardware-specific optimization strategies.

        Why: Creates actionable optimization plans for different memory pressure levels
             to ensure Clever maintains maximum cognitive capability under constraints.
        Where: Used by apply_optimization() to select appropriate strategy.
        How: Hierarchical strategies from abundant resources to critical pressure.
        """
        total_mb = self.baseline_memory_mb

        return [
            OptimizationStrategy(
                name="abundant",
                memory_threshold_mb=int(total_mb * 0.4),  # >40% available (1544MB+)
                actions=[
                    "enable_full_features",
                    "preload_models",
                    "enable_rich_ui",
                    "full_vscode_features",
                ],
                vscode_settings={
                    "python.analysis.memory.keepLibraryAst": True,
                    "python.analysis.indexing": True,
                    "typescript.suggest.enabled": True,
                    "editor.semanticHighlighting.enabled": True,
                    "workbench.editor.enablePreview": True,
                    "search.followSymlinks": True,
                },
                clever_config={
                    "max_conversation_history": 100,
                    "enable_context_memory": True,
                    "particle_count": 1000,
                    "nlp_models": ["full"],
                    "response_generation_depth": "deep",
                },
                intelligence_level="maximum",
                description="Full capabilities - abundant resources",
            ),
            OptimizationStrategy(
                name="balanced",
                memory_threshold_mb=int(total_mb * 0.25),  # >25% available (965MB+)
                actions=[
                    "optimize_vscode",
                    "selective_features",
                    "memory_conscious_ui",
                    "balanced_clever",
                ],
                vscode_settings={
                    "python.analysis.memory.keepLibraryAst": False,
                    "python.analysis.indexing": False,
                    "typescript.suggest.enabled": True,
                    "editor.semanticHighlighting.enabled": False,
                    "workbench.editor.enablePreview": False,
                    "search.followSymlinks": False,
                    "python.analysis.autoImportCompletions": False,
                },
                clever_config={
                    "max_conversation_history": 50,
                    "enable_context_memory": True,
                    "particle_count": 500,
                    "nlp_models": ["essential"],
                    "response_generation_depth": "balanced",
                },
                intelligence_level="high",
                description="Optimized for current constraints",
            ),
            OptimizationStrategy(
                name="aggressive",
                memory_threshold_mb=int(total_mb * 0.15),  # >15% available (579MB+)
                actions=[
                    "disable_heavy_vscode_features",
                    "minimal_clever_memory",
                    "reduce_ui_complexity",
                    "aggressive_gc",
                ],
                vscode_settings={
                    "python.analysis.memory.keepLibraryAst": False,
                    "python.analysis.indexing": False,
                    "typescript.suggest.enabled": False,
                    "editor.semanticHighlighting.enabled": False,
                    "workbench.editor.enablePreview": False,
                    "search.followSymlinks": False,
                    "python.analysis.autoImportCompletions": False,
                    "python.analysis.diagnosticMode": "workspace",
                    "extensions.autoUpdate": False,
                    "telemetry.telemetryLevel": "off",
                },
                clever_config={
                    "max_conversation_history": 20,
                    "enable_context_memory": False,
                    "particle_count": 200,
                    "nlp_models": ["minimal"],
                    "response_generation_depth": "quick",
                    "aggressive_memory_cleanup": True,
                },
                intelligence_level="adaptive",
                description="Aggressive optimization under pressure",
            ),
            OptimizationStrategy(
                name="emergency",
                memory_threshold_mb=int(total_mb * 0.08),  # >8% available (309MB+)
                actions=[
                    "emergency_vscode_optimization",
                    "minimal_clever_operation",
                    "emergency_memory_management",
                    "disable_non_essential_features",
                ],
                vscode_settings={
                    "python.analysis.memory.keepLibraryAst": False,
                    "python.analysis.indexing": False,
                    "python.analysis.autoSearchPaths": False,
                    "typescript.suggest.enabled": False,
                    "javascript.suggest.enabled": False,
                    "editor.semanticHighlighting.enabled": False,
                    "workbench.editor.enablePreview": False,
                    "search.followSymlinks": False,
                    "python.analysis.autoImportCompletions": False,
                    "python.analysis.diagnosticMode": "off",
                    "extensions.autoUpdate": False,
                    "telemetry.telemetryLevel": "off",
                    "workbench.settings.enableNaturalLanguageSearch": False,
                    "editor.hover.enabled": False,
                },
                clever_config={
                    "max_conversation_history": 5,
                    "enable_context_memory": False,
                    "particle_count": 50,
                    "nlp_models": ["none"],
                    "response_generation_depth": "minimal",
                    "aggressive_memory_cleanup": True,
                    "emergency_mode": True,
                },
                intelligence_level="survival",
                description="Emergency mode - minimal viable operation",
            ),
        ]

    def get_hardware_profile(self, force_refresh: bool = False) -> HardwareProfile:
        """
        Get comprehensive hardware profile with intelligent caching.

        Why: Provides real-time hardware state for optimization decisions while
             minimizing performance overhead through intelligent caching.
        Where: Called by optimization routines to assess current system state.
        How: Cached hardware monitoring with configurable refresh intervals.

        Args:
            force_refresh: Force profile refresh regardless of cache

        Returns:
            HardwareProfile with current system state
        """
        current_time = time.time()

        # Use cached profile if recent and not forced
        if (
            not force_refresh
            and self._cached_profile
            and current_time - self._last_profile_time < self._profile_cache_seconds
        ):
            return self._cached_profile

        # Get memory information
        memory = psutil.virtual_memory()
        total_mb = memory.total / (1024 * 1024)
        available_mb = memory.available / (1024 * 1024)
        free_mb = memory.free / (1024 * 1024)

        # Determine memory pressure level
        available_percent = (available_mb / total_mb) * 100
        if available_percent > 40:
            pressure_level = "low"
            optimization_level = "maximum"
        elif available_percent > 25:
            pressure_level = "medium"
            optimization_level = "balanced"
        elif available_percent > 15:
            pressure_level = "high"
            optimization_level = "aggressive"
        else:
            pressure_level = "critical"
            optimization_level = "emergency"

        # Get CPU information
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=0.1)

        # Get disk information
        disk = psutil.disk_usage("/")
        disk_free_gb = disk.free / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)

        # Estimate VS Code memory usage
        vscode_memory_mb = self._get_vscode_memory_usage()

        # Estimate Clever memory usage
        clever_memory_mb = self._get_clever_memory_usage()

        profile = HardwareProfile(
            total_memory_mb=int(total_mb),
            available_memory_mb=int(available_mb),
            free_memory_mb=int(free_mb),
            memory_pressure_level=pressure_level,
            cpu_count=cpu_count or 1,
            cpu_usage_percent=cpu_usage,
            disk_free_gb=disk_free_gb,
            disk_total_gb=disk_total_gb,
            vscode_memory_mb=vscode_memory_mb,
            clever_memory_mb=clever_memory_mb,
            optimization_level=optimization_level,
        )

        # Cache the profile
        self._cached_profile = profile
        self._last_profile_time = current_time

        self.debugger.info(
            "hardware_optimizer",
            f"Hardware profile: {available_mb:.0f}MB available, "
            f"pressure={pressure_level}, optimization={optimization_level}",
        )

        return profile

    def _get_vscode_memory_usage(self) -> int:
        """
        Estimate VS Code memory usage across all processes.

        Why: Understanding VS Code memory consumption enables intelligent optimization
             decisions for symbiotic operation with Clever.
        Where: Called by get_hardware_profile() for resource allocation planning.
        How: Process monitoring and memory summation with error handling.

        Returns:
            Estimated VS Code memory usage in MB
        """
        try:
            # Get all processes with 'code' in name
            total_memory_kb = 0
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                try:
                    proc_info = proc.info
                    if "code" in proc_info["name"].lower():
                        memory_kb = proc_info["memory_info"].rss / 1024
                        total_memory_kb += memory_kb
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return int(total_memory_kb / 1024)  # Convert to MB

        except Exception as e:
            self.debugger.error("hardware_optimizer", f"VS Code memory check failed: {e}")
            return 800  # Reasonable estimate

    def _get_clever_memory_usage(self) -> int:
        """
        Estimate Clever's current memory usage.

        Why: Understanding Clever's memory footprint enables optimization decisions
             and resource allocation for maximum cognitive capabilities.
        Where: Called by get_hardware_profile() for system resource tracking.
        How: Process monitoring for Python processes and memory estimation.

        Returns:
            Estimated Clever memory usage in MB
        """
        try:
            current_process = psutil.Process()
            memory_mb = current_process.memory_info().rss / (1024 * 1024)
            return int(memory_mb)
        except Exception as e:
            self.debugger.error("hardware_optimizer", f"Clever memory check failed: {e}")
            return 100  # Reasonable estimate

    def get_optimal_strategy(self) -> OptimizationStrategy:
        """
        Determine optimal optimization strategy based on current hardware state.

        Why: Selects the most appropriate optimization approach for current memory
             pressure to maximize Clever's cognitive capabilities within constraints.
        Where: Called by apply_optimization() to implement hardware-aware settings.
        How: Hardware profile analysis with strategy threshold matching.

        Returns:
            OptimizationStrategy best suited for current conditions
        """
        profile = self.get_hardware_profile()
        available_mb = profile.available_memory_mb

        # Find the most appropriate strategy
        for strategy in self.strategies:
            if available_mb >= strategy.memory_threshold_mb:
                return strategy

        # If no strategy matches, use emergency mode
        return self.strategies[-1]

    def apply_optimization(self) -> Dict[str, Any]:
        """
        Apply comprehensive hardware-aware optimization.

        Why: Implements intelligent resource management to transform memory constraints
             into competitive advantages for Clever's cognitive capabilities.
        Where: Called at startup and during memory pressure events.
        How: Multi-layered optimization affecting VS Code, Clever config, and system.

        Returns:
            Dict with optimization results and applied settings
        """
        profile = self.get_hardware_profile(force_refresh=True)
        strategy = self.get_optimal_strategy()

        results = {
            "timestamp": time.time(),
            "hardware_profile": profile.to_dict(),
            "strategy_applied": strategy.name,
            "intelligence_level": strategy.intelligence_level,
            "optimizations": [],
            "vscode_optimized": False,
            "clever_optimized": False,
            "memory_before_mb": profile.available_memory_mb,
            "memory_after_mb": None,
        }

        self.debugger.info(
            "hardware_optimizer",
            f"Applying {strategy.name} strategy " f"(intelligence: {strategy.intelligence_level})",
        )

        # Apply VS Code optimizations
        try:
            vscode_result = self._optimize_vscode(strategy)
            results["vscode_optimized"] = vscode_result
            if vscode_result:
                results["optimizations"].append("vscode_settings")
        except Exception as e:
            self.debugger.error("hardware_optimizer", f"VS Code optimization failed: {e}")

        # Apply Clever optimizations
        try:
            clever_result = self._optimize_clever_config(strategy)
            results["clever_optimized"] = clever_result
            if clever_result:
                results["optimizations"].append("clever_config")
        except Exception as e:
            self.debugger.error("hardware_optimizer", f"Clever optimization failed: {e}")

        # Apply system-level optimizations
        try:
            system_result = self._apply_system_optimizations(strategy)
            if system_result:
                results["optimizations"].append("system_level")
        except Exception as e:
            self.debugger.error("hardware_optimizer", f"System optimization failed: {e}")

        # Force garbage collection if aggressive or emergency mode
        if strategy.name in ["aggressive", "emergency"]:
            gc.collect()
            results["optimizations"].append("garbage_collection")

        # Get updated memory state
        time.sleep(1)  # Allow optimizations to take effect
        updated_profile = self.get_hardware_profile(force_refresh=True)
        results["memory_after_mb"] = updated_profile.available_memory_mb

        memory_improvement = updated_profile.available_memory_mb - profile.available_memory_mb

        self.debugger.info(
            "hardware_optimizer",
            f"Optimization complete: {memory_improvement:+.0f}MB change, "
            f"now {updated_profile.available_memory_mb:.0f}MB available",
        )

        return results

    def _optimize_vscode(self, strategy: OptimizationStrategy) -> bool:
        """
        Apply VS Code optimizations for memory efficiency.

        Why: VS Code consumes significant memory; intelligent optimization creates
             symbiotic relationship where both Clever and VS Code operate efficiently.
        Where: Called by apply_optimization() for VS Code resource management.
        How: Settings.json modification with memory-conscious configurations.

        Args:
            strategy: OptimizationStrategy with VS Code settings

        Returns:
            True if optimization applied successfully
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_settings_path.parent.mkdir(exist_ok=True)

            # Load existing settings or create new
            existing_settings = {}
            if self.vscode_settings_path.exists():
                try:
                    with open(self.vscode_settings_path, "r") as f:
                        existing_settings = json.load(f)
                except json.JSONDecodeError:
                    self.debugger.warning(
                        "hardware_optimizer", "Invalid VS Code settings JSON, resetting"
                    )

            # Merge with optimization settings
            optimized_settings = {**existing_settings, **strategy.vscode_settings}

            # Add hardware-specific optimizations
            optimized_settings.update(
                {
                    # Memory optimizations
                    "files.watcherExclude": {
                        "**/.git/objects/**": True,
                        "**/.git/subtree-cache/**": True,
                        "**/node_modules/**": True,
                        "**/.venv/**": True,
                        "**/venv/**": True,
                    },
                    "search.exclude": {
                        "**/node_modules": True,
                        "**/bower_components": True,
                        "**/.venv": True,
                        "**/venv": True,
                        "**/.git": True,
                    },
                    # Performance optimizations
                    "editor.largeFileOptimizations": True,
                    "editor.maxTokenizationLineLength": 20000,
                    "diffEditor.maxComputationTime": 5000,
                    # Hardware-specific limits
                    "terminal.integrated.persistentSessionReviveProcess": "never",
                    "workbench.editor.limit.enabled": True,
                    "workbench.editor.limit.value": 10,
                    # Clever-specific optimizations
                    "python.defaultInterpreterPath": "./.venv/bin/python",
                    "python.analysis.stubPath": "./.venv/lib/python3.12/site-packages",
                }
            )

            # Write optimized settings
            with open(self.vscode_settings_path, "w") as f:
                json.dump(optimized_settings, f, indent=2)

            self.debugger.info(
                "hardware_optimizer",
                f"Applied VS Code {strategy.name} optimization settings",
            )
            return True

        except Exception as e:
            self.debugger.error("hardware_optimizer", f"VS Code optimization failed: {e}")
            return False

    def _optimize_clever_config(self, strategy: OptimizationStrategy) -> bool:
        """
        Apply Clever-specific optimizations based on memory pressure.

        Why: Adapts Clever's cognitive capabilities to available memory, ensuring
             maximum intelligence within hardware constraints.
        Where: Called by apply_optimization() for Clever memory management.
        How: Dynamic configuration adjustment with memory-conscious parameters.

        Args:
            strategy: OptimizationStrategy with Clever settings

        Returns:
            True if optimization applied successfully
        """
        try:
            # Create hardware-aware config file
            config_path = self.root_dir / "hardware_config.json"

            hardware_config = {
                "strategy_name": strategy.name,
                "intelligence_level": strategy.intelligence_level,
                "timestamp": time.time(),
                "clever_settings": strategy.clever_config,
                "hardware_profile": self.get_hardware_profile().to_dict(),
            }

            with open(config_path, "w") as f:
                json.dump(hardware_config, f, indent=2)

            # Set environment variables for immediate effect
            for key, value in strategy.clever_config.items():
                env_key = f"CLEVER_{key.upper()}"
                os.environ[env_key] = str(value)

            self.debugger.info(
                "hardware_optimizer", f"Applied Clever {strategy.name} configuration"
            )
            return True

        except Exception as e:
            self.debugger.error("hardware_optimizer", f"Clever config optimization failed: {e}")
            return False

    def _apply_system_optimizations(self, strategy: OptimizationStrategy) -> bool:
        """
        Apply system-level memory optimizations.

        Why: System-level optimizations free additional memory for Clever's cognitive
             operations through intelligent resource management.
        Where: Called by apply_optimization() for system resource optimization.
        How: Process optimization and memory cleanup with error handling.

        Args:
            strategy: OptimizationStrategy with system actions

        Returns:
            True if optimizations applied successfully
        """
        try:
            optimizations_applied = 0

            # Aggressive garbage collection
            if "aggressive_gc" in strategy.actions:
                gc.collect()
                optimizations_applied += 1

            # Emergency memory management
            if "emergency_memory_management" in strategy.actions:
                # Force Python garbage collection with all generations
                for _ in range(3):
                    gc.collect()

                # Clear caches if possible
                if hasattr(sys, "_clear_type_cache"):
                    sys._clear_type_cache()

                optimizations_applied += 1

            self.debugger.info(
                "hardware_optimizer",
                f"Applied {optimizations_applied} system optimizations",
            )
            return optimizations_applied > 0

        except Exception as e:
            self.debugger.error("hardware_optimizer", f"System optimization failed: {e}")
            return False

    @contextmanager
    def memory_monitoring_context(self, operation_name: str = "operation"):
        """
        Context manager for monitoring memory usage during operations.

        Why: Provides intelligent memory tracking for operations to identify
             optimization opportunities and ensure memory-conscious development.
        Where: Used around memory-intensive operations for monitoring.
        How: Before/after memory measurement with automated reporting.

        Args:
            operation_name: Description of the operation being monitored

        Yields:
            HardwareProfile at operation start
        """
        start_profile = self.get_hardware_profile(force_refresh=True)
        start_time = time.time()

        self.debugger.info(
            "hardware_optimizer",
            f"Starting {operation_name}: " f"{start_profile.available_memory_mb:.0f}MB available",
        )

        try:
            yield start_profile
        finally:
            end_time = time.time()
            end_profile = self.get_hardware_profile(force_refresh=True)

            memory_change = end_profile.available_memory_mb - start_profile.available_memory_mb
            duration = end_time - start_time

            self.debugger.info(
                "hardware_optimizer",
                f"Completed {operation_name}: "
                f"{memory_change:+.0f}MB change in {duration:.2f}s, "
                f"{end_profile.available_memory_mb:.0f}MB available",
            )

    def monitor_and_optimize_continuously(self, check_interval: int = 30) -> None:
        """
        Continuous memory monitoring with automatic optimization.

        Why: Maintains optimal system performance through proactive memory management
             and adaptive optimization based on changing conditions.
        Where: Can be run as background process for continuous optimization.
        How: Periodic hardware monitoring with automatic optimization triggers.

        Args:
            check_interval: Seconds between monitoring checks
        """
        self.debugger.info(
            "hardware_optimizer",
            f"Starting continuous monitoring (interval: {check_interval}s)",
        )

        last_optimization_time = 0
        min_optimization_interval = 120  # Don't optimize more than every 2 minutes

        try:
            while True:
                profile = self.get_hardware_profile(force_refresh=True)
                current_time = time.time()

                # Check if optimization is needed
                need_optimization = (
                    profile.memory_pressure_level in ["high", "critical"]
                    or profile.available_memory_mb < 400  # Less than 400MB available
                )

                # Apply optimization if needed and enough time has passed
                if (
                    need_optimization
                    and current_time - last_optimization_time > min_optimization_interval
                ):

                    self.debugger.warning(
                        "hardware_optimizer",
                        f"Memory pressure detected: {profile.memory_pressure_level}, "
                        f"{profile.available_memory_mb:.0f}MB available",
                    )

                    optimization_result = self.apply_optimization()
                    last_optimization_time = current_time

                    self.debugger.info(
                        "hardware_optimizer",
                        f"Auto-optimization applied: {optimization_result['strategy_applied']}",
                    )

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.debugger.info("hardware_optimizer", "Continuous monitoring stopped")
        except Exception as e:
            self.debugger.error("hardware_optimizer", f"Monitoring error: {e}")


# Global optimizer instance
_hardware_optimizer = None


def get_hardware_optimizer() -> HardwareOptimizer:
    """
    Get global hardware optimizer instance.

    Why: Provides singleton access to hardware optimization capabilities across
         the Clever ecosystem for consistent resource management.
    Where: Called by modules needing hardware-aware configuration and optimization.
    How: Lazy initialization with global instance caching.

    Returns:
        HardwareOptimizer instance for system optimization
    """
    global _hardware_optimizer
    if _hardware_optimizer is None:
        _hardware_optimizer = HardwareOptimizer()
    return _hardware_optimizer


def apply_hardware_optimization() -> Dict[str, Any]:
    """
    Apply hardware optimization using global optimizer.

    Why: Convenient function for applying hardware optimization without
         managing optimizer instance lifecycle.
    Where: Called by startup scripts and optimization triggers.
    How: Uses global optimizer instance to apply current optimal strategy.

    Returns:
        Dict with optimization results
    """
    optimizer = get_hardware_optimizer()
    return optimizer.apply_optimization()


def get_current_hardware_profile() -> HardwareProfile:
    """
    Get current hardware profile using global optimizer.

    Why: Convenient access to hardware state for optimization decisions
         throughout the Clever ecosystem.
    Where: Called by modules needing current hardware information.
    How: Uses global optimizer instance with intelligent caching.

    Returns:
        HardwareProfile with current system state
    """
    optimizer = get_hardware_optimizer()
    return optimizer.get_hardware_profile()


if __name__ == "__main__":
    """
    Command-line interface for hardware optimization.

    Usage:
        python hardware_optimizer.py                    # Apply optimization once
        python hardware_optimizer.py --monitor         # Continuous monitoring
        python hardware_optimizer.py --profile         # Show hardware profile
        python hardware_optimizer.py --strategies      # Show available strategies
    """
    import argparse

    parser = argparse.ArgumentParser(description="Hardware-aware optimization for Clever")
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Run continuous monitoring and optimization",
    )
    parser.add_argument("--profile", action="store_true", help="Show current hardware profile")
    parser.add_argument(
        "--strategies",
        action="store_true",
        help="Show available optimization strategies",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitoring interval in seconds (default: 30)",
    )

    args = parser.parse_args()

    optimizer = get_hardware_optimizer()

    if args.profile:
        profile = optimizer.get_hardware_profile()
        print("\n🖥️  Hardware Profile:")
        print(
            f"   Memory: {profile.available_memory_mb:.0f}MB available / {profile.total_memory_mb:.0f}MB total"
        )
        print(f"   Pressure: {profile.memory_pressure_level}")
        print(f"   CPU: {profile.cpu_usage_percent:.1f}% usage ({profile.cpu_count} cores)")
        print(f"   Disk: {profile.disk_free_gb:.1f}GB free / {profile.disk_total_gb:.1f}GB total")
        print(f"   VS Code: {profile.vscode_memory_mb:.0f}MB")
        print(f"   Clever: {profile.clever_memory_mb:.0f}MB")
        print(f"   Optimization Level: {profile.optimization_level}")

    elif args.strategies:
        print("\n🔧 Available Optimization Strategies:")
        for strategy in optimizer.strategies:
            print(f"   {strategy.name.title()}: {strategy.description}")
            print(f"      Threshold: {strategy.memory_threshold_mb}MB+")
            print(f"      Intelligence: {strategy.intelligence_level}")
            print()

    elif args.monitor:
        optimizer.monitor_and_optimize_continuously(args.interval)

    else:
        # Apply optimization once
        result = optimizer.apply_optimization()
        print(f"\n✅ Applied {result['strategy_applied']} optimization")
        print(f"   Intelligence Level: {result['intelligence_level']}")
        print(f"   Memory Change: {result['memory_after_mb'] - result['memory_before_mb']:+.0f}MB")
        print(f"   Available: {result['memory_after_mb']:.0f}MB")
        print(f"   Optimizations: {', '.join(result['optimizations'])}")
