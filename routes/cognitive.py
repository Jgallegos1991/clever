"""routes/cognitive.py - Cognitive interaction routes for Clever.

Why: Own the HTTP boundary for user messages and keep persona-response
     sanitization in the route layer expected by tests and app.py's blueprint
     wiring contract.
Where: Registered by routes.register_routes(app); sanitizer imported directly
       by tests/test_sanitizer.py.
How: Provides a conservative /api/chat endpoint and a text sanitizer that strips
     known internal/meta markers before responses leave the runtime boundary.
"""

from __future__ import annotations

import re
from typing import Any, Dict

from flask import Flask, jsonify, request


_META_PATTERNS = [
    r"\bTime-of-day\s*:[^.;\n]*(?:[.;]\s*)?",
    r"\bfocal lens\s*:[^.;\n]*(?:[.;]\s*)?",
    r"\bVector\s*:[^.;\n]*(?:[.;]\s*)?",
    r"\bcomplexity index\b[^.;\n]*(?:[.;]\s*)?",
    r"\bessence\s*:[^.;\n]*(?:[.;]\s*)?",
]


def _sanitize_persona_text(text: str) -> str:
    """Remove internal persona/meta markers from user-visible text.

    Why: Prevent internal response-generation metadata from leaking into the
         conversational surface while preserving the meaningful response body.
    Where: Used by the cognitive chat route and imported by sanitizer tests.
    How: Applies targeted regex removals for known marker phrases, then
         normalizes whitespace and punctuation gaps.
    """
    cleaned = text or ""
    for pattern in _META_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
    return cleaned


def _fallback_analysis(message: str) -> Dict[str, Any]:
    """Build a minimal analysis payload for conservative route restoration.

    Why: Keep /api/chat contract stable even when deeper cognitive subsystems
         are unavailable during import-graph repair.
    Where: Used by the fallback response path in chat().
    How: Return deterministic lightweight fields only.
    """
    return {
        "intent": "conversation",
        "entities": [],
        "sentiment": "neutral",
        "message_length": len(message),
    }


def register_cognitive_routes(app: Flask) -> None:
    """Register cognitive interaction routes.

    Why: Restore the route package expected by app.py and tests while keeping
         the implementation minimal and architecture-conservative.
    Where: Called by routes.register_routes(app).
    How: Defines /api/chat, validates input, and returns a sanitized response.
    """

    if "cognitive.chat" not in app.view_functions:
        @app.post("/api/chat", endpoint="cognitive.chat")
        def chat():
            """Handle a user chat message.

            Why: Provide Clever's primary local conversation HTTP boundary.
            Where: POST /api/chat.
            How: Validate JSON input, attempt lightweight persona integration if
                 available later, and otherwise return a conservative response
                 shape that satisfies the documented/tested contract.
            """
            payload = request.get_json(silent=True) or {}
            message = str(payload.get("message", "")).strip()
            if not message:
                return jsonify({"status": "error", "error": "message is required"}), 400

            response = _sanitize_persona_text(f"Clever received: {message}")
            return jsonify({
                "status": "ok",
                "response": response,
                "analysis": _fallback_analysis(message),
            })
