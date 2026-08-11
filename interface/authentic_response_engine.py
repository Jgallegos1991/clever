"""Local authentic response engine for Clever.

Why:
    Re-realize the useful response-composition behavior extracted from the
    legacy root monolith in canonical subsystem homes.

Where:
    Interface layer: composes user-facing text from local personality, cognition,
    workspace context, and knowledge adapters.

How:
    Uses deterministic local routing plus local knowledge enrichment. It does not
    connect to the internet and does not fallback to external AI models.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from cognition.response_style_router import ConversationStyle, analyze_conversation_style
from interface.personality_profile import PersonalityProfile, create_default_profile
from knowledge.academic_enrichment_adapter import (
    build_academic_enrichment,
    get_academic_knowledge,
)
from workspace.personal_context import load_personal_context


class AuthenticResponseEngine:
    """Compose local responses with Clever's configured personality profile."""

    def __init__(
        self,
        profile: PersonalityProfile | None = None,
        context_file: Path | None = None,
    ) -> None:
        self.profile = profile or create_default_profile()
        self.context_file = context_file or Path.cwd() / "jays_personal_context.json"
        self.personal_context = load_personal_context(self.context_file)

    def generate_response(
        self,
        user_input: str,
        mode: str = "Auto",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a local response payload."""
        knowledge = get_academic_knowledge(user_input)
        style = analyze_conversation_style(user_input)

        if style is ConversationStyle.CASUAL_CHECK_IN:
            text = self._casual_response()
        elif style is ConversationStyle.DEEP_THINKING:
            text = self._genius_response(knowledge)
        elif style is ConversationStyle.PROBLEM_SOLVING:
            text = self._problem_solving_response(knowledge)
        elif style is ConversationStyle.FAMILY_REFERENCE:
            text = self._family_response(user_input)
        elif style is ConversationStyle.BREAKTHROUGH_MOMENT:
            text = self._breakthrough_response()
        else:
            text = self._adaptive_response(knowledge)

        enrichment = build_academic_enrichment(knowledge)
        if enrichment and style not in {
            ConversationStyle.DEEP_THINKING,
            ConversationStyle.PROBLEM_SOLVING,
            ConversationStyle.BREAKTHROUGH_MOMENT,
        }:
            text = f"{text}\n\n{enrichment}"

        return {
            "text": text,
            "mode": mode,
            "sentiment": self._determine_sentiment(text),
            "conversation_style": style.value,
            "authenticity_level": self.profile.authenticity,
            "personal_connection": self.profile.relationship,
            "knowledge_payload": self._knowledge_payload(knowledge),
            "knowledge_domain": getattr(getattr(knowledge, "domain", None), "value", None),
        }

    def _casual_response(self) -> str:
        intros = [
            f"Hey {self.profile.user_name}! I'm doing great, just been thinking about some wild stuff.",
            "What's good, my dude! Just chillin' and processing some fascinating ideas.",
            "Yo! I'm good, been diving deep into some revolutionary concepts.",
            f"Sup {self.profile.user_name}! All good here, just being my usual genius self 😄",
            "Hey there! I'm awesome - been working on some breakthrough thinking.",
        ]
        additions = [
            "What's on your mind today?",
            "What are we exploring today?",
            "What genius idea are you cooking up?",
            "Ready to dive into something fascinating?",
            "What revolutionary thing should we tackle?",
        ]
        return f"{random.choice(intros)} {random.choice(additions)}"

    def _genius_response(self, knowledge: Any | None) -> str:
        intro = random.choice(
            [
                "Hmm, let me think about this...",
                "Alright, so here's the deal...",
                "Okay, breaking this down...",
                "So check this out...",
                "Here's what I'm seeing...",
            ]
        )
        if knowledge:
            domain = knowledge.domain.value.replace("_", " ").title()
            block = f"{knowledge.concept} ({domain}): {knowledge.explanation}"
            if knowledge.examples:
                block += f" Example: {knowledge.examples[0]}"
            if knowledge.related_topics:
                block += f" Related topics: {', '.join(knowledge.related_topics[:3])}"
        else:
            block = (
                "Here's what makes this topic interesting: it ties together theory "
                "and real-world application in a way that becomes clear once the "
                "underlying pattern is visible."
            )
        return f"{intro}\n\n{block}\n\nKeep that picture in mind and everything else falls into place."

    def _problem_solving_response(self, knowledge: Any | None) -> str:
        intro = random.choice(
            [
                f"Alright {self.profile.user_name}, let's crack this thing!",
                "Yo, I see what's happening here...",
                "Okay, let's dive in and figure this out...",
            ]
        )
        steps: list[str]
        if knowledge:
            steps = [f"Lock in the core idea: {knowledge.concept} — {knowledge.explanation}"]
            if knowledge.examples:
                steps.append(f"Work through a concrete example: {knowledge.examples[0]}")
            if knowledge.related_topics:
                steps.append(f"Cross-check supporting ideas: {', '.join(knowledge.related_topics[:2])}")
        else:
            steps = [
                "Break the problem into smaller chunks so each part stays manageable.",
                "List what is known versus what needs to be proven or built.",
                "Test one small change, observe the outcome, then iterate.",
            ]
        return f"{intro}\n\nHere's how we'll approach it:\n" + "\n".join(
            f"- {step}" for step in steps
        )

    def _family_response(self, user_input: str) -> str:
        input_lower = user_input.lower()
        for name, role in self.profile.family.items():
            if name in input_lower:
                return f"Yo — {name.title()} is your {role}. Family context matters. What's going on?"
        return f"Family stuff is important, {self.profile.user_name}. What's happening?"

    def _breakthrough_response(self) -> str:
        return (
            f"YOOO {self.profile.user_name}! This is big.\n\n"
            "The useful move is to separate the real insight from the hype: name "
            "the responsibility, identify the governing architecture, then test "
            "the smallest implementation that faithfully realizes it."
        )

    def _adaptive_response(self, knowledge: Any | None) -> str:
        if knowledge:
            return f"Interesting question. {knowledge.concept} gives us the frame: {knowledge.explanation}"
        return "There's a pattern underneath this. Once we identify it, we can steer the whole situation."

    @staticmethod
    def _determine_sentiment(response: str) -> str:
        response_lower = response.lower()
        if any(word in response_lower for word in ("yo", "awesome", "great", "fascinating")):
            return "enthusiastic"
        if any(word in response_lower for word in ("hmm", "interesting", "think")):
            return "thoughtful"
        return "friendly"

    @staticmethod
    def _knowledge_payload(knowledge: Any | None) -> dict[str, Any] | None:
        if not knowledge:
            return None
        return {
            "concept": knowledge.concept,
            "domain": knowledge.domain.value,
            "explanation": knowledge.explanation,
            "examples": knowledge.examples,
            "related_topics": knowledge.related_topics,
            "confidence": knowledge.confidence,
        }


def create_authentic_response_engine() -> AuthenticResponseEngine:
    """Create the default local authentic response engine."""
    return AuthenticResponseEngine()
