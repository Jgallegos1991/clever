#!/usr/bin/env python3
"""
Voice engine regression tests guarding Clever's warm companion persona.

Why: Ensure voice transformations and backend status reporting stay aligned
with Jay's offline-first expectations even as audio modules evolve.
Where: Executed within the pytest suite and documentation validator to confirm
the voice stack still honors its guardrails before deployments.
How: Instantiates `CleverVoiceEngine`, runs representative transformations, and
asserts persona softening plus backend metadata remain intact.

File Usage:
    - `make test`: pytest entry point covering the voice pipeline.
    - `validate-documentation.sh`: scans this file for Why/Where/How compliance.
Connects to:
    - `clever_voice_engine.py`: source module under test.
    - `enhanced_voice_engine.py`: related persona presets referenced by tests.
"""

import pytest

from clever_voice_engine import CleverVoiceEngine


def test_preview_transformed_warm_humor():
    engine = CleverVoiceEngine()
    engine.set_persona("warm_humorous_companion")
    text = "However, we can optimize this and therefore, ship it."
    out = engine.preview_transformed(text)
    # Softening replacements should occur
    assert "But hey," in out or "So," in out
    # Warm tail addendum or empathy softener likely present
    assert "you're doing great" in out or "— alright?" in out


def test_backend_status_shape():
    engine = CleverVoiceEngine()
    status = engine.get_status()
    assert "active_persona" in status
    assert "available_backends" in status
    assert isinstance(status["available_backends"], list)
    assert status.get("offline_only") is True
