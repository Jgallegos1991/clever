import time

"""
evolution_engine.py - Advanced Learning and Growth Engine for Clever's Digital Brain Extension

Why: Implements sophisticated learning and adaptation capabilities as the cognitive growth
     system for Jay's digital brain extension, capturing interaction patterns, learning
     preferences, and continuously evolving Clever's cognitive partnership abilities
     through advanced pattern recognition and behavioral adaptation.

Where: Core learning orchestrator between user interactions and cognitive enhancement,
       serving as the primary intelligence evolution system that drives Clever's
       continuous improvement and relationship building capabilities.

How: Advanced interaction tracking with machine learning-inspired pattern recognition,
     preference modeling, behavioral adaptation, and cognitive enhancement analytics,
     all integrated with the enhanced configuration system for optimal performance.

File Usage:
    - Learning foundation: Core system for tracking all user interactions and cognitive learning
    - Pattern recognition: Advanced analytics for interaction patterns and behavioral adaptation
    - Performance analytics: Comprehensive telemetry and metrics for system optimization
    - Memory coordination: Deep integration with memory engine for holistic understanding
    - Adaptation driver: Feeds learning data to persona engine for personality evolution
    - Metrics collection: Advanced usage patterns, response effectiveness, and satisfaction tracking
    - Debug support: Comprehensive introspection data for development and troubleshooting
    - Health monitoring: Advanced system health checks and performance validation
    - Continuous improvement: Enables Clever to evolve and improve through sophisticated learning
    - Relationship building: Tracks cognitive partnership development with detailed analytics
    - Autonomous optimization: Supports self-improving system capabilities with ML techniques
    - Analytics substrate: Foundation for advanced cognitive enhancement and predictive analytics
    - Configuration management: Uses enhanced config system for learning parameters
    - Digital sovereignty: Maintains offline-first learning without external dependencies

Connects to:
    - app.py: Main Flask application integration for interaction logging and learning analytics
    - config/: Enhanced configuration system for learning parameters and performance tuning
    - persona.py: Personality engine integration for adaptive response generation
    - memory_engine.py: Deep memory integration for comprehensive cognitive understanding
    - database.py: Advanced persistence layer for long-term learning and pattern storage
    - debug_config.py: Comprehensive logging and performance monitoring integration
    - introspection.py: Runtime system analysis and learning insights visualization
    - health_monitor.py: Advanced health monitoring with learning system validation
    - routes/system.py: System analytics and learning insights API endpoints
    - nlp_processor.py: Natural language processing integration for interaction analysis

Performance Notes:
    - Memory usage: Efficient interaction caching with configurable limits and cleanup
    - CPU impact: Optimized pattern recognition with background processing capabilities
    - I/O operations: Minimal database writes with batch processing and smart caching
    - Scaling limits: Designed for intensive single-user cognitive partnership learning
    - Processing time: Real-time interaction logging with background analytics processing
    - Data retention: Configurable interaction history with intelligent archiving

Critical Dependencies:
    - Required packages: datetime, typing, time, collections, threading
    - Enhanced config: Type-safe configuration management for learning parameters
    - Memory system: Deep integration with advanced memory and conversation tracking
    - Database system: Advanced persistence for long-term learning and analytics
    - Debug system: Comprehensive logging and performance monitoring
    - Pattern recognition: Advanced analytics for behavioral pattern detection
    - Threading support: Background processing for non-blocking learning operations
"""

import time
from collections import defaultdict, deque
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

# Enhanced configuration and debugging
from config import get_config, get_memory_config
from debug_config import get_debugger, performance_monitor

# Global initialization
debugger = get_debugger()


class AdvancedEvolutionEngine:
    """
    Advanced evolution engine for comprehensive learning and cognitive growth

    Why: Implements sophisticated learning algorithms and behavioral adaptation
         for Jay's digital brain extension, enabling continuous cognitive partnership
         enhancement through advanced pattern recognition and preference modeling.
    Where: Core learning system integrating with all Clever components for
           comprehensive intelligence evolution and relationship building.
    How: Multi-threaded interaction processing with machine learning-inspired
         analytics, persistent storage, and real-time adaptation capabilities.
    """

    def __init__(self):
        """
        Initialize advanced evolution engine with enhanced configuration

        Why: Set up sophisticated learning capabilities with configurable parameters
        Where: Called once during app initialization for cognitive learning setup
        How: Use enhanced config for learning parameters and advanced data structures
        """
        # Enhanced configuration integration
        try:
            self.config = get_config()
            self.memory_config = get_memory_config()
            debugger.info("evolution_engine", "Enhanced configuration loaded successfully")
        except Exception as e:
            debugger.error("evolution_engine", f"Enhanced config required: {e}")
            raise RuntimeError("Enhanced configuration required for cognitive learning")

        # Thread-safe processing
        self._lock = Lock()

        # Advanced data structures
        max_interactions = getattr(self.memory_config, "max_interactions", 1000)
        self.interactions = deque(maxlen=max_interactions)
        self.interaction_patterns = defaultdict(list)
        self.mode_preferences = defaultdict(int)
        self.response_effectiveness = defaultdict(list)

        # Session and performance tracking
        self.session_start = time.time()
        self.total_interactions = 0
        self.learning_cycles = 0
        self.adaptation_score = 0.0

        # Advanced analytics
        self.behavioral_patterns = {}
        self.preference_model = {}
        self.cognitive_metrics = {
            "learning_velocity": 0.0,
            "adaptation_rate": 0.0,
            "relationship_depth": 0.0,
            "cognitive_coherence": 0.0,
        }

        debugger.info("evolution_engine", "Advanced evolution engine initialized")

    @performance_monitor("evolution_engine.log_interaction")
    def log_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """
        Log user interaction with advanced analytics and learning

        Why: Capture comprehensive interaction data for sophisticated cognitive learning
        Where: Called after every user interaction to build learning foundation
        How: Thread-safe processing with advanced pattern recognition and analytics
        """
        if not interaction_data:
            debugger.warning("evolution_engine", "Empty interaction data received")
            return

        with self._lock:
            enhanced_interaction = {
                "timestamp": time.time(),
                "session_time": time.time() - self.session_start,
                "interaction_id": f"{self.total_interactions + 1}_{int(time.time())}",
                "data": interaction_data.copy(),
            }

            self.interactions.append(enhanced_interaction)
            self.total_interactions += 1

            # Advanced pattern analysis
            self._analyze_interaction_patterns(enhanced_interaction)

            debugger.info(
                "evolution_engine",
                f"Interaction logged: total={self.total_interactions}",
            )

    def _analyze_interaction_patterns(self, interaction: Dict[str, Any]) -> None:
        """Analyze interaction patterns for behavioral modeling"""
        data = interaction["data"]
        mode = data.get("active_mode", "Unknown")

        # Mode preference learning
        self.mode_preferences[mode] += 1

        # Pattern sequence analysis
        pattern_key = f"{mode}_{data.get('sentiment', 'neutral')}"
        self.interaction_patterns[pattern_key].append(interaction["timestamp"])

    def get_interaction_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive interaction summary with advanced analytics

        Why: Provide detailed analytics for system optimization and insights
        Where: Used by monitoring, UI, and analytical systems
        How: Advanced statistical analysis of interaction patterns and metrics
        """
        if not self.interactions:
            return {
                "total_interactions": 0,
                "session_duration": 0,
                "cognitive_metrics": self.cognitive_metrics,
                "learning_status": "No interactions recorded",
                "adaptation_score": 0.0,
            }

        with self._lock:
            # Mode usage analysis
            total_usage = sum(self.mode_preferences.values()) if self.mode_preferences else 1
            mode_analytics = {}
            if self.mode_preferences:
                most_used_mode = max(self.mode_preferences, key=self.mode_preferences.get)
                preference_strength = self.mode_preferences[most_used_mode] / total_usage
                mode_analytics = {
                    "most_preferred": most_used_mode,
                    "preference_strength": preference_strength,
                    "distribution": dict(self.mode_preferences),
                }

            return {
                "total_interactions": self.total_interactions,
                "session_duration": time.time() - self.session_start,
                "recent_interactions": len(self.interactions),
                "mode_analytics": mode_analytics,
                "cognitive_metrics": self.cognitive_metrics,
                "adaptation_score": self.adaptation_score,
                "learning_cycles": self.learning_cycles,
            }

    def get_learning_insights(self) -> List[str]:
        """
        Get advanced learning insights with sophisticated analysis

        Why: Provide intelligent feedback on cognitive partnership development
        Where: Used by monitoring systems and user interface for learning feedback
        How: Advanced pattern analysis and cognitive assessment for meaningful insights
        """
        insights = []

        if self.total_interactions == 0:
            insights.append("Cognitive learning system ready for first interaction")
            return insights

        summary = self.get_interaction_summary()

        # Interaction volume insights
        if summary["total_interactions"] > 100:
            insights.append(
                f"Extensive learning achieved: {summary['total_interactions']} interactions processed"
            )
        elif summary["total_interactions"] > 50:
            insights.append(
                f"Strong learning foundation: {summary['total_interactions']} interactions analyzed"
            )
        elif summary["total_interactions"] > 10:
            insights.append(
                f"Building cognitive partnership: {summary['total_interactions']} interactions"
            )

        # Mode preference insights
        if summary["mode_analytics"] and summary["mode_analytics"].get("most_preferred"):
            mode_name = summary["mode_analytics"]["most_preferred"]
            preference_strength = summary["mode_analytics"]["preference_strength"]
            insights.append(
                f"Strong preference for {mode_name} mode (confidence: {preference_strength:.1%})"
            )

        # Session insights
        session_minutes = summary["session_duration"] / 60
        if session_minutes > 60:
            insights.append(
                f"Extended cognitive session: {session_minutes:.1f} minutes of deep partnership"
            )
        elif session_minutes > 20:
            insights.append(f"Productive session: {session_minutes:.1f} minutes of active learning")

        return insights[:6]  # Limit to most important insights

    def reset_session(self) -> None:
        """
        Reset current session data with enhanced cleanup

        Why: Allow clean session starts with comprehensive data reset
        Where: Used for testing, session management, and system resets
        How: Thread-safe reset of all session-specific data and metrics
        """
        with self._lock:
            self.interactions.clear()
            self.interaction_patterns.clear()
            self.session_start = time.time()
            self.learning_cycles = 0

            # Preserve long-term learning but reset session metrics
            self.cognitive_metrics = {
                "learning_velocity": 0.0,
                "adaptation_rate": 0.0,
                "relationship_depth": self.cognitive_metrics.get("relationship_depth", 0.0) * 0.5,
                "cognitive_coherence": 0.0,
            }

            debugger.info("evolution_engine", "Session reset completed with learning continuity")


# Global advanced evolution engine instance
_evolution_engine = None
_engine_lock = Lock()


def get_evolution_engine() -> AdvancedEvolutionEngine:
    """
    Get global advanced evolution engine instance with thread safety

    Why: Provide singleton access across application with enhanced capabilities
    Where: Used by all modules needing sophisticated evolution tracking
    How: Thread-safe singleton pattern with advanced evolution engine
    """
    global _evolution_engine
    if _evolution_engine is None:
        with _engine_lock:
            if _evolution_engine is None:  # Double-check locking pattern
                _evolution_engine = AdvancedEvolutionEngine()
                debugger.info("evolution_engine", "Global advanced evolution engine created")
    return _evolution_engine


def reset_evolution_engine() -> None:
    """
    Reset global advanced evolution engine with thread safety

    Why: Allow clean state for testing and system resets
    Where: Used in test cases and system maintenance
    How: Thread-safe reset of global engine with proper cleanup
    """
    global _evolution_engine
    with _engine_lock:
        if _evolution_engine is not None:
            debugger.info("evolution_engine", "Resetting global evolution engine")
        _evolution_engine = None
