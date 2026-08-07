"""tests/test_response_quality.py - Tests for the Response Quality Validation Layer

Why: Ensure the quality validator correctly identifies placeholder/low-quality
     responses and correctly passes high-quality contextual responses, so that
     the PersonaEngine can detect and log degraded output reliably.

Where: Part of the standard pytest suite (tests/). Guards against regressions
       in utils/response_quality.py and verifies that PersonaEngine surfaces
       quality metrics in debug_metrics.

How: Direct unit tests on ResponseQualityValidator and QualityReport, plus
     integration smoke tests via PersonaEngine.generate() to confirm the
     quality score key is present in debug_metrics.

Connects to:
    - utils/response_quality.py: Module under test (validator, QualityReport, helper)
    - persona.py: Integration check — generate() must attach quality metrics
    - pytest: Test framework
"""

from __future__ import annotations

import pytest

from utils.response_quality import (
    QualityReport,
    ResponseQualityValidator,
    check_response_quality,
)


# ---------------------------------------------------------------------------
# Unit tests: ResponseQualityValidator
# ---------------------------------------------------------------------------

class TestResponseQualityValidator:
    """Direct tests on the validator class."""

    def setup_method(self):
        self.v = ResponseQualityValidator()

    # ---- Placeholder detection ----

    def test_placeholder_triggers_fail(self):
        """Known placeholder phrases must produce a failing score."""
        bad_responses = [
            "That's definitely worth exploring. I love diving into new topics.",
            "I'm not sure about that one.",
            "That's interesting. Let me think about this.",
            "I apologize, but I'm having trouble processing right now. Please try again in a moment.",
        ]
        for resp in bad_responses:
            report = self.v.check(resp, "some user input")
            assert report.placeholder_detected, f"Should detect placeholder in: {resp!r}"
            assert not report.is_acceptable, f"Should fail for placeholder: {resp!r}"

    def test_clean_response_passes(self):
        """A substantive, on-topic response should not be flagged as a placeholder."""
        clean = (
            "Quantum tunneling is when a particle passes through a potential barrier "
            "that classical mechanics says it shouldn't be able to. The key is that "
            "particles have wave-like properties — the wavefunction can 'leak' through "
            "the barrier with some non-zero probability."
        )
        report = self.v.check(clean, "explain quantum tunneling")
        assert not report.placeholder_detected
        assert report.is_acceptable, f"Clean response should pass; score={report.score}"

    # ---- Length check ----

    def test_too_short_fails(self):
        """Responses under the minimum character threshold must fail the length check."""
        report = self.v.check("Yep.", "what is 2 plus 2")
        assert not report.length_ok
        assert not report.is_acceptable

    def test_adequate_length_passes_length_check(self):
        report = self.v.check("That comes out to 4. Easy math, bro!", "what is 2+2")
        assert report.length_ok

    # ---- Specificity check ----

    def test_off_topic_response_penalised(self):
        """A response that shares no meaningful tokens with the user's question is
        penalised for low specificity."""
        # User asks about Python, response is about cooking
        user = "how do i use decorators in python programming"
        resp = (
            "Bro, let me tell you about the best recipe for tacos — first you marinate "
            "the chicken for at least two hours, then season generously with cumin and chili."
        )
        report = self.v.check(resp, user)
        # Specificity penalty should be applied (tokens like 'python', 'decorators' absent)
        assert "shares no meaningful tokens" in " ".join(report.issues)

    # ---- Score range ----

    def test_score_is_within_range(self):
        """Score must always be between 0 and 100."""
        cases = [
            ("", ""),
            ("That's interesting.", "hi"),
            ("Real talk: 2 + 2 = 4. Easy math!", "what is 2 + 2"),
        ]
        for resp, user in cases:
            report = self.v.check(resp, user)
            assert 0.0 <= report.score <= 100.0, f"Score out of range: {report.score}"

    # ---- QualityReport.summary() ----

    def test_summary_contains_score(self):
        report = self.v.check("That's interesting.", "hi there")
        summary = report.summary()
        assert "quality=" in summary

    def test_summary_pass_label(self):
        clean = (
            "Quantum tunneling lets particles move through classically forbidden barriers "
            "because the wavefunction has non-zero amplitude on the other side."
        )
        report = self.v.check(clean, "quantum tunneling")
        assert "PASS" in report.summary()

    def test_summary_fail_label(self):
        report = self.v.check("I'm not sure about that.", "some question")
        assert "LOW-QUALITY" in report.summary()


# ---------------------------------------------------------------------------
# Unit tests: check_response_quality convenience wrapper
# ---------------------------------------------------------------------------

class TestCheckResponseQualityHelper:
    """Tests for the module-level convenience function."""

    def test_returns_quality_report(self):
        result = check_response_quality("Some response text that is long enough to pass.", "user input")
        assert isinstance(result, QualityReport)

    def test_no_user_text_still_works(self):
        """Calling with no user_text should not raise."""
        result = check_response_quality("A decent response that has enough characters.")
        assert isinstance(result, QualityReport)


# ---------------------------------------------------------------------------
# Integration test: PersonaEngine surfaces quality metrics
# ---------------------------------------------------------------------------

class TestPersonaEngineQualityIntegration:
    """Verify that PersonaEngine.generate() attaches quality metrics to the
    response so callers have visibility into response quality at runtime."""

    def test_generate_attaches_quality_score(self):
        """debug_metrics on the returned response must include response_quality_score."""
        from persona import PersonaEngine

        engine = PersonaEngine()
        resp = engine.generate("What is quantum computing?", mode="Auto")
        metrics = getattr(resp, "debug_metrics", {})
        assert "response_quality_score" in metrics, (
            "PersonaEngine.generate() should attach response_quality_score to debug_metrics"
        )
        score = metrics["response_quality_score"]
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 100.0

    def test_arithmetic_question_gets_specific_answer(self):
        """A simple arithmetic question should not trigger a generic placeholder response
        and should contain the correct numerical result."""
        from persona import PersonaEngine

        engine = PersonaEngine()
        resp = engine.generate("what is 12 * 7", mode="Auto")
        # Response must not be flagged as a placeholder
        report = check_response_quality(resp.text, "what is 12 * 7")
        assert not report.placeholder_detected, (
            f"Arithmetic question got a placeholder response: {resp.text!r}"
        )
        # Response must contain the correct answer (84)
        assert "84" in resp.text, (
            f"Expected '84' in arithmetic response, got: {resp.text!r}"
        )
