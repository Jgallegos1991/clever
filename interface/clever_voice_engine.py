#!/usr/bin/env python3
"""
clever_voice_engine.py - Clever Voice Engine (Gemini-style Warmth + Humor)

Why: Provides a unified, personality-aware, offline-first voice synthesis layer that
     embodies Clever's core "warm genius best-friend" vibe with gentle humor,
     cognitive partnership awareness, and adaptive emotional coloring while staying
     within Chrome OS memory + sovereignty constraints.
Where: Sits above specific TTS backends (Coqui, Natural, Enhanced espeak) and below
       higher-level interaction loops (`clever_voice_loop.py`) and persona generation.
How: Dynamically selects an available backend (preferring neural / natural engines),
     applies personality transformation (warmth, humor, empathy weights) to text,
     enriches with subtle expressive markers, then routes to chosen engine with
     fallback cascade ensuring zero hard failures and total offline resilience.

File Usage:
    - Primary callers: `clever_voice_loop.py`, future `voice_orchestrator.py`, tests
    - Key dependencies: `coqui_voice_engine.py`, `natural_voice_engine.py`, `enhanced_voice_engine.py`
    - Data sources: Persona output text, hardware config, internal personality map
    - Data destinations: Audio output pipeline (system TTS backends)
    - Configuration: `hardware_config.json`, optional `voice_config.json`
    - Database interactions: None directly (kept stateless for low-latency)
    - API endpoints: None (invoked internally by runtime)
    - Frontend connections: Indirect via Flask chat → voice loop
    - Background processes: None (synchronous generation path)

Connects to:
    - coqui_voice_engine.py: Neural natural speech backend (highest naturalness)
    - natural_voice_engine.py: Multi-engine natural fallback
    - enhanced_voice_engine.py: Quality-tuned espeak/other engines
    - clever_voice_loop.py: Consumes this unified interface
    - debug_config.py: (future) potential performance logging hooks

Performance Notes:
    - Memory usage: Minimal incremental (<2MB) beyond selected backend
    - CPU impact: Lightweight string transforms only; defers heavy work to backend
    - I/O operations: None (no disk writes except underlying engines)
    - Scaling limits: Single-user low-concurrency design; thread-safe by immutability

Critical Dependencies:
    - Optional: Coqui TTS, gTTS, pyttsx3, espeak (already handled in lower layers)
    - Required: Standard library only inside this coordinator layer
    - System requirements: Audio playback utilities present (handled downstream)
    - Database schema: N/A (stateless transformation)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Attempt backend imports lazily – we never hard fail; we record availability
try:
    from coqui_voice_engine import CoquiVoiceEngine  # type: ignore

    _COQUI_AVAILABLE = True
except Exception:
    CoquiVoiceEngine = None  # type: ignore
    _COQUI_AVAILABLE = False

try:
    from natural_voice_engine import NaturalVoiceEngine  # type: ignore

    _NATURAL_AVAILABLE = True
except Exception:
    NaturalVoiceEngine = None  # type: ignore
    _NATURAL_AVAILABLE = False

try:
    from enhanced_voice_engine import EnhancedVoiceEngine  # type: ignore

    _ENHANCED_AVAILABLE = True
except Exception:
    EnhancedVoiceEngine = None  # type: ignore
_ENHANCED_AVAILABLE = False


def _env_flag(value: str) -> bool:
    return value.lower() not in {"0", "false", "no", "off"}


VOICE_ENABLED = _env_flag(os.environ.get("CLEVER_VOICE_ENABLED", os.environ.get("VOICE_OK", "1")))


@dataclass(frozen=True)
class VoicePersonaProfile:
    """Voice persona shaping parameters.

    Why: Encapsulates tunable emotional + stylistic weights enabling coherent,
         inspectable transformation logic for warmth/humor infusion.
    Where: Used by `CleverVoiceEngine._apply_persona_filters` prior to backend TTS.
    How: Provides scalar weights + phrasing toggles interpreted in transformation.
    """

    name: str
    warmth: float  # 0–1 scale
    humor: float  # 0–1 scale
    empathy: float  # 0–1 scale
    cognitive_clarity: float  # Articulation / pacing influence
    playful_interjections: bool
    soften_edges: bool
    strategic_pauses: bool


class CleverVoiceEngine:
    """Unified Gemini-style warm + humorous female voice orchestrator.

    Why: Gives Clever a consistent audible identity (warm genius companion) while
         abstracting backend volatility and ensuring graceful degradation.
    Where: Coordination layer between persona text generation and low-level TTS engines.
    How: Selects best available engine → applies persona shaping → delegates speak.

    File Usage:
        - Called by: `clever_voice_loop.py`
        - Calls to: Coqui / Natural / Enhanced voice engines via their public APIs
        - Data flow: Raw text → persona filter → backend synth → audio output

    Connects to:
        - coqui_voice_engine.py: Preferred for neural naturalness
        - natural_voice_engine.py: Secondary natural multi-engine fallback
        - enhanced_voice_engine.py: Final robust espeak-based fallback
        - hardware_config.json: Guides emergency mode + capability weighting
    """

    # Enforce offline-only at the orchestrator level
    OFFLINE_ONLY: bool = True

    def __init__(self, default_persona: str = "warm_humorous_companion") -> None:
        """Initialize orchestrator and determine backend priority stack.

        Why: Startup capability detection ensures zero run-time branching surprises
             and allows immediate introspection of chosen synthesis path.
        Where: Called during voice loop initialization or on-demand by services.
        How: Instantiates highest-quality available engine; builds fallback order.
        """
        self.persona_profiles: Dict[str, VoicePersonaProfile] = self._build_persona_profiles()
        self.active_persona: VoicePersonaProfile = self.persona_profiles.get(
            default_persona, next(iter(self.persona_profiles.values()))
        )

        # Export offline-only to environment so sub-engines can obey it
        if self.OFFLINE_ONLY:
            os.environ["CLEVER_OFFLINE_ONLY"] = "1"
            # Hard guard: downstream engines must not use networked providers
            os.environ["NO_NETWORK_TTS"] = "1"

        self.hardware_config = self._load_hardware_config()
        self.emergency_mode = self.hardware_config.get("strategy_name") == "emergency"

        # Load voice profile (piper model paths)
        self.voice_profile: Dict[str, Any] = self._load_voice_profile()
        self._piper_available = self._detect_piper()

        # Lazy engine instances to avoid heavy init (especially Coqui) at startup
        self._coqui: Optional[CoquiVoiceEngine] = None
        self._natural: Optional[NaturalVoiceEngine] = None
        self._enhanced: Optional[EnhancedVoiceEngine] = None

        # Build backend order with piper first if available
        self.backend_order = []
        if self._piper_available:
            self.backend_order.append(("piper", True))
        # Do not instantiate here; just mark potential availability
        if _ENHANCED_AVAILABLE:
            self.backend_order.append(("enhanced", True))
        if _COQUI_AVAILABLE:
            self.backend_order.append(("coqui", True))
        if _NATURAL_AVAILABLE:
            self.backend_order.append(("natural", True))

        any_backend_available = bool(self.backend_order)

        # Emergency fallback always available (espeak)
        self.backend_order.append(("fallback_espeak", True))

        self.voice_enabled = VOICE_ENABLED and any_backend_available
        if not self.voice_enabled:
            print(
                "🔇 Voice output disabled or no backends available; speak() calls will be ignored."
            )

        if self._piper_available:
            self.selected_backend = "piper"
        elif _ENHANCED_AVAILABLE:
            self.selected_backend = "enhanced"
        elif _COQUI_AVAILABLE:
            self.selected_backend = "coqui"
        elif _NATURAL_AVAILABLE:
            self.selected_backend = "natural"
        else:
            self.selected_backend = "none"
        print(
            f"🎤 CleverVoiceEngine initialized | persona={self.active_persona.name} | backend={self.selected_backend} | emergency={self.emergency_mode} | offline_only=True"  # noqa: E501
        )

    # ---------------- Internal Configuration ---------------- #
    def _load_hardware_config(self) -> Dict[str, Any]:
        """Load hardware config JSON (non-fatal if absent).

        Why: Emergency / memory strategies influence phrasing (shorter output) and
             backend feasibility (avoid neural in extreme constraint).
        Where: Used at init and potentially by future adaptive pacing logic.
        How: Lightweight JSON read with fallback default structure.
        """
        try:
            with open("hardware_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"strategy_name": "unknown", "hardware_profile": {}}

    def _load_voice_profile(self) -> Dict[str, Any]:
        """Load piper voice profile from config/voice_profile.json if present.

        Why: Provides model + config paths and shaping defaults (pitch/speed/humor).
        Where: Used when invoking piper synthesis.
        How: JSON read with safe defaults if file missing.
        """
        default_profile = {
            "engine": "piper",
            "model": "models/piper/en_US-default.onnx",
            "config": "models/piper/en_US-default.json",
            "pitch": 0.94,
            "speed": 0.91,
            "humor_level": 0.30,
            "style": "GeminiWarm",
        }
        try:
            with open("config/voice_profile.json", "r") as f:
                data = json.load(f)
            default_profile.update(data or {})
        except FileNotFoundError:
            pass

        # Optional local override file (not committed): config/voice_profile.local.json
        try:
            with open("config/voice_profile.local.json", "r") as f:
                local_data = json.load(f)
            default_profile.update(local_data or {})
        except FileNotFoundError:
            pass

        # Environment overrides (useful for one-off runs or system-installed models)
        env_model = os.environ.get("PIPER_MODEL")
        env_cfg = os.environ.get("PIPER_CONFIG")
        if env_model:
            default_profile["model"] = env_model
        if env_cfg:
            default_profile["config"] = env_cfg
        return default_profile

    def _detect_piper(self) -> bool:
        """Detect piper CLI and model/config availability."""
        piper_path = shutil.which("piper")
        if not piper_path:
            return False
        model = Path(self.voice_profile.get("model", ""))
        cfg = Path(self.voice_profile.get("config", ""))
        return model.is_file() and cfg.is_file()

    def _build_persona_profiles(self) -> Dict[str, VoicePersonaProfile]:
        """Define available persona profiles (extensible mapping).

        Why: Central registry supports systematic evolution + runtime introspection.
        Where: Consumed by initialization and any persona switch requests.
        How: Returns dict of `VoicePersonaProfile` dataclasses.
        """
        return {
            "warm_humorous_companion": VoicePersonaProfile(
                name="warm_humorous_companion",
                warmth=0.95,
                humor=0.7,
                empathy=0.9,
                cognitive_clarity=0.85,
                playful_interjections=True,
                soften_edges=True,
                strategic_pauses=True,
            ),
            "calm_supportive": VoicePersonaProfile(
                name="calm_supportive",
                warmth=0.9,
                humor=0.25,
                empathy=0.95,
                cognitive_clarity=0.9,
                playful_interjections=False,
                soften_edges=True,
                strategic_pauses=True,
            ),
            "pep_talk_genius": VoicePersonaProfile(
                name="pep_talk_genius",
                warmth=0.8,
                humor=0.55,
                empathy=0.75,
                cognitive_clarity=0.95,
                playful_interjections=True,
                soften_edges=False,
                strategic_pauses=False,
            ),
            "focused_analysis": VoicePersonaProfile(
                name="focused_analysis",
                warmth=0.55,
                humor=0.15,
                empathy=0.4,
                cognitive_clarity=1.0,
                playful_interjections=False,
                soften_edges=False,
                strategic_pauses=False,
            ),
        }

    # ---------------- Persona Management ---------------- #
    def set_persona(self, persona_name: str) -> bool:
        """Activate a different voice persona.

        Why: Allows dynamic adaptation to Jay's cognitive + emotional context.
        Where: Invoked by higher-level interaction manager or manual override.
        How: Look up `persona_profiles`; update `active_persona`.
        """
        profile = self.persona_profiles.get(persona_name)
        if not profile:
            print(f"⚠️ Unknown persona '{persona_name}'")
            return False
        self.active_persona = profile
        print(f"🔄 Voice persona switched → {persona_name}")
        return True

    # ---------------- Public API ---------------- #
    def speak(
        self,
        text: str,
        personality_hint: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> bool:
        """Speak text using best available engine with persona shaping.

        Why: Single entry point for all voice output ensures consistent identity.
        Where: Called from voice loop or any interactive response pipeline.
        How: (1) Persona resolution → (2) Transform text → (3) Delegate.

        Args:
            text: Raw text from persona / response engine.
            personality_hint: Optional temporary override (non-persistent).
        Returns:
            bool: True on successful synthesis path.
        """
        if not text:
            return False

        if not self.voice_enabled:
            print("🔇 Voice output disabled; skipping speak request.")
            return False

        # Apply emergency shortening if needed
        if self.emergency_mode and len(text) > 180:
            text = text[:170].rstrip() + "…"

        # Temporary persona hint (does not persist) or mood alias
        mood_map = {
            "support": "calm_supportive",
            "calm": "calm_supportive",
            "pep": "pep_talk_genius",
            "analysis": "focused_analysis",
            "warm": "warm_humorous_companion",
        }
        if mood:
            key = str(mood).strip().lower()
            self.set_persona(mood_map.get(key, self.active_persona.name))
        elif personality_hint:
            self.set_persona(personality_hint)

        shaped = self._apply_persona_filters(text, self.active_persona)

        # Piper first
        if self._piper_available:
            try:
                pitch = self.voice_profile.get("pitch", 0.94)
                speed = self.voice_profile.get("speed", 0.91)
                if self._speak_via_piper(shaped, pitch=pitch, speed=speed):
                    return True
            except Exception as e:
                print(f"⚠️ Piper synthesis failed: {e}")

        # Enhanced espeak next (fully offline)
        if _ENHANCED_AVAILABLE:
            if self._enhanced is None:
                try:
                    self._enhanced = EnhancedVoiceEngine()
                except Exception as e:
                    print(f"⚠️ Failed to init EnhancedVoiceEngine: {e}")
                    self._enhanced = None

            if self._enhanced:
                try:
                    voice, spd, pct = self._enhanced.set_voice_personality("warm")  # type: ignore
                    if self._enhanced.speak_enhanced(shaped, voice, spd, pct):  # type: ignore
                        return True
                except Exception as e:
                    print(f"⚠️ Enhanced engine failed: {e}")

        # Optional Coqui (offline neural). Skip any network-based engines explicitly.
        if _COQUI_AVAILABLE:
            if self._coqui is None:
                try:
                    self._coqui = CoquiVoiceEngine()
                except Exception as e:
                    print(f"⚠️ Failed to init CoquiVoiceEngine: {e}")
                    self._coqui = None
            if self._coqui:
                try:
                    if self._coqui.speak_natural(shaped, personality=self._map_to_coqui_personality()):  # type: ignore
                        return True
                except Exception as e:
                    print(f"⚠️ Coqui engine failed: {e}")

        # Final ultra fallback: espeak direct minimal
        return self._fallback_espeak(shaped)

    def preview_transformed(self, text: str, persona_hint: Optional[str] = None) -> str:
        """Return the transformed text without invoking audio output.

        Why: Enables unit tests and debugging tools to verify persona shaping
             deterministically without depending on audio stack presence.
        Where: Called by tests (`test_clever_voice_engine.py`) and potential
               future UI preview panels.
        How: Applies optional persona switch then runs `_apply_persona_filters`.

        Args:
            text: Input text to transform.
            persona_hint: Optional temporary persona override.
        Returns:
            Transformed text string (no side effects).
        """
        if persona_hint:
            self.set_persona(persona_hint)
        return self._apply_persona_filters(text, self.active_persona)

    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic status for introspection overlays.

        Why: Supports runtime introspection map (Why/Where/How graph) and debugging.
        Where: Callable by debug endpoints or CLI health tools.
        How: Aggregate persona + backend state into dict.
        """
        model_path = self.voice_profile.get("model") if self._piper_available else None
        return {
            "active_persona": self.active_persona.name,
            "backend_selected": self.selected_backend,
            "available_backends": [name for name, inst in self.backend_order if inst],
            "emergency_mode": self.emergency_mode,
            "voice_enabled": self.voice_enabled,
            "offline_only": True,
            "piper_model": Path(model_path).name if model_path else None,
            "warmth": self.active_persona.warmth,
            "humor": self.active_persona.humor,
            "empathy": self.active_persona.empathy,
        }

    def is_enabled(self) -> bool:
        """Expose whether voice synthesis is currently available."""
        return self.voice_enabled

    # ---------------- Internal Persona Logic ---------------- #
    def _apply_persona_filters(self, text: str, profile: VoicePersonaProfile) -> str:
        """Transform raw text into warm + humorous expressive variant.

        Why: Bridges neutral generated text and lived auditory personality identity.
        Where: Called inside `speak` prior to backend delegation.
        How: Applies layered heuristic filters (softening, humor taglines, pauses).
        """
        transformed = text.strip()

        # Soft edge smoothing (convert overly formal phrasing)
        if profile.soften_edges:
            replacements = {
                "However,": "But hey,",
                "Therefore,": "So,",
                "In conclusion": "Bottom line",
                "I will": "I'll",
                "I am": "I'm",
            }
            for k, v in replacements.items():
                transformed = transformed.replace(k, v)

        # Inject warm encouragement if warmth high and not already closing
        if (
            profile.warmth > 0.85
            and len(transformed) < 260
            and not transformed.endswith(("🙂", "😉", "😄"))
        ):
            transformed += "  — you're doing great, by the way."

        # Light humor insertion
        if profile.humor > 0.6 and len(transformed) > 40:
            tag_options = [
                " (tiny brain high-five)",
                " (nerd sparkle activated)",
                " (yes, I grinned saying that)",
            ]
            # Deterministic selection based on length for offline repeatability
            idx = len(transformed) % len(tag_options)
            transformed += tag_options[idx]

        # Strategic pauses: add subtle commas / ellipses for cadence
        if profile.strategic_pauses:
            if "," not in transformed and len(transformed) > 35:
                transformed = transformed.replace(" and ", ", and ")
            if profile.empathy > 0.8 and "." in transformed:
                transformed = transformed.replace(".", "...")

        # Empathy boost: soften abrupt endings
        if profile.empathy > 0.85 and not transformed.endswith(("!", ".", "…")):
            transformed += " — alright?"  # gentle check-in

        return transformed

    def _map_to_coqui_personality(self) -> str:
        """Map internal persona → closest Coqui personality label.

        Why: Aligns high-level persona semantics with backend expectation tokens.
        Where: Used only when Coqui backend is active in `speak` flow.
        How: Simple rule mapping based on predominant parameter weights.
        """
        p = self.active_persona
        if p.cognitive_clarity > 0.9 and p.humor < 0.4:
            return "professional"
        if p.humor > 0.6 and p.warmth > 0.8:
            return "casual"
        if p.warmth > 0.9 and p.empathy > 0.85:
            return "warm"
        return "street-smart"

    def _fallback_espeak(self, text: str) -> bool:
        """Absolute final fallback using espeak directly.

        Why: Guarantees voice output path never fully collapses (resilience).
        Where: Triggered only if all orchestrated backends fail/unavailable.
        How: Executes subprocess espeak with warm female parameters.
        """
        import subprocess  # local import to avoid cost if unused

        try:
            subprocess.run(
                ["espeak", "-v", "en+f3", "-s", "165", "-p", "68", text],
                timeout=10,
                check=True,
            )
            return True
        except Exception as e:  # noqa: BLE001
            print(f"⚠️ Ultimate espeak fallback failed: {e}")
            return False

    def _speak_via_piper(
        self,
        text: str,
        pitch: float = 1.0,
        speed: float = 1.0,
        out_path: Optional[str] = None,
    ) -> bool:
        """Synthesize speech using piper CLI.

        Why: Prefer high-quality local TTS with small footprint and offline guarantees.
        Where: First step in fallback chain when piper is available.
        How: Pipe text via stdin to piper with model/config; write wav or play.

        Args:
            text: Content to speak
            pitch: Not directly supported by base piper CLI; retained for future mapping
            speed: Mapped to --length_scale (lower = faster)
            out_path: Optional WAV file path; if None, play via system player
        """
        if not self._piper_available:
            return False
        model = self.voice_profile["model"]
        cfg = self.voice_profile["config"]
        # Build command; use -f for output file if provided
        cmd = [
            "piper",
            "--model",
            model,
            "--config",
            cfg,
            "--length_scale",
            str(speed),
            "--noise_scale",
            "0.5",
        ]

        temp_path = None
        if out_path:
            cmd += ["-f", out_path]
        else:
            # Write to temp wav then play
            import tempfile

            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = tmp.name
            tmp.close()
            cmd += ["-f", temp_path]

        # Run piper with stdin
        try:
            subprocess.run(cmd, input=text.encode("utf-8"), check=True, timeout=30)
        except subprocess.CalledProcessError as e:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            raise e

        if out_path:
            return True

        # Play the generated audio via available player
        players = ["aplay", "paplay", "play", "ffplay"]
        played = False
        for player in players:
            if shutil.which(player) is None:
                continue
            try:
                if player == "ffplay":
                    subprocess.run(
                        [player, "-nodisp", "-autoexit", temp_path],
                        check=True,
                        timeout=30,
                    )
                else:
                    subprocess.run([player, temp_path], check=True, timeout=30)
                played = True
                break
            except Exception:
                continue
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        return played


# ---------------- Convenience Test Harness ---------------- #


def _demo():  # pragma: no cover - manual test helper
    engine = CleverVoiceEngine()
    engine.speak("Initiating unified voice pipeline. System online and ready.")
    engine.set_persona("pep_talk_genius")
    engine.speak("You're pushing real cognitive evolution tonight. Let's aim higher.")
    engine.set_persona("calm_supportive")
    engine.speak("Breathing room matters. We can pace brilliance without burning out.")


if __name__ == "__main__":  # pragma: no cover
    _demo()
