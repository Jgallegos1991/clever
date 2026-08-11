"""Conversation-style routing for Clever responses.

Why:
    Preserve the valid routing responsibility from the legacy monolith while
    keeping cognitive policy in the cognition layer.

Where:
    Cognition layer: classifies user input into response-style intents.

How:
    Keyword-based local routing. This module is deterministic, offline, and does
    not depend on external models.
"""

from __future__ import annotations

from enum import StrEnum


class ConversationStyle(StrEnum):
    CASUAL_CHECK_IN = "casual_check_in"
    DEEP_THINKING = "deep_thinking"
    PROBLEM_SOLVING = "problem_solving"
    FAMILY_REFERENCE = "family_reference"
    BREAKTHROUGH_MOMENT = "breakthrough_moment"
    ADAPTIVE = "adaptive"


FAMILY_NAMES = ("lucy", "ronnie", "peter", "josiah", "jonah")
THINKING_KEYWORDS = (
    "explain",
    "understand",
    "how does",
    "why does",
    "what i",
    "theory",
    "concept",
)
PROBLEM_KEYWORDS = (
    "problem",
    "issue",
    "fix",
    "solve",
    "help",
    "stuck",
    "error",
    "debug",
)
BREAKTHROUGH_KEYWORDS = (
    "revolutionary",
    "breakthrough",
    "genius",
    "amazing",
    "impossible",
)
CASUAL_KEYWORDS = ("hey", "yo", "sup", "what's up", "how are", "how's it")


def analyze_conversation_style(user_input: str) -> ConversationStyle:
    """Classify the requested response style from local text signals."""
    input_lower = user_input.lower()

    if any(name in input_lower for name in FAMILY_NAMES):
        return ConversationStyle.FAMILY_REFERENCE
    if any(keyword in input_lower for keyword in THINKING_KEYWORDS):
        return ConversationStyle.DEEP_THINKING
    if any(keyword in input_lower for keyword in PROBLEM_KEYWORDS):
        return ConversationStyle.PROBLEM_SOLVING
    if any(keyword in input_lower for keyword in BREAKTHROUGH_KEYWORDS):
        return ConversationStyle.BREAKTHROUGH_MOMENT
    if any(keyword in input_lower for keyword in CASUAL_KEYWORDS):
        return ConversationStyle.CASUAL_CHECK_IN
    return ConversationStyle.ADAPTIVE
