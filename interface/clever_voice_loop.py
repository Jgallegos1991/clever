#!/usr/bin/env python3
"""
clever        # Initialize natural voice engine if available (prioritize over enhanced)
        if NATURAL_VOICE_AVAILABLE:
            try:
                self.natural_voice = NaturalVoiceEngine()
                # Set Clever's personality to friendly (natural female)
                self.voice_params = ('friendly', 165, 68)  # personality, speed, pitch
                print("✨ Natural voice engine loaded with friendly female personality")
                self.voice_engine_type = 'natural'
            except Exception as e:
                print(f"⚠️  Natural voice engine failed to load: {e}")
                self.natural_voice = None
                self.voice_engine_type = 'enhanced'
        else:
            self.natural_voice = None
            self.voice_engine_type = 'enhanced'
        
        # Fallback to enhanced voice engine
        if self.voice_engine_type == 'enhanced' and ENHANCED_VOICE_AVAILABLE:
            try:
                self.enhanced_voice = EnhancedVoiceEngine()
                # Set Clever's personality to street-smart
                self.voice_params = self.enhanced_voice.set_voice_personality('street-smart')
                print("✨ Enhanced voice engine loaded with street-smart personality")
            except Exception as e:
                print(f"⚠️  Enhanced voice engine failed to load: {e}")
                self.enhanced_voice = None
                self.voice_params = ('en+f3', 165, 68)  # Default female street-smart parameters
        else:
            if not hasattr(self, 'enhanced_voice'):
                self.enhanced_voice = None
            if not hasattr(self, 'voice_params'):
                self.voice_params = ('en+f3', 165, 68)  # Default female street-smart parameters - Lightwei    def __init__(self):
        \"\"\"Initialize l    def speak_lightweight(self, text: str, voice: str = 'en-us') -> bool:
        \"\"\"Enhanced text-to-speech with better voice quality\"\"\"
        if len(text) > 200:  # Limit text length for memory efficiency
            text = text[:200] + \"...\"
        
        # Try enhanced voice engine first
        if self.enhanced_voice:
            try:
                voice_id, speed, pitch = self.voice_params
                success = self.enhanced_voice.speak_enhanced(text, voice_id, speed, pitch)
                if success:
                    return True
                else:
                    print(\"⚠️  Enhanced voice failed, falling back to espeak\")
            except Exception as e:
                print(f\"⚠️  Enhanced voice error: {e}, falling back to espeak\")
        
        # Fallback to basic espeak
        try:
            # Use enhanced espeak parameters for better quality
            subprocess.run(['espeak', '-v', voice, '-s', '170', '-p', '45', '-a', '80', text], 
                          timeout=10, check=True)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            print(\"⚠️  Text-to-speech not available\")
            return Falseice system with device constraints\"\"\"
        self.memory_limit_mb = 50  # Stay under emergency mode limits
        self.microphone_available = self._check_microphone()
        self.audio_system_ready = self._check_audio_system()
        
        # Initialize enhanced voice engine if available
        if ENHANCED_VOICE_AVAILABLE:
            try:
                self.enhanced_voice = EnhancedVoiceEngine()
                # Set Clever's personality to street-smart
                self.voice_params = self.enhanced_voice.set_voice_personality('street-smart')
                print(\"✨ Enhanced voice engine loaded with street-smart personality\")
            except Exception as e:
                print(f\"⚠️  Enhanced voice engine failed to load: {e}\")
                self.enhanced_voice = None
                self.voice_params = ('en+f3', 165, 68)  # Default female street-smart parameters
        else:
            self.enhanced_voice = None
            self.voice_params = ('en+f3', 165, 68)  # Default female street-smart parameters

Why: Provides voice interaction for Clever while respecting severe memory constraints
     (383MB available) and Chrome OS device limitations.
Where: Voice activation system optimized for Intel Pentium Silver N6000 with 3.7GB RAM
How: Uses minimal dependencies, lightweight speech processing, and emergency mode optimization

Device Specifications Compliance:
    - Memory Usage: <50MB total (current available: 383MB)
    - Audio System: sof-rt5682 codec with muted microphone (needs unmuting)
    - CPU: Intel Pentium Silver N6000 @ 1.10GHz (low-power optimization)
    - Chrome OS: Codespaces environment with network limitations
    - Emergency Mode: Critical memory pressure requires minimal resource usage

Connects to:
    - hardware_config.json: Emergency mode settings and memory constraints
    - docs/config/device_specifications.md: Audio hardware capabilities and limits
    - app.py: Main Flask application for processing voice input
    - persona.py: Lightweight response generation in emergency mode
"""

import json
import subprocess
import sys
import time

try:
    from clever_voice_engine import CleverVoiceEngine

    CLEVER_UNIFIED_VOICE_AVAILABLE = True
except ImportError:
    CLEVER_UNIFIED_VOICE_AVAILABLE = False
    print("⚠️  Clever unified voice engine not available - using legacy path")

# Lightweight imports only - avoid heavy dependencies in emergency mode
try:
    import speech_recognition as sr

    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  Speech recognition not available - install with: pip install SpeechRecognition")

try:
    from natural_voice_engine import NaturalVoiceEngine

    NATURAL_VOICE_AVAILABLE = True
except ImportError:
    NATURAL_VOICE_AVAILABLE = False
    print("⚠️  Natural voice engine not available - using basic TTS")

try:
    from enhanced_voice_engine import EnhancedVoiceEngine

    ENHANCED_VOICE_AVAILABLE = True
except ImportError:
    ENHANCED_VOICE_AVAILABLE = False
    print("⚠️  Enhanced voice engine not available - using basic TTS")

try:
    from app import app as clever_app

    CLEVER_APP_AVAILABLE = True
except ImportError:
    CLEVER_APP_AVAILABLE = False
    print("⚠️  Clever app not available")


class LightweightVoiceSystem:
    """
    Memory-optimized voice system for Chrome OS device constraints

    Why: Enables voice interaction within severe memory limits (383MB available)
    Where: Runs alongside Clever app in emergency optimization mode
    How: Minimal memory footprint, local TTS, optimized for device capabilities
    """

    def __init__(self):
        """Initialize lightweight voice system with device constraints"""
        self.memory_limit_mb = 50  # Stay under emergency mode limits
        self.microphone_available = self._check_microphone()
        self.audio_system_ready = self._check_audio_system()
        # Prefer new unified voice engine when available
        self._clever_voice = None
        if CLEVER_UNIFIED_VOICE_AVAILABLE:
            try:
                self._clever_voice = CleverVoiceEngine()
                # default persona embodies warmth + humor
                self._clever_voice.set_persona("warm_humorous_companion")
                print("✨ Clever unified voice engine loaded (warm + humorous)")
            except Exception as e:
                print(f"⚠️  Failed to init CleverVoiceEngine: {e}")
                self._clever_voice = None

    def _check_microphone(self) -> bool:
        """Check if microphone is available and unmuted"""
        try:
            # Check if microphone is muted (per device specs: "Microphone: Muted")
            result = subprocess.run(
                ["amixer", "get", "Capture"], capture_output=True, text=True, timeout=5
            )
            if "off" in result.stdout.lower():
                print("🎤 Microphone is muted - attempting to unmute...")
                subprocess.run(["amixer", "set", "Capture", "cap"], timeout=5)
                return True
            return True
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            print("⚠️  Could not access microphone controls")
            return False

    def _check_audio_system(self) -> bool:
        """Verify audio system is functional per device specs"""
        try:
            # Device specs show: sof-rt5682 codec, speakers at 100%, headphones at 40%
            result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)
            return "sof-rt5682" in result.stdout
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            print("⚠️  Audio system check failed")
            return False

    def speak_lightweight(self, text: str, voice: str = "en+f3") -> bool:
        """Lightweight text-to-speech preferring unified engine then fallbacks"""
        # Try unified voice orchestrator first
        if getattr(self, "_clever_voice", None):
            try:
                if self._clever_voice.speak(text):
                    return True
            except Exception as e:
                print(f"⚠️  Unified voice failed, falling back: {e}")
        try:
            if len(text) > 200:  # Limit text length for memory efficiency
                text = text[:200] + "..."

            # Use female espeak voice with natural parameters
            subprocess.run(
                ["espeak", "-v", voice, "-s", "165", "-p", "68", text],
                timeout=10,
                check=True,
            )
            return True
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            print("⚠️  Text-to-speech not available")
            return False

    def listen_lightweight(self, timeout: int = 5) -> str:
        """Lightweight speech recognition with memory optimization"""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.microphone_available:
            print("⚠️  Speech recognition not available")
            return ""

        try:
            r = sr.Recognizer()
            # Use device specs: "Microphone: Muted (CBJ Boost: 30dB)"
            with sr.Microphone() as source:
                print("🎤 Listening... (optimized for Chrome OS)")
                r.adjust_for_ambient_noise(source, duration=0.5)  # Minimal adjustment
                audio = r.listen(source, timeout=timeout, phrase_time_limit=5)

                # Use local recognition if possible to avoid network calls
                try:
                    text = r.recognize_sphinx(audio)  # Offline recognition
                    print(f"🗣️  Heard (offline): {text}")
                    return text
                except:
                    # Fallback to online recognition if offline fails
                    text = r.recognize_google(audio)
                    print(f"🗣️  Heard (online): {text}")
                    return text

        except sr.WaitTimeoutError:
            print("⏱️  Listening timeout")
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
        except Exception as e:
            print(f"⚠️  Speech recognition error: {e}")

        return ""

    def get_clever_response(self, user_input: str) -> str:
        """Get response from Clever app with memory optimization"""
        if not CLEVER_APP_AVAILABLE:
            return "Clever app not available. Please start the main application."

        try:
            # Use lightweight request to Clever app
            with clever_app.test_client() as client:
                response = client.post(
                    "/api/chat",
                    json={"message": user_input, "mode": "Quick Hit"},
                    timeout=10,
                )
                if response.status_code == 200:
                    data = response.get_json()
                    return data.get("response", "No response available")
                else:
                    return "Clever is having trouble responding right now."
        except Exception as e:
            print(f"⚠️  Error getting Clever response: {e}")
            return "Clever is temporarily unavailable."


def main():
    """Main voice loop optimized for Chrome OS device constraints"""
    print("🧠 Clever Voice System - Chrome OS Optimized")
    print("📊 Memory limit: 50MB | Emergency mode: Active")
    print("🎤 Device: Google Pirika | Audio: sof-rt5682")

    voice_system = LightweightVoiceSystem()

    if not voice_system.audio_system_ready:
        print("❌ Audio system not ready. Please check device audio.")
        # Why: Signal the startup script that voice cannot initialize so Clever can stay online.
        # Where: Handshake between lightweight voice loop and start_clever.sh fallback path.
        # How: Non-zero exit code tells the launcher to downgrade to text-only mode.
        return 2

    print("\n💡 Say 'Hey Clever' to start (or type 'quit' to exit)")

    # Check for hardware optimization mode
    try:
        with open("hardware_config.json", "r") as f:
            config = json.load(f)
            if config.get("strategy_name") == "emergency":
                print(
                    f"⚡ Emergency mode active: {config['hardware_profile']['available_memory_mb']}MB available"
                )
    except FileNotFoundError:
        pass

    # Startup voice backend line (if unified engine loaded)
    try:
        if getattr(voice_system, "_clever_voice", None):
            st = voice_system._clever_voice.get_status()
            model = st.get("piper_model") or "none"
            print(
                f"[voice] backend={st.get('backend_selected')} offline_only={st.get('offline_only')} model={model}"
            )
    except Exception:
        pass

    while True:
        try:
            # Listen for wake word
            user_input = (
                input("\n> ").strip()
                if not voice_system.microphone_available
                else voice_system.listen_lightweight()
            )

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "goodbye"]:
                voice_system.speak_lightweight("Peace out! Clever voice system shutting down.")
                break

            # Check for wake word
            if "hey clever" in user_input.lower() or "clever" in user_input.lower():
                voice_system.speak_lightweight("Yo! What's up? I'm here!")

                # Continue conversation
                while True:
                    next_input = (
                        input("You: ").strip()
                        if not voice_system.microphone_available
                        else voice_system.listen_lightweight()
                    )

                    if not next_input or next_input.lower() in [
                        "goodbye",
                        "exit",
                        "done",
                    ]:
                        voice_system.speak_lightweight("Catch you later!")
                        break

                    # Get Clever's response
                    response = voice_system.get_clever_response(next_input)
                    print(f"Clever: {response}")
                    voice_system.speak_lightweight(response)

        except KeyboardInterrupt:
            print("\n👋 Voice system interrupted")
            break
        except Exception as e:
            print(f"⚠️  Error in voice loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    sys.exit(main() or 0)
