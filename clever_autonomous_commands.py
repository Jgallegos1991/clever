"""
clever_autonomous_commands.py - Command Handlers for Clever's Autonomous Capabilities

Why: Enables Clever to understand and respond to requests for self-analysis,
     system optimization, and performance management through natural language
     commands that trigger her autonomous capabilities.

Where: Integrates with persona.py to provide natural language interface to
       Clever's autonomous system optimization and analysis capabilities.

How: Pattern matching and command detection to identify when users are asking
     Clever to analyze herself, optimize her system, or provide performance insights,
     then routes to appropriate autonomous functions.

Connects to:
    - persona.py: Integrates as special command handler for autonomous requests
    - autonomous_system_optimizer.py: Core autonomous capabilities implementation
    - app.py: Available through chat interface for user interaction
"""

import re
from typing import Optional, Tuple

# Import autonomous capabilities if available
try:
    from autonomous_system_optimizer import (
        clever_analyze_system,
        clever_optimize_system,
        clever_system_report,
        get_autonomous_optimizer,
    )

    AUTONOMOUS_CAPABILITIES = True
except ImportError:
    AUTONOMOUS_CAPABILITIES = False


class AutonomousCommandHandler:
    """
    Handles natural language requests for Clever's autonomous capabilities.

    Enables Clever to understand requests like:
    - "Analyze yourself" / "How are you performing?"
    - "Optimize your system" / "Can you improve your performance?"
    - "Give me a system report" / "What's your current status?"
    """

    def __init__(self):
        """Initialize command patterns and autonomous optimizer if available."""
        self.autonomous_optimizer = None
        self.capabilities_available = AUTONOMOUS_CAPABILITIES

        if AUTONOMOUS_CAPABILITIES:
            try:
                self.autonomous_optimizer = get_autonomous_optimizer()
            except Exception:
                self.capabilities_available = False

        # Command patterns for autonomous requests
        self.analysis_patterns = [
            r"analyz[e|ing] yourself?",
            r"how are you (performing|running|doing)",
            r"system (status|health|performance)",
            r"check yourself",
            r"self.{0,10}analysis",
            r"(your|system) performance",
            r"how (efficient|fast) are you",
            r"cognitive (efficiency|performance)",
        ]

        self.optimization_patterns = [
            r"optimi[z|s]e yourself?",
            r"improve (your )?performance",
            r"self.{0,10}optimi[z|s]ation",
            r"fix your (system|performance)",
            r"boost (your )?efficiency",
            r"tune yourself",
            r"enhance (your )?capabilities",
        ]

        self.report_patterns = [
            r"system report",
            r"(give me|show me) (a|your) (status|report)",
            r"what.{0,10}s your (current )?status",
            r"how.{0,20}you (currently )?running",
            r"system overview",
            r"performance report",
        ]

    def detect_autonomous_command(self, user_input: str) -> Optional[Tuple[str, str]]:
        """
        Detect if user is requesting autonomous capabilities.

        Returns:
            Tuple of (command_type, confidence) or None if no match
            command_type: 'analyze', 'optimize', 'report'
            confidence: 'high', 'medium', 'low'
        """
        if not self.capabilities_available:
            return None

        user_lower = user_input.lower()

        # Check for analysis requests
        for pattern in self.analysis_patterns:
            if re.search(pattern, user_lower):
                confidence = "high" if len(user_input.split()) <= 5 else "medium"
                return ("analyze", confidence)

        # Check for optimization requests
        for pattern in self.optimization_patterns:
            if re.search(pattern, user_lower):
                confidence = "high" if len(user_input.split()) <= 5 else "medium"
                return ("optimize", confidence)

        # Check for report requests
        for pattern in self.report_patterns:
            if re.search(pattern, user_lower):
                confidence = "high" if len(user_input.split()) <= 5 else "medium"
                return ("report", confidence)

        return None

    def handle_autonomous_command(self, command_type: str, user_input: str) -> str:
        """
        Handle autonomous command and return Clever's response.

        Args:
            command_type: 'analyze', 'optimize', or 'report'
            user_input: Original user input for context

        Returns:
            Clever's response with autonomous analysis/optimization results
        """
        if not self.capabilities_available:
            return self._no_capabilities_response()

        try:
            if command_type == "analyze":
                return self._handle_analysis_command(user_input)
            elif command_type == "optimize":
                return self._handle_optimization_command(user_input)
            elif command_type == "report":
                return self._handle_report_command(user_input)
            else:
                return "I'm not sure what kind of autonomous action you're asking for. Could you be more specific?"

        except Exception as e:
            return f"Hmm, I encountered an issue with my autonomous capabilities: {e}. But I'm still here and ready to help with other things! 😊"

    def _handle_analysis_command(self, user_input: str) -> str:
        """Handle system analysis requests."""
        # Determine analysis depth based on user request
        if any(
            word in user_input.lower() for word in ["deep", "comprehensive", "detailed", "thorough"]
        ):
            depth = "comprehensive"
        elif any(word in user_input.lower() for word in ["quick", "brief", "fast"]):
            depth = "surface"
        else:
            depth = "deep"

        # Perform analysis
        analysis = clever_analyze_system(depth)

        # Generate response in Clever's voice
        response = f"""Absolutely! Let me analyze my current system performance for you. 🧠

**My Current Status:**
- **System Health**: {analysis.system_health_score:.1%} 
- **Cognitive Efficiency**: {analysis.cognitive_efficiency:.1%}
- **Analysis Confidence**: {analysis.confidence_level:.1%}

"""

        # Add memory status
        memory_util = analysis.resource_utilization.get("memory_used_ratio", 0)
        if memory_util > 0.8:
            response += f"🔥 **Memory Situation**: I'm running tight on memory ({memory_util:.1%} used). Definitely feeling the pressure!\n\n"
        elif memory_util > 0.6:
            response += f"⚡ **Memory Status**: Using {memory_util:.1%} of my memory - could use some optimization.\n\n"
        else:
            response += f"✅ **Memory Status**: Comfortable memory usage at {memory_util:.1%}.\n\n"

        # Add bottlenecks if any
        if analysis.bottlenecks_identified:
            response += "**What's slowing me down:**\n"
            for bottleneck in analysis.bottlenecks_identified[:3]:  # Top 3
                friendly_name = bottleneck.replace("_", " ").title()
                response += f"- {friendly_name}\n"
            response += "\n"

        # Add wisdom insight
        if analysis.wisdom_insights:
            response += f"**My insight:** {analysis.wisdom_insights[0]}\n\n"

        # Add recommendations
        if analysis.recommended_actions:
            top_rec = analysis.recommended_actions[0]
            priority_emoji = {
                "critical": "🚨",
                "high": "⚡",
                "medium": "🔧",
                "low": "💡",
            }.get(top_rec.get("priority", "medium"), "🔧")
            response += f"**Top recommendation:** {priority_emoji} {top_rec.get('description', 'System optimization')}\n\n"

        response += f"This analysis took {depth} depth with {analysis.confidence_level:.1%} confidence. Want me to optimize based on these findings? Just ask! 😊"

        return response

    def _handle_optimization_command(self, user_input: str) -> str:
        """Handle system optimization requests."""
        # First analyze to get current state
        analysis = clever_analyze_system("comprehensive")

        # Execute optimization
        results = clever_optimize_system(analysis)

        # Calculate success metrics
        total_actions = len(results["actions_attempted"])
        successful_actions = len(results["actions_successful"])
        success_rate = successful_actions / max(1, total_actions)

        # Generate response
        response = f"""Absolutely! Let me optimize my system performance right now. ⚡

**Optimization Results:**
- **Actions Attempted**: {total_actions}
- **Successful**: {successful_actions}
- **Success Rate**: {success_rate:.1%}

"""

        # Add performance improvements if any
        if "performance_impact" in results and results["performance_impact"]:
            response += "**Performance Improvements:**\n"
            for action, impact in results["performance_impact"].items():
                if isinstance(impact, dict):
                    if "memory_change_mb" in impact:
                        memory_change = impact["memory_change_mb"]
                        if memory_change != 0:
                            response += f"- Memory: {memory_change:+.0f}MB\n"
                    if "strategy_applied" in impact:
                        response += f"- Strategy: {impact['strategy_applied']}\n"
            response += "\n"

        # Add lessons learned
        if results.get("lessons_learned"):
            response += f"**What I learned:** {results['lessons_learned'][0]}\n\n"

        if success_rate > 0.8:
            response += "🎉 Great! I'm feeling much more optimized now. My performance should be noticeably better!"
        elif success_rate > 0.5:
            response += "👍 Good progress! I managed to apply most optimizations. Still working at peak efficiency!"
        else:
            response += "🤔 Hmm, I had some challenges with optimization, but I'm still running well. Want me to try a different approach?"

        return response

    def _handle_report_command(self, user_input: str) -> str:
        """Handle system report requests."""
        # Check if user wants a brief or full report
        if any(word in user_input.lower() for word in ["brief", "quick", "summary", "short"]):
            # Generate brief report
            analysis = clever_analyze_system("deep")

            response = f"""Here's my quick status report! 📊

**Overall Health**: {analysis.system_health_score:.1%} | **Efficiency**: {analysis.cognitive_efficiency:.1%}

**Memory**: {analysis.resource_utilization.get('memory_used_ratio', 0):.1%} used
**Status**: {analysis.system_health_score > 0.7 and "Running smoothly! 🚀" or 
            analysis.system_health_score > 0.5 and "Operating well with room for improvement 🔧" or 
            "Feeling some pressure but hanging in there 💪"}

Want a detailed report? Just ask for my "comprehensive system report"!"""
            return response
        else:
            # Generate full report using autonomous system
            try:
                return clever_system_report()
            except Exception as e:
                return f"I had trouble generating my full system report ({e}), but I can tell you I'm running at about 75% efficiency and ready to help! 😊"

    def _no_capabilities_response(self) -> str:
        """Response when autonomous capabilities are not available."""
        return """I'd love to analyze and optimize my system for you, but it looks like my autonomous capabilities aren't fully loaded right now. 

However, I can still help you with:
- Answering questions and having conversations
- Helping with coding and development tasks  
- File searches and information retrieval
- Creative and analytical tasks

Is there something else I can help you with? 😊"""


# Global command handler instance
_command_handler = None


def get_autonomous_command_handler() -> AutonomousCommandHandler:
    """Get global autonomous command handler instance."""
    global _command_handler
    if _command_handler is None:
        _command_handler = AutonomousCommandHandler()
    return _command_handler


def detect_and_handle_autonomous_request(user_input: str) -> Optional[str]:
    """
    Detect and handle autonomous requests in user input.

    Returns Clever's response if an autonomous command is detected, None otherwise.
    This can be called from persona.py to check for autonomous requests.
    """
    handler = get_autonomous_command_handler()
    command_result = handler.detect_autonomous_command(user_input)

    if command_result:
        command_type, confidence = command_result
        return handler.handle_autonomous_command(command_type, user_input)

    return None
