#!/usr/bin/env python3
from __future__ import annotations

"""clever_memory_manager.py - Comprehensive memory management for Clever.

Why: Provides unified memory and process oversight for Clever's development environment,
     enabling adaptive optimization and emergency interventions when system pressure
     threatens performance.
Where: Central memory management component that integrates with development tools,
       VS Code optimization, and Clever's monitoring/health systems.
How: Uses psutil to inspect memory state, applies tiered optimization strategies,
     and records optimization history for self-aware optimization behavior.

File Usage:
    - Called by: development scripts, manual command-line invocation, health monitors
    - Calls to: vscode_memory_optimizer.py, emergency_memory_stabilizer.py, system tools
    - Data flow: system state → assessment → optimization action → history capture
    - Configuration: threshold parameters are defined in this file for local tuning
    - Database interactions: optional history can be extended to log strategies

Connects to:
    - emergency_memory_stabilizer.py: emergency response actions
    - vscode_memory_optimizer.py: VS Code-specific memory tuning
    - development_environment_optimizer.py: broader environment optimization
    - debug_config.py: logging and debugging observability
    - config.py: threshold tuning and runtime configuration
    - database.py: optional persistence for optimization history
"""

import gc
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import psutil


class CleverMemoryManager:
    """
    Comprehensive memory management system for Clever development environment.

    Provides adaptive memory optimization with multiple intervention levels.
    """

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent

        # Memory thresholds in MB
        self.critical_threshold = 250  # Emergency intervention
        self.warning_threshold = 400  # Preventive optimization
        self.optimal_threshold = 600  # Normal operation

        # Monitoring state
        self.monitoring = False
        self.last_optimization = None
        self.optimization_history = []

        # Component managers
        self.emergency_stabilizer = None
        self.vscode_optimizer = None

    def get_system_memory(self) -> Dict[str, Any]:
        """Return system-level memory statistics using psutil."""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total_mb": int(vm.total // 1024 // 1024),
            "used_mb": int(vm.used // 1024 // 1024),
            "free_mb": int(vm.free // 1024 // 1024),
            "available_mb": int(vm.available // 1024 // 1024),
            "swap_total_mb": int(swap.total // 1024 // 1024),
            "swap_used_mb": int(swap.used // 1024 // 1024),
            "timestamp": datetime.now(),
        }

    def get_process_memory(self) -> Dict[str, int]:
        """Return memory usage for key development processes."""
        processes = {"vscode": 0, "python": 0}

        for proc in psutil.process_iter(["name", "cmdline", "memory_info"]):
            try:
                name = (proc.info.get("name") or "").lower()
                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                rss = proc.info.get("memory_info").rss if proc.info.get("memory_info") else 0
                mem_mb = int(rss // 1024)

                if "code" in name or "code" in cmdline or "visual studio code" in cmdline:
                    processes["vscode"] += mem_mb
                if "python" in name or "python" in cmdline:
                    processes["python"] += mem_mb
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def assess_memory_situation(self) -> Dict[str, Any]:
        """Assess current memory state and decide the correct intervention level."""
        memory = self.get_system_memory()
        processes = self.get_process_memory()
        available = memory["available_mb"]

        if available < self.critical_threshold:
            pressure_level = "critical"
            intervention = "emergency"
        elif available < self.warning_threshold:
            pressure_level = "warning"
            intervention = "preventive"
        elif available < self.optimal_threshold:
            pressure_level = "moderate"
            intervention = "gentle"
        else:
            pressure_level = "normal"
            intervention = "none"

        return {
            "memory": memory,
            "processes": processes,
            "pressure_level": pressure_level,
            "intervention_needed": intervention,
            "available_mb": available,
        }

    def apply_gentle_optimization(self) -> List[str]:
        """Apply gentle memory optimizations that are safe and low-risk."""
        actions: List[str] = []
        print("💚 Applying gentle memory optimizations...")

        try:
            cache_dirs = list(self.base_path.rglob("__pycache__"))
            for cache_dir in cache_dirs:
                subprocess.run(["rm", "-rf", str(cache_dir)], check=False)
            if cache_dirs:
                actions.append(f"Cleared {len(cache_dirs)} Python cache dirs")
        except Exception:
            pass

        try:
            from vscode_memory_optimizer import VSCodeMemoryOptimizer

            optimizer = VSCodeMemoryOptimizer()
            if optimizer.optimize_for_current_memory():
                actions.append("VS Code settings optimized")
        except Exception:
            pass

        try:
            collected = gc.collect()
            if collected > 0:
                actions.append(f"Python GC collected {collected} objects")
        except Exception:
            pass

        print(f"✅ Gentle optimization: {', '.join(actions)}")
        return actions

    def apply_preventive_optimization(self) -> List[str]:
        """Apply preventive optimizations before memory pressure becomes critical."""
        actions = self.apply_gentle_optimization()
        print("🟡 Applying preventive memory optimizations...")

        try:
            subprocess.run(["sudo", "sync"], check=False)
            subprocess.run(["sudo", "sh", "-c", "echo 1 > /proc/sys/vm/drop_caches"], check=False)
            actions.append("System caches cleared")
        except Exception:
            pass

        try:
            subprocess.run(["pkill", "-f", "chrome.*renderer"], check=False)
            actions.append("Chrome renderers restarted")
        except Exception:
            pass

        try:
            from vscode_memory_optimizer import VSCodeMemoryOptimizer

            optimizer = VSCodeMemoryOptimizer()
            optimizer.optimize_clever_workspace()
            actions.append("VS Code workspace optimized")
        except Exception:
            pass

        print(f"✅ Preventive optimization: {', '.join(actions)}")
        return actions

    def apply_emergency_optimization(self) -> List[str]:
        """Apply emergency optimization actions under critical memory pressure."""
        actions = self.apply_preventive_optimization()
        print("🔴 Applying EMERGENCY memory optimizations!")

        try:
            subprocess.run(["pkill", "-f", "pylance"], check=False)
            actions.append("Pylance restarted")
        except Exception:
            pass

        try:
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                    pid = proc.info.get("pid")
                    if (
                        pid
                        and "python" in name
                        and "flask" not in cmdline
                        and "5000" not in cmdline
                    ):
                        subprocess.run(["kill", str(pid)], check=False)
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue
            actions.append("Non-essential Python processes killed")
        except Exception:
            pass

        try:
            subprocess.run(["sudo", "sync"], check=False)
            subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"], check=False)
            actions.append("Aggressive system cache clear")
        except Exception:
            pass

        print(f"🚨 EMERGENCY optimization: {', '.join(actions)}")
        return actions

    def optimize_memory(self, force_level: str | None = None) -> List[str]:
        """Optimize memory based on current situation or a forced intervention level."""
        situation = self.assess_memory_situation()
        intervention = force_level if force_level else situation["intervention_needed"]

        print(
            f"🧠 Memory Assessment: {situation['available_mb']}MB available ({situation['pressure_level']})"
        )

        if intervention == "emergency":
            actions = self.apply_emergency_optimization()
        elif intervention == "preventive":
            actions = self.apply_preventive_optimization()
        elif intervention == "gentle":
            actions = self.apply_gentle_optimization()
        else:
            actions = []
            print("✅ Memory situation is optimal - no intervention needed")

        if actions:
            optimization_event = {
                "timestamp": datetime.now(),
                "pressure_level": situation["pressure_level"],
                "intervention": intervention,
                "actions": actions,
                "memory_before": situation["memory"]["available_mb"],
            }
            self.optimization_history.append(optimization_event)
            self.last_optimization = datetime.now()

        return actions

    def start_continuous_monitoring(self, interval: int = 30) -> None:
        """Begin continuous memory monitoring and trigger optimization as needed."""
        self.monitoring = True
        print(f"🔍 Starting Clever memory monitoring (check every {interval}s)")

        self._last_status_time = datetime.now()
        while self.monitoring:
            try:
                situation = self.assess_memory_situation()
                elapsed = datetime.now() - self._last_status_time

                if situation["pressure_level"] != "normal" or elapsed.total_seconds() > 120:
                    print(
                        f"💾 {situation['available_mb']}MB available | Pressure: {situation['pressure_level']}"
                    )
                    self._last_status_time = datetime.now()

                if situation["intervention_needed"] != "none":
                    if (
                        not self.last_optimization
                        or datetime.now() - self.last_optimization > timedelta(minutes=5)
                    ):
                        self.optimize_memory()

                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n🛑 Memory monitoring stopped")
                self.monitoring = False
                break
            except Exception:
                print("Error occurred during monitoring")
                time.sleep(interval)

    def get_status_report(self) -> Dict[str, Any]:
        """Return current memory status and recent optimization history."""
        situation = self.assess_memory_situation()
        return {
            "current_memory": situation,
            "monitoring_active": self.monitoring,
            "last_optimization": (
                self.last_optimization.isoformat() if self.last_optimization else None
            ),
            "optimization_count": len(self.optimization_history),
            "recent_optimizations": [
                {
                    "timestamp": event["timestamp"].isoformat(),
                    "pressure_level": event["pressure_level"],
                    "intervention": event["intervention"],
                    "actions_count": len(event["actions"]),
                }
                for event in self.optimization_history[-5:]
            ],
        }


def main() -> None:
    """Main memory management entry point."""
    manager = CleverMemoryManager()
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            status = manager.get_status_report()
            print("🧠 CLEVER MEMORY MANAGER STATUS")
            print("=" * 40)
            print(f"Available Memory: {status['current_memory']['available_mb']}MB")
            print(f"Pressure Level: {status['current_memory']['pressure_level']}")
            print(f"Monitoring Active: {status['monitoring_active']}")
            print(f"Total Optimizations: {status['optimization_count']}")
        elif command == "optimize":
            force_level = sys.argv[2] if len(sys.argv) > 2 else None
            actions = manager.optimize_memory(force_level)
            print(f"✅ Optimization complete: {len(actions)} actions applied")

        elif command == "monitor":
            manager.start_continuous_monitoring()

        elif command == "emergency":
            print("🚨 EMERGENCY MEMORY OPTIMIZATION")
            actions = manager.apply_emergency_optimization()
            print(f"✅ Emergency optimization complete: {len(actions)} actions applied")

        else:
            print("Usage: python3 clever_memory_manager.py [status|optimize|monitor|emergency]")

    else:
        actions = manager.optimize_memory()
        print(f"✅ Memory optimization complete: {len(actions)} actions applied")


if __name__ == "__main__":
    main()
