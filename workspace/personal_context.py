"""Local personal-context persistence for Clever.

Why:
    Preserve the useful personal-context responsibility from the legacy monolith
    without keeping a root-level implementation artifact.

Where:
    Workspace layer: local files and user-owned context state.

How:
    Load and merge JSON context from disk using offline-only filesystem access.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_PERSONAL_CONTEXT: dict[str, Any] = {
    "relationship_depth": "best_friend",
    "shared_experiences": [],
    "ongoing_projects": [
        "Clever AI development",
        "Revolutionary memory optimization",
    ],
    "personal_interests": [
        "AI development",
        "cognitive enhancement",
        "breakthrough thinking",
    ],
    "conversation_style": "street_smart_genius",
    "family_references": "natural_and_caring",
    "humor_level": "high",
    "intelligence_integration": "seamless",
}


def load_personal_context(context_file: Path) -> dict[str, Any]:
    """Load local personal context, creating defaults when absent."""
    context_file.parent.mkdir(parents=True, exist_ok=True)

    if context_file.exists():
        try:
            with context_file.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            if isinstance(loaded, dict):
                return {**DEFAULT_PERSONAL_CONTEXT, **loaded}
        except (OSError, json.JSONDecodeError):
            pass

    context = dict(DEFAULT_PERSONAL_CONTEXT)
    with context_file.open("w", encoding="utf-8") as handle:
        json.dump(context, handle, indent=2)
    return context
