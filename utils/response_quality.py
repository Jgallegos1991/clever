"""utils/response_quality.py - Response Quality Validation Layer for Clever

Why: Enforce a minimum quality bar on every generated response so users never
     receive generic placeholder text that erodes trust in the cognitive
     partnership. Provides scoring, detection of low-quality patterns, and
     structured audit metadata so the evolution engine can track improvement.

Where: Sits between PersonaEngine._generate_impl() and the final PersonaResponse
       construction. Called after mode-handler text is assembled, before the Jay
       wrapper is applied.

How: A stateless ResponseQualityValidator class scans response text against
     a curated list of placeholder fingerprints, checks minimum content length,
     and computes a 0-100 quality score. Returns a QualityReport dataclass that
     callers log via the debug system.

File Usage:
    - Primary callers: persona.py PersonaEngine._generate_impl()
    - Key dependencies: None (stdlib only, offline-safe)
    - Data flow: accepts raw response string → returns QualityReport with
      score and issues list

Connects to:
    - persona.py: Quality check integrated into response generation pipeline
    - debug_config.py: Score and issues logged at INFO / WARNING level
    - evolution_engine.py: Quality score surfaced in interaction log for
      continuous improvement tracking

Performance Notes:
    - Memory usage: Negligible — pure string operations
    - CPU impact: Sub-millisecond per call; no external I/O
    - Scaling limits: N/A — single-user, single-process

Critical Dependencies:
    - Python 3.8+ standard library (re, dataclasses, typing)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Placeholder fingerprints — phrases that signal a generic / low-quality
# response that doesn't actually address the user's input.
# Each entry is a (regex_pattern, human_readable_label) tuple so that
# QualityReport.issues contains meaningful descriptions, not raw regex.
# ---------------------------------------------------------------------------
_PLACEHOLDER_PATTERNS: List[Tuple[str, str]] = [
    (r"\bi'm not sure\b",                                "uncertainty phrase: \"I'm not sure\""),
    (r"\bthat'?s interesting\b",                         "filler affirmation: \"That's interesting\""),
    (r"\bthat is interesting\b",                         "filler affirmation: \"That is interesting\""),
    (r"\bi don't know\b",                                "uncertainty phrase: \"I don't know\""),
    (r"\bi cannot (help|answer|assist)\b",               "deflection phrase: \"I cannot help/answer\""),
    (r"\bcould you (please )?clarify\b",                 "deflection phrase: \"Could you clarify\""),
    (r"\bi apologize[,.]? but i'?m having trouble processing\b", "error fallback: \"I apologize, but I'm having trouble\""),
    (r"\bplease try again in a moment\b",                "error fallback: \"Please try again in a moment\""),
    (r"\bthat'?s definitely worth exploring\b",          "generic placeholder: \"That's definitely worth exploring\""),
    (r"\bwhat'?s your angle on this\b",                  "generic deflection: \"What's your angle on this\""),
    (r"\blet me think about that with you\b",            "generic filler: \"Let me think about that with you\""),
    (r"\binteresting question\.\s*let me think\b",       "generic filler: \"Interesting question. Let me think\""),
    (r"\bi (love|enjoy) diving into new topics\b",       "generic filler: \"I love/enjoy diving into new topics\""),
    (r"\bhow does this (context )?change your perspective\b", "generic deflection: \"How does this change your perspective\""),
    (r"\bwant me to break this down step by step\b",     "generic filler: \"Want me to break this down step by step\""),
    (r"\bwould you like me to dive deeper into this topic\b", "generic filler: \"Would you like me to dive deeper\""),
    (r"\bshould i explore related areas\b",              "generic filler: \"Should I explore related areas\""),
]

# Minimum acceptable response length (characters, stripped)
_MIN_LENGTH = 30

# Weights for scoring sub-factors (must sum to 1.0)
_WEIGHT_PLACEHOLDER = 0.50   # No placeholder patterns
_WEIGHT_LENGTH = 0.25         # Adequate length
_WEIGHT_SPECIFICITY = 0.25    # Contains topic-relevant tokens

# Common stopwords excluded from the specificity token check.
# Keeping this as a module-level constant makes it easy to extend.
_COMMON_STOPWORDS: frozenset = frozenset({
    "what", "that", "this", "with", "have", "just", "been",
    "will", "your", "from", "they", "their", "about", "when",
    "where", "which", "should", "could", "would", "there",
    "then", "than", "does", "dont", "isnt", "arent", "wasnt",
    "were", "want", "need", "make", "some", "more", "into",
    "also", "even", "like", "only", "very", "such", "much",
})


@dataclass
class QualityReport:
    """Structured result from ResponseQualityValidator.check().

    Why: Provide a machine-readable audit trail for every response so the
         evolution engine and debug tooling can track quality trends over time.
    Where: Produced by ResponseQualityValidator.check(); consumed by
           PersonaEngine._generate_impl() for logging.
    How: Immutable dataclass with a numeric score (0–100) and an issues list
         that enumerates every failing criterion.
    """

    score: float                      # 0–100; higher is better
    issues: List[str] = field(default_factory=list)
    placeholder_detected: bool = False
    length_ok: bool = True
    is_acceptable: bool = True        # True when score >= threshold

    def summary(self) -> str:
        """One-line summary for log output."""
        tag = "✅ PASS" if self.is_acceptable else "⚠️  LOW-QUALITY"
        return f"{tag} quality={self.score:.0f}/100 issues={self.issues}"


class ResponseQualityValidator:
    """Stateless validator that scores a response string.

    Why: Centralise all quality heuristics in one place so the PersonaEngine
         remains focused on generation while this class handles enforcement.
    Where: Instantiated once as a class-level constant in persona.py; called
           inside _generate_impl() before returning the PersonaResponse.
    How: Compiles placeholder regex patterns once at instantiation, then runs
         three sub-checks (placeholder, length, specificity) and aggregates a
         weighted score.

    Connects to:
        - persona.py: PersonaEngine uses _quality_validator.check()
        - debug_config.py: caller logs QualityReport.summary()
    """

    # Score threshold below which a response is flagged as low-quality
    ACCEPTABLE_THRESHOLD = 55.0

    def __init__(self) -> None:
        """Compile regex patterns once for performance.

        Why: Compiling patterns at instantiation avoids repeated compilation
             overhead on every check() call.
        Where: Called once when the module-level _validator singleton is created.
        How: Each (pattern, label) tuple is compiled; labels stored separately
             for human-readable error messages.
        """
        self._compiled: List[Tuple[re.Pattern, str]] = [
            (re.compile(pattern, re.IGNORECASE), label)
            for pattern, label in _PLACEHOLDER_PATTERNS
        ]

    def check(self, response_text: str, user_text: str = "") -> QualityReport:
        """Score a response and return a QualityReport.

        Why: Provide a fast, deterministic quality gate before returning a
             response to the user.
        Where: Called by PersonaEngine._generate_impl() after assembling the
               final response string.
        How: Three weighted sub-scores are combined:
             1. Placeholder check  (50 pts) — penalise any matching phrases
             2. Length check        (25 pts) — penalise responses below minimum
             3. Specificity check   (25 pts) — reward topic token overlap

        Args:
            response_text: The assembled response string to evaluate.
            user_text: Original user input used for specificity scoring.

        Returns:
            QualityReport with score, issues list, and pass/fail flag.

        File Usage:
            - Called by: persona.py PersonaEngine._generate_impl()
            - Calls to: None (pure computation)
            - Data flow: response string + user string → QualityReport

        Connects to:
            - persona.py: Primary consumer of returned QualityReport
            - debug_config.py: Caller logs the report summary
        """
        issues: List[str] = []
        text = (response_text or "").strip()
        user_lower = (user_text or "").lower()

        # ---- Sub-score 1: Placeholder detection ----
        placeholder_score = _WEIGHT_PLACEHOLDER * 100
        placeholder_detected = False
        for compiled_pattern, label in self._compiled:
            if compiled_pattern.search(text):
                placeholder_detected = True
                issues.append(label)
                placeholder_score = 0.0
                break  # One hit is enough to zero out this component

        # ---- Sub-score 2: Length check ----
        length_ok = len(text) >= _MIN_LENGTH
        length_score = (_WEIGHT_LENGTH * 100) if length_ok else 0.0
        if not length_ok:
            issues.append(f"response too short ({len(text)} chars, minimum {_MIN_LENGTH})")

        # ---- Sub-score 3: Specificity check ----
        # Reward responses that re-use at least one meaningful token from the
        # user's input (basic proxy for topical relevance).
        specificity_score = _WEIGHT_SPECIFICITY * 100
        if user_lower:
            user_tokens = {
                tok for tok in re.split(r"\W+", user_lower)
                if len(tok) > 3 and tok not in _COMMON_STOPWORDS
            }
            text_lower = text.lower()
            if user_tokens and not any(tok in text_lower for tok in user_tokens):
                specificity_score = 0.0
                issues.append("response shares no meaningful tokens with user input")

        score = placeholder_score + length_score + specificity_score
        is_acceptable = score >= self.ACCEPTABLE_THRESHOLD

        return QualityReport(
            score=score,
            issues=issues,
            placeholder_detected=placeholder_detected,
            length_ok=length_ok,
            is_acceptable=is_acceptable,
        )


# Module-level singleton — import and reuse rather than reinstantiate
_validator = ResponseQualityValidator()


def check_response_quality(response_text: str, user_text: str = "") -> QualityReport:
    """Convenience wrapper around the module-level validator singleton.

    Why: Allow callers to import a single function instead of managing a class
         instance, keeping the API minimal and easy to use.
    Where: Imported by persona.py as a drop-in quality gate.
    How: Delegates to the pre-compiled _validator singleton.

    Args:
        response_text: The assembled response string to evaluate.
        user_text: Original user input used for specificity scoring.

    Returns:
        QualityReport with score, issues, and pass/fail status.
    """
    return _validator.check(response_text, user_text)
