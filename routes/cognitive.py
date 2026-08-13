"""routes/cognitive.py - Cognitive interaction routes for Clever.

Why: Own the HTTP boundary for user messages and route chat through Clever's
     actual persona engine instead of a placeholder response.
Where: Registered by routes.register_routes(app); sanitizer imported directly
       by tests/test_sanitizer.py.
How: Provides /api/chat, sanitizes outbound text, lazily loads the canonical
     persona engine, and fails explicitly if cognition cannot be reached.
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


def _load_persona_engine():
    """Load Clever's canonical persona engine lazily.

    Why: /api/chat must use actual Clever cognition, not a placeholder or fake
         fallback, while keeping module import lightweight for sanitizer tests.
    Where: Called inside chat() only after request validation.
    How: Imports the global persona_engine from core.persona; any import/runtime
         failure is allowed to surface to the route as an explicit 503.
    """
    from core.persona import persona_engine

    return persona_engine


def _analysis_from_persona_response(persona_response: Any, message: str) -> Dict[str, Any]:
    """Build the public analysis payload from PersonaResponse metadata.

    Why: Preserve the tested /api/chat response contract while grounding fields
         in the actual persona engine result instead of a fake fallback analysis.
    Where: Used by chat() after persona_engine.generate().
    How: Reads stable attributes from PersonaResponse and fills only lightweight
         compatibility metadata when a field is absent.
    """
    context = getattr(persona_response, "context", {}) or {}
    nlp_analysis = context.get("nlp_analysis", {}) if isinstance(context, dict) else {}
    return {
        "intent": nlp_analysis.get("intent") or context.get("conversation_intent") if isinstance(context, dict) else None,
        "entities": nlp_analysis.get("entities", []),
        "sentiment": getattr(persona_response, "sentiment", nlp_analysis.get("sentiment", "neutral")),
        "mode": getattr(persona_response, "mode", "Auto"),
        "message_length": len(message),
    }


def register_cognitive_routes(app: Flask) -> None:
    """Register cognitive interaction routes.

    Why: Restore the route package expected by app.py and tests while routing
         chat through the canonical persona engine.
    Where: Called by routes.register_routes(app).
    How: Defines /api/chat, validates input, calls persona_engine.generate(),
         sanitizes the returned text, and reports explicit service errors if
         cognition cannot be imported or initialized.
    """

    if "cognitive.chat" not in app.view_functions:
        @app.post("/api/chat", endpoint="cognitive.chat")
        def chat():
            """Handle a user chat message through Clever's persona engine.

            Why: Provide Clever's primary local conversation HTTP boundary using
                 real cognition rather than a temporary scaffold.
            Where: POST /api/chat.
            How: Validate JSON input, delegate to persona_engine.generate(), and
                 return sanitized user-visible response text plus analysis data.
            """
            payload = request.get_json(silent=True) or {}
            message = str(payload.get("message", "")).strip()
            if not message:
                return jsonify({"status": "error", "error": "message is required"}), 400

            try:
                persona_engine = _load_persona_engine()
                persona_response = persona_engine.generate(
                    message,
                    mode=str(payload.get("mode", "Auto") or "Auto"),
                    context=payload.get("context") if isinstance(payload.get("context"), dict) else None,
                    history=payload.get("history") if isinstance(payload.get("history"), list) else None,
                )
            except Exception as exc:
                return jsonify({
                    "status": "error",
                    "error": "persona engine unavailable",
                    "details": str(exc),
                }), 503

            response_text = _sanitize_persona_text(getattr(persona_response, "text", ""))
            return jsonify({
                "status": "ok",
                "response": response_text,
                "analysis": _analysis_from_persona_response(persona_response, message),
                "approach": getattr(persona_response, "mode", None),
                "mood": getattr(persona_response, "sentiment", None),
                "particle_intensity": getattr(persona_response, "particle_command", None),
            })
