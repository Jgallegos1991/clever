"""Academic enrichment adapter for local response generation.

Why:
    Keep academic enrichment as an adapter around the canonical academic
    knowledge engine instead of embedding that responsibility in a root monolith.

Where:
    Knowledge layer: educational enrichment sourced from local knowledge engines.

How:
    Calls the existing local academic engine when available and formats a compact
    enrichment payload. No internet access and no external AI fallback.
"""

from __future__ import annotations

from typing import Any

try:
    from cognition.academic_knowledge_engine import get_academic_engine
except ImportError:  # pragma: no cover - optional during partial installs
    get_academic_engine = None  # type: ignore[assignment]


def get_academic_knowledge(user_input: str) -> Any | None:
    """Return local academic knowledge for user input when available."""
    if get_academic_engine is None:
        return None
    engine = get_academic_engine()
    analysis = engine.analyze_academic_content(user_input)
    return engine.get_educational_response(analysis, user_input)


def build_academic_enrichment(knowledge: Any | None) -> str | None:
    """Build a short enrichment paragraph from a knowledge response."""
    if not knowledge:
        return None

    domain = knowledge.domain.value.replace("_", " ").title()
    segments = [f"Deep dive: {knowledge.concept} ({domain}) — {knowledge.explanation}"]
    if knowledge.examples:
        segments.append(f"Example: {'; '.join(knowledge.examples[:2])}")
    if knowledge.related_topics:
        segments.append(
            f"Wanna explore further? Check {', '.join(knowledge.related_topics[:3])}."
        )
    return " ".join(segments)
