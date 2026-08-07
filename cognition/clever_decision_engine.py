#!/usr/bin/env python3
"""
clever_decision_engine.py - Clever's Decision-Making Framework for System Actions

Why: Provides Clever with sophisticated decision-making capabilities to prevent
     disruptive actions and make context-aware choices about system interactions
Where: Core decision engine integrated throughout Clever's cognitive system
How: Multi-layered decision framework with context analysis and impact assessment

File Usage:
    - Called by: All system components before performing potentially disruptive actions
    - Key dependencies: debug_config.py for logging, database.py for context storage
    - Decision contexts: Development environment protection, user interaction analysis
    - Impact assessment: System stability, workflow disruption, resource usage
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from debug_config import get_debugger

debugger = get_debugger()


class ActionSeverity(Enum):
    """Action severity levels for decision-making"""

    HARMLESS = "harmless"  # No risk (logging, reading)
    LOW_RISK = "low_risk"  # Minimal impact (file writes)
    MEDIUM_RISK = "medium_risk"  # Potential disruption (service restarts)
    HIGH_RISK = "high_risk"  # Major disruption (IDE restart, system changes)
    CRITICAL = "critical"  # System-wide impact (network changes, etc.)


class UserContext(Enum):
    """User interaction context states"""

    ACTIVELY_CODING = "actively_coding"  # User is actively developing
    CONVERSING = "conversing"  # User is chatting with Clever
    IDLE_SHORT = "idle_short"  # Short idle period (< 5 min)
    IDLE_LONG = "idle_long"  # Long idle period (> 5 min)
    ASLEEP_DETECTED = "asleep_detected"  # Keyboard mashing detected
    TYPO_PATTERN = "typo_pattern"  # Typo/correction pattern detected
    UNCERTAIN = "uncertain"  # Cannot determine context


@dataclass
class DecisionContext:
    """Context information for decision-making"""

    action_type: str
    severity: ActionSeverity
    description: str
    user_context: UserContext
    timestamp: float = field(default_factory=time.time)
    environment_state: Dict[str, Any] = field(default_factory=dict)
    recent_actions: List[str] = field(default_factory=list)
    user_input_pattern: str = "normal"
    vscode_active: bool = True
    codespace_environment: bool = False


@dataclass
class DecisionResult:
    """Result of decision-making process"""

    allow_action: bool
    reasoning: str
    alternative_action: Optional[str] = None
    defer_until: Optional[float] = None
    requires_confirmation: bool = False


class CleverDecisionEngine:
    """
    Clever's sophisticated decision-making engine for system actions

    Why: Prevents disruptive actions that could restart IDE or interrupt workflow
    Where: Central decision authority for all potentially impactful system operations
    How: Context-aware analysis with user pattern recognition and impact assessment
    """

    def __init__(self):
        """Initialize decision engine with pattern recognition"""
        self._lock = threading.RLock()
        self._recent_decisions = []
        self._user_patterns = {}
        self._last_user_activity = time.time()
        self._consecutive_typos = 0
        self._keyboard_mash_threshold = 5

        debugger.info("decision_engine", "Clever decision engine initialized")

    def analyze_user_input_pattern(self, user_input: str) -> UserContext:
        """
        Analyze user input to determine context (talking, typos, asleep)

        Why: Critical for understanding whether user is actively engaged or needs assistance
        Where: Called before any system action to assess user state
        How: Pattern recognition for keyboard mashing, typos, and normal conversation
        """
        if not user_input or len(user_input.strip()) == 0:
            return UserContext.IDLE_SHORT

        # Detect keyboard mashing (fell asleep on keyboard)
        keyboard_mash_indicators = [
            len(set(user_input.lower())) <= 3 and len(user_input) > 10,  # Repeated chars
            user_input.count(" ") == 0 and len(user_input) > 20,  # No spaces, long
            any(
                char * 5 in user_input.lower() for char in "abcdefghijklmnopqrstuvwxyz"
            ),  # 5+ repeated chars
            user_input.lower() in ["aaaaa", "sssss", "ddddd", "fffff"],  # Common mash patterns
        ]

        if any(keyboard_mash_indicators):
            self._consecutive_typos += 1
            if self._consecutive_typos >= self._keyboard_mash_threshold:
                debugger.info("decision_engine", "Keyboard mashing detected - user may be asleep")
                return UserContext.ASLEEP_DETECTED
            return UserContext.TYPO_PATTERN

        # Detect typo patterns
        typo_indicators = [
            len(user_input) < 5
            and not any(word in user_input.lower() for word in ["yes", "no", "ok", "hi"]),
            user_input.count("x") > len(user_input) * 0.3,  # High x ratio (backspace attempts)
        ]

        if any(typo_indicators):
            return UserContext.TYPO_PATTERN

        # Reset typo counter for normal input
        self._consecutive_typos = 0

        # Detect normal conversation
        if len(user_input.split()) >= 2 or any(
            word in user_input.lower()
            for word in ["continue", "yes", "no", "okay", "thanks", "please"]
        ):
            return UserContext.CONVERSING

        return UserContext.UNCERTAIN

    def assess_environment_risk(self, action_type: str, severity: ActionSeverity) -> Dict[str, Any]:
        """
        Assess environmental risk of performing an action

        Why: Prevents actions that could disrupt VS Code, codespace, or development workflow
        Where: Called before system modifications to evaluate impact
        How: Multi-factor risk assessment considering environment and action severity
        """
        risk_factors = {
            "vscode_disruption_risk": False,
            "codespace_disruption_risk": False,
            "system_resource_risk": False,
            "workflow_interruption_risk": False,
            "recovery_difficulty": "easy",
        }

        # VS Code disruption risks
        vscode_risky_actions = [
            "module_level_import_monitoring",
            "aggressive_system_monitoring",
            "file_watcher_creation",
            "large_file_modifications",
            "extension_installation",
        ]

        if action_type in vscode_risky_actions or severity in [
            ActionSeverity.HIGH_RISK,
            ActionSeverity.CRITICAL,
        ]:
            risk_factors["vscode_disruption_risk"] = True
            risk_factors["recovery_difficulty"] = "difficult"

        # Codespace-specific risks
        if action_type in ["network_configuration", "port_binding", "service_restart"]:
            risk_factors["codespace_disruption_risk"] = True

        # System resource risks
        if action_type in ["memory_intensive_operation", "cpu_intensive_monitoring"]:
            risk_factors["system_resource_risk"] = True

        return risk_factors

    def make_decision(self, context: DecisionContext) -> DecisionResult:
        """
        Make an informed decision about whether to allow an action

        Why: Central decision-making prevents disruptive actions and maintains workflow
        Where: Called before any potentially impactful system operation
        How: Multi-factor analysis considering user context, environment, and action severity
             with optional visual representation of decision process
        """
        with self._lock:
            # Analyze current situation
            risk_assessment = self.assess_environment_risk(context.action_type, context.severity)

            # Check if we should create visual representation of this decision
            should_visualize = context.severity in [
                ActionSeverity.HIGH_RISK,
                ActionSeverity.CRITICAL,
            ]

            if should_visualize:
                try:
                    # Import here to avoid circular imports
                    from clever_visual_cognitive_engine import visualize_decision

                    decision_context = {
                        "action_type": context.action_type,
                        "description": context.description,
                        "severity": context.severity.value,
                        "user_context": context.user_context.value,
                        "risk_assessment": risk_assessment,
                    }

                    canvas_id = visualize_decision(decision_context)
                    debugger.info(
                        "decision_engine",
                        f"Decision visualization created: {canvas_id}",
                    )
                except Exception as e:
                    debugger.error(
                        "decision_engine",
                        f"Failed to create decision visualization: {e}",
                    )

            # Decision logic based on user context
            if context.user_context == UserContext.ASLEEP_DETECTED:
                return DecisionResult(
                    allow_action=False,
                    reasoning="User appears to be asleep (keyboard mashing detected) - deferring disruptive actions",
                    defer_until=time.time() + 3600,  # Defer for 1 hour
                )

            if context.user_context == UserContext.TYPO_PATTERN:
                if context.severity in [
                    ActionSeverity.HIGH_RISK,
                    ActionSeverity.CRITICAL,
                ]:
                    return DecisionResult(
                        allow_action=False,
                        reasoning="User input suggests typos/confusion - avoiding high-risk actions",
                        requires_confirmation=True,
                    )

            if context.user_context == UserContext.ACTIVELY_CODING:
                if risk_assessment["vscode_disruption_risk"]:
                    return DecisionResult(
                        allow_action=False,
                        reasoning="User actively coding - preventing VS Code disruption",
                        alternative_action="defer_until_idle",
                    )

            # Environment-specific decisions
            if context.codespace_environment and risk_assessment["codespace_disruption_risk"]:
                return DecisionResult(
                    allow_action=False,
                    reasoning="Codespace environment - avoiding service disruption",
                    alternative_action="use_safe_alternative",
                )

            # Default approval for low-risk actions
            if context.severity in [ActionSeverity.HARMLESS, ActionSeverity.LOW_RISK]:
                return DecisionResult(allow_action=True, reasoning="Low-risk action approved")

            # Require careful consideration for higher-risk actions
            if context.severity in [ActionSeverity.HIGH_RISK, ActionSeverity.CRITICAL]:
                return DecisionResult(
                    allow_action=False,
                    reasoning="High-risk action requires explicit user confirmation",
                    requires_confirmation=True,
                )

            # Default medium-risk approval with monitoring
            return DecisionResult(
                allow_action=True,
                reasoning="Medium-risk action approved with monitoring",
            )

    def log_decision(self, context: DecisionContext, result: DecisionResult):
        """Log decision for pattern analysis and learning"""
        decision_record = {
            "timestamp": context.timestamp,
            "action_type": context.action_type,
            "severity": context.severity.value,
            "user_context": context.user_context.value,
            "decision": result.allow_action,
            "reasoning": result.reasoning,
        }

        self._recent_decisions.append(decision_record)

        # Keep only recent decisions (last 100)
        if len(self._recent_decisions) > 100:
            self._recent_decisions = self._recent_decisions[-100:]

        debugger.info(
            "decision_engine",
            f"Decision logged: {context.action_type} -> {'ALLOWED' if result.allow_action else 'DENIED'}",
        )


# Global decision engine instance
_decision_engine = None


def get_decision_engine() -> CleverDecisionEngine:
    """Get shared decision engine instance"""
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = CleverDecisionEngine()
    return _decision_engine


def require_decision(
    action_type: str,
    severity: ActionSeverity,
    description: str,
    user_input: str = "",
    **kwargs,
) -> DecisionResult:
    """
    Convenient function to require decision approval for an action

    Why: Simple interface for components to check before performing actions
    Where: Called throughout Clever's system before potentially disruptive operations
    How: Creates context and gets decision from engine
    """
    engine = get_decision_engine()

    context = DecisionContext(
        action_type=action_type,
        severity=severity,
        description=description,
        user_context=engine.analyze_user_input_pattern(user_input),
        **kwargs,
    )

    result = engine.make_decision(context)
    engine.log_decision(context, result)

    return result
