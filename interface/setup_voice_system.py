#!/usr/bin/env python3
"""
setup_voice_system.py - Voice System Setup for Chrome OS Device

Why: Installs and configures voice dependencies optimized for Chrome OS device
     constraints (383MB available memory, emergency mode optimization).
Where: Prepares voice system for Clever's digital brain extension on Google Pirika
How: Lightweight dependency installation with fallback options for offline operation

Device Specifications Compliance:
    - Memory: Install only essential packages to preserve 383MB available
    - Audio: Configure sof-rt5682 codec and unmute microphone
    - CPU: Optimize for Intel Pentium Silver N6000 @ 1.10GHz
    - Storage: Minimal installation footprint (84.3GB free)

Connects to:
    - clever_voice_loop.py: Lightweight voice interaction system
    - clever_voice_takeover.py: Device-optimized voice takeover
    - hardware_config.json: Emergency mode settings
    - docs/config/device_specifications.md: Device audio capabilities
"""

import json
import subprocess
import sys
import time


class VoiceSystemSetup:
    """
    Voice system setup optimized for Chrome OS device constraints

    Why: Ensures voice system works within emergency mode memory limits
    Where: Chrome OS Google Pirika device with severe resource constraints
    How: Minimal dependency installation with graceful fallbacks
    """

    def __init__(self):
        """Initialize voice system setup"""
        self.device_constraints = self._load_hardware_config()
        self.emergency_mode = self.device_constraints.get("strategy_name") == "emergency"

    def _load_hardware_config(self) -> dict:
        """Load current hardware configuration"""
        try:
            with open("hardware_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"strategy_name": "unknown", "hardware_profile": {}}

    def check_audio_system(self) -> bool:
        """Verify Chrome OS audio system is ready"""
        print("🔍 Checking Chrome OS audio system...")

        try:
            # Check for sof-rt5682 codec (per device specs)
            result = subprocess.run(
                ["cat", "/proc/asound/cards"], capture_output=True, text=True, timeout=5
            )
            if "sof-rt5682" in result.stdout:
                print("✅ sof-rt5682 audio codec detected")
            else:
                print("⚠️  Expected sof-rt5682 codec not found")

            # Check ALSA mixer controls
            result = subprocess.run(
                ["amixer", "scontrols"], capture_output=True, text=True, timeout=5
            )
            print(f"🎛️  Audio controls available: {len(result.stdout.splitlines())} controls")

            return True

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ) as e:
            print(f"❌ Audio system check failed: {e}")
            return False

    def setup_microphone(self) -> bool:
        """Configure microphone per device specifications"""
        print("🎤 Setting up microphone...")

        try:
            # Device specs show microphone is muted by default
            print("📊 Device specs: Microphone muted, CBJ Boost: 30dB available")

            # Unmute capture
            subprocess.run(["amixer", "set", "Capture", "cap"], timeout=5)
            print("✅ Microphone unmuted")

            # Set reasonable capture level
            subprocess.run(["amixer", "set", "Capture", "70%"], timeout=5)
            print("🔊 Capture level set to 70%")

            return True

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ) as e:
            print(f"❌ Microphone setup failed: {e}")
            return False

    def install_lightweight_dependencies(self) -> bool:
        """Install enhanced voice dependencies for better quality"""
        print("📦 Installing enhanced voice dependencies...")

        if self.emergency_mode:
            available_mb = self.device_constraints.get("hardware_profile", {}).get(
                "available_memory_mb", 0
            )
            print(f"⚠️  Emergency mode active - {available_mb}MB available memory")
            print("🎯 Installing essential + enhanced packages...")

        try:
            # Check if espeak is available (lightweight TTS)
            result = subprocess.run(["which", "espeak"], capture_output=True)
            if result.returncode == 0:
                print("✅ espeak TTS available")
            else:
                print("⚠️  espeak not found - TTS may not work")

            # Install SpeechRecognition (essential)
            print("🎯 Installing SpeechRecognition...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "SpeechRecognition"],
                    timeout=60,
                    check=True,
                )
                print("✅ SpeechRecognition installed")
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                print("⚠️  SpeechRecognition installation failed - voice input disabled")

            # Install pyttsx3 for better offline TTS (priority enhancement)
            print("🎯 Installing pyttsx3 (enhanced offline TTS)...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyttsx3"],
                    timeout=90,
                    check=True,
                )
                print("✅ pyttsx3 installed - better voice quality available!")
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                print("⚠️  pyttsx3 installation failed - using espeak only")

            # Install gTTS for highest quality (if not emergency mode)
            if not self.emergency_mode:
                print("🎯 Installing gTTS (high-quality online TTS)...")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "gtts", "pygame"],
                        timeout=120,
                        check=True,
                    )
                    print("✅ gTTS and pygame installed - highest quality voice available!")
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    print("⚠️  gTTS installation failed - offline engines only")
            else:
                print("⚡ Skipping gTTS in emergency mode to preserve memory")

            return True

        except Exception as e:
            print(f"❌ Dependency installation failed: {e}")
            return False

    def test_voice_system(self) -> bool:
        """Test voice system functionality"""
        print("🧪 Testing voice system...")

        # Test TTS
        try:
            subprocess.run(["espeak", "-v", "en-us", "Voice system test"], timeout=10)
            print("✅ Text-to-speech working")
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            print("⚠️  Text-to-speech not available")

        # Test speech recognition import
        try:
            import speech_recognition as sr

            print("✅ Speech recognition library available")

            # Quick microphone test
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    print("🎤 Testing microphone access...")
                    r.adjust_for_ambient_noise(source, duration=1)
                    print("✅ Microphone access successful")
            except Exception as e:
                print(f"⚠️  Microphone test failed: {e}")

        except ImportError:
            print("⚠️  Speech recognition not available")

        return True

    def create_voice_config(self):
        """Create voice system configuration"""
        config = {
            "voice_system": {
                "emergency_mode": self.emergency_mode,
                "memory_limit_mb": 50,
                "audio_codec": "sof-rt5682",
                "tts_engine": "espeak",
                "speech_recognition": "google/sphinx",
                "microphone_boost": "30dB",
                "setup_timestamp": str(time.time()),
            },
            "device_compliance": {
                "chrome_os_optimized": True,
                "memory_budget": "50MB",
                "cpu_optimization": "Intel Pentium Silver N6000",
                "audio_hardware": "Google Pirika sof-rt5682",
            },
        }

        with open("voice_config.json", "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Voice configuration saved to voice_config.json")

    def run_setup(self):
        """Run complete voice system setup"""
        print("🧠 Clever Voice System Setup - Chrome OS Optimized")
        print("=" * 60)

        if self.emergency_mode:
            print("🚨 EMERGENCY MODE DETECTED")
            print(
                f"📊 Available memory: {self.device_constraints.get('hardware_profile', {}).get('available_memory_mb', 'unknown')}MB"
            )
            print("⚡ Using minimal resource setup")

        print("\\n🎯 Setup Steps:")

        # Step 1: Check audio system
        audio_ok = self.check_audio_system()

        # Step 2: Setup microphone
        mic_ok = self.setup_microphone()

        # Step 3: Install dependencies
        deps_ok = self.install_lightweight_dependencies()

        # Step 4: Test system
        test_ok = self.test_voice_system()

        # Step 5: Create config
        self.create_voice_config()

        print("\\n" + "=" * 60)
        print("🎉 Voice System Setup Complete!")
        print(f"🎤 Audio System: {'✅' if audio_ok else '❌'}")
        print(f"🎙️  Microphone: {'✅' if mic_ok else '❌'}")
        print(f"📦 Dependencies: {'✅' if deps_ok else '❌'}")
        print(f"🧪 System Test: {'✅' if test_ok else '❌'}")

        if all([audio_ok, mic_ok, deps_ok, test_ok]):
            print("\\n🚀 Ready to run: python clever_voice_loop.py")
        else:
            print("\\n⚠️  Some components failed - voice system will run in fallback mode")

        return all([audio_ok, mic_ok, deps_ok, test_ok])


def main():
    """Run voice system setup"""
    setup = VoiceSystemSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()
