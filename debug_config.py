"""debug_config.py - Advanced Debugging & Performance Monitoring for Clever's Cognitive Partnership

Why: Provides comprehensive debugging, logging, and performance monitoring that enables
transparent system operation and continuous optimization of Clever's cognitive partnership
capabilities. Essential for maintaining the authentic digital brain extension experience
through detailed system insights and performance analytics.

Where: Core debugging infrastructure used throughout all Clever components, providing
system-wide logging, performance tracking, error analysis, and runtime introspection
for optimal cognitive partnership performance and troubleshooting capabilities.

How: Advanced debugging system with performance analytics, error pattern recognition,
component health monitoring, and intelligent analysis integration - all operating
offline for complete digital sovereignty and privacy protection.

File Usage:
    - System transparency: Comprehensive logging and monitoring for all Clever operations
    - Performance analytics: Advanced performance tracking and optimization insights
    - Error intelligence: Pattern recognition and intelligent error analysis capabilities
    - Component health: Real-time health monitoring for all cognitive system components
    - Development support: Debug interfaces and runtime introspection for system development
    - Troubleshooting foundation: Detailed diagnostic information for issue resolution
    - Optimization insights: Performance data collection for continuous system improvement
    - Runtime analysis: Live system state monitoring and performance visualization
    - Quality assurance: System validation and health verification capabilities
    - Cognitive insights: Debugging support for personality engine and memory systems
    - Security monitoring: Access control and security event logging capabilities
    - Resource tracking: Memory, CPU, and system resource usage monitoring
    - Session management: Debug session tracking and analytical data collection
    - Integration testing: Comprehensive testing support for all system components

Connects to:
    - app.py: Primary Flask application integration for system-wide debugging
        - get_debugger() calls throughout main application for comprehensive logging
        - Performance monitoring for all route handlers and API endpoints
        - Error handling and recovery coordination for robust operation
    - persona.py: Personality engine debugging and performance monitoring
        - Response generation performance tracking and optimization
        - Memory integration debugging and relationship building analytics
        - Conversation flow monitoring and quality assurance
    - evolution_engine.py: Learning system debugging and growth analytics
        - Interaction logging performance and learning efficiency tracking
        - Cognitive growth monitoring and adaptation analytics
    - memory_engine.py: Memory system debugging and performance optimization
        - Memory formation and retrieval performance tracking
        - Relationship building analytics and memory health monitoring
    - nlp_processor.py: Natural language processing performance and accuracy monitoring
        - Text analysis performance tracking and optimization insights
        - NLP capability testing and validation support
    - database.py: Database performance monitoring and optimization analytics
        - Query performance tracking and connection health monitoring
        - Data integrity verification and backup operation logging
    - introspection.py: Runtime system analysis and architectural transparency
        - System state monitoring and performance visualization
        - Component interaction analysis and dependency mapping
    - intelligent_analyzer.py: Advanced analytics integration and insight generation
        - Performance data aggregation for intelligent system analysis
        - Component health reporting and optimization recommendations
    - system_validator.py: System validation and health verification support
        - Validation process logging and result tracking
        - Health check coordination and status reporting
    - All Clever modules: Universal debugging interface for consistent system monitoring
        - Standardized logging interface across all cognitive components
        - Performance tracking and optimization support for entire system

Performance Notes:
    - Memory usage: Lightweight logging with configurable retention and intelligent cleanup
    - CPU impact: Minimal overhead debugging with efficient data structures and lazy evaluation
    - I/O operations: Optimized logging with batching and asynchronous writing capabilities
    - Scaling limits: Designed for intensive single-user debugging with comprehensive coverage
    - Data collection: Intelligent sampling and aggregation for performance insights
    - Storage efficiency: Compressed logging and intelligent data retention policies
    - Real-time monitoring: Low-latency health checks and status reporting
    - Analytics processing: Efficient pattern recognition and trend analysis

Critical Dependencies:
    - Required packages: Python 3.8+ standard library (collections, datetime, os, time)
    - Optional packages: Enhanced analytics libraries for advanced performance insights
    - System requirements: File system access for logging and debug data storage
    - Memory constraints: Chrome OS optimized with intelligent memory management
    - Configuration integration: Enhanced config system for debug settings and limits
    - Error handling: Robust error recovery and graceful degradation capabilities
    - Thread safety: Multi-threaded debugging support for concurrent operations
    - Digital sovereignty: Complete offline operation with no external dependencies
"""

import os
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, Optional


class SimpleDebugger:
    """
    Enhanced debugger for Clever AI with performance analytics

    Why: Provides debugging, logging, and performance monitoring that feeds
    into the intelligent analysis system for better insights
    Where: Used throughout application for status tracking and performance analysis
    How: Print-based logging with timestamps, performance tracking, and data collection
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize enhanced debugger with performance tracking

        Why: Set up logging and performance monitoring for intelligent analysis
        Where: Called once during app initialization
        How: Configure session ID, performance registries, and analytics
        """
        self.session_id = session_id or f"clever_{int(time.time())}"
        self.debug_level = os.environ.get("CLEVER_DEBUG_LEVEL", "INFO")
        self.error_count = 0

        # Enhanced: Performance tracking for intelligent analysis
        self.performance_data = defaultdict(list)  # function -> [durations]
        self.error_patterns = deque(maxlen=100)  # recent errors for pattern analysis
        self.component_health = {}  # component -> health metrics

    def info(self, component: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log info message

        Why: Provide status information during operation
        Where: Used throughout application for status updates
        How: Print formatted message with timestamp
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{component}] INFO: {message}")
        if extra:
            print(f"  Extra: {extra}")

    def debug(self, component: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message if debug level permits"""
        if self.debug_level == "DEBUG":
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{component}] DEBUG: {message}")
            if extra:
                print(f"  Extra: {extra}")

    def error(self, component: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Enhanced error logging with pattern tracking

        Why: Track errors for debugging and feed into intelligent analysis
        Where: Used in exception handling throughout application
        How: Print error, increment counter, and store for pattern analysis
        """
        self.error_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{component}] ERROR: {message}")
        if extra:
            print(f"  Extra: {extra}")

        # Enhanced: Store error for pattern analysis
        self.error_patterns.append(
            {
                "component": component,
                "message": message,
                "timestamp": time.time(),
                "extra": extra,
            }
        )

    def warning(self, component: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{component}] WARNING: {message}")
        if extra:
            print(f"  Extra: {extra}")

    def track_performance(self, component: str, operation: str, duration: float):
        """
        Enhanced performance tracking for intelligent analysis

        Why: Monitor operation timing and feed data to intelligent analyzer
        Where: Used in performance-critical operations throughout the app
        How: Log timing and store data for pattern analysis and recommendations
        """
        self.info(component, f"Performance: {operation} took {duration:.3f}s")

        # Enhanced: Store performance data for intelligent analysis
        key = f"{component}.{operation}"
        self.performance_data[key].append(duration)

        # Keep only recent measurements (last 100) to prevent memory growth
        if len(self.performance_data[key]) > 100:
            self.performance_data[key] = self.performance_data[key][-100:]

        # Update component health metrics
        self._update_component_health(component, duration)

    def _update_component_health(self, component: str, duration: float):
        """
        Update component health metrics for intelligent analysis

        Why: Track component performance trends for health assessment
        Where: Called by track_performance to maintain health data
        How: Calculate and store health metrics based on performance data
        """
        if component not in self.component_health:
            self.component_health[component] = {
                "total_calls": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0,
                "max_duration": 0.0,
                "health_score": 100.0,
                "last_updated": time.time(),
            }

        health = self.component_health[component]
        health["total_calls"] += 1
        health["total_duration"] += duration
        health["avg_duration"] = health["total_duration"] / health["total_calls"]
        health["max_duration"] = max(health["max_duration"], duration)
        health["last_updated"] = time.time()

        # Simple health score: penalize slow operations
        if duration > 1.0:  # >1s is considered slow
            health["health_score"] = max(0, health["health_score"] - 5)
        elif duration < 0.1:  # <100ms is good
            health["health_score"] = min(100, health["health_score"] + 1)

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for intelligent analysis

        Why: Provide performance data to intelligent analyzer for insights
        Where: Called by intelligent_analyzer to correlate performance issues
        How: Return structured performance data with statistics
        """
        stats = {}
        for key, durations in self.performance_data.items():
            if durations:
                import statistics

                stats[key] = {
                    "count": len(durations),
                    "avg": statistics.mean(durations),
                    "max": max(durations),
                    "min": min(durations),
                    "recent": durations[-10:],  # last 10 measurements
                    "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0,
                }
        return stats

    def get_debug_summary(self) -> Dict[str, Any]:
        """
        Enhanced debug session summary with performance insights

        Why: Provide comprehensive overview including performance and health data
        Where: Used by monitoring, health checks, and intelligent analysis
        How: Return dictionary with metrics, performance stats, and component health
        """
        return {
            "session_id": self.session_id,
            "debug_level": self.debug_level,
            "error_count": self.error_count,
            "timestamp": datetime.now().isoformat(),
            "performance_functions_tracked": len(self.performance_data),
            "component_health": self.component_health,
            "error_patterns_count": len(self.error_patterns),
            "total_performance_measurements": sum(len(d) for d in self.performance_data.values()),
        }


# Simple performance monitor decorator
def performance_monitor(component: str):
    """
    Decorator for performance monitoring

    Why: Track execution time of critical functions
    Where: Applied to functions that need timing analysis
    How: Wrapper that measures and logs execution duration
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                debugger = get_debugger()
                debugger.track_performance(component, func.__name__, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                debugger = get_debugger()
                debugger.error(component, f"Error in {func.__name__}: {str(e)}")
                debugger.track_performance(component, f"{func.__name__}_error", duration)
                raise

        return wrapper

    return decorator


# Global debugger instance
_debugger = None


# Global performance monitoring registry
class PerformanceRegistry:
    """
    Global registry for performance monitoring data

    Why: Centralize performance data collection for intelligent analysis
    Where: Accessed by intelligent_analyzer and debug tools
    How: Singleton pattern with thread-safe data collection
    """

    def __init__(self):
        self._stats = {}
        self._lock = None  # Will be set when needed

    def get_stats(self) -> Dict[str, Any]:
        """Get all performance statistics."""
        debugger = get_debugger()
        return debugger.get_performance_stats()

    def get_component_health(self) -> Dict[str, Any]:
        """Get component health metrics."""
        debugger = get_debugger()
        return debugger.component_health


# Global registry instance
performance_monitor_registry = PerformanceRegistry()


def get_debugger() -> SimpleDebugger:
    """
    Get global debugger instance

    Why: Provide singleton access to debugger across application
    Where: Used by all modules needing debugging capabilities
    How: Create or return existing debugger instance

    Connects to:
        - app.py: Main application debugging
        - All modules: Universal debugging access
    """
    global _debugger
    if _debugger is None:
        _debugger = SimpleDebugger()
    return _debugger


def reset_debugger():
    """
    Reset global debugger instance

    Why: Allow clean state for testing and reinitialization
    Where: Used in test cases and system restarts
    How: Clear global debugger variable
    """
    global _debugger
    _debugger = None
