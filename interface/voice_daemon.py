"""
Offline voice loop daemon for Clever.

Why: Provide a local microphone → Clever → speaker loop so Jay can interact with Clever hands-free while staying fully offline.
Where: Launched by `scripts/start.sh` (tmux voice window) or manually via CLI when running Clever on the Chromebook.
How: Uses sounddevice for capture/playback, WebRTC VAD for activity detection, optional wake-word/STT models, and the `/chat` endpoint for responses.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

import sounddevice as sd
import webrtcvad

# Optional imports guarded for offline deployment
try:
    from openwakeword.model import Model as OWW
except Exception:  # pragma: no cover
    OWW = None

try:
    import vosk
except Exception:  # pragma: no cover
    vosk = None

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

# Chromebook audio defaults observed during setup
sd.default.device = (4, 4)  # input index, output index
sd.default.samplerate = 16000
sd.default.channels = 1

APP_URL = "http://127.0.0.1:8000/chat"
MODELS = Path("data/models")
WAKE_DIR = MODELS / "openwakeword"
VOSK_DIR = MODELS / "vosk"
WAKEWORD = os.environ.get("CLEVER_WAKEWORD", "hey clever")
SAMPLE_RATE = 16000
CHANNELS = 1


def tts_say(text: str) -> None:
    """Speak text via pyttsx3 when available, otherwise print."""
    if pyttsx3:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return
        except Exception:  # pragma: no cover
            pass
    print(f"[TTS] {text}")


def stt_transcribe_pcm(pcm_bytes: bytes) -> str:
    """Return best-effort transcript using Vosk if the model exists."""
    if vosk and VOSK_DIR.exists():
        try:
            model_dirs = [p for p in VOSK_DIR.iterdir() if p.is_dir()]
            if model_dirs:
                model = vosk.Model(str(model_dirs[0]))
                recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
                recognizer.AcceptWaveform(pcm_bytes)
                result = json.loads(recognizer.Result() or "{}").get("text", "")
                return result.strip()
        except Exception:  # pragma: no cover
            return ""
    return ""


def post_chat(text: str) -> str:
    """Send text to Clever's chat endpoint and return raw JSON response."""
    try:
        return subprocess.check_output(
            [
                "curl",
                "-sS",
                "-X",
                "POST",
                APP_URL,
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps({"text": text, "mode": "auto"}),
            ],
            text=True,
        )
    except Exception as exc:  # pragma: no cover
        return json.dumps({"error": f"chat_error: {exc}"})


def wake_model():
    """Return an openWakeWord model if assets are available."""
    if OWW and WAKE_DIR.exists():
        return OWW(wakeword_models=str(WAKE_DIR))
    return None


def run_loop() -> None:
    """Main capture/response loop for Clever voice interactions."""
    vad = webrtcvad.Vad(2)
    model = wake_model()
    block_ms = 30
    block_bytes = int(SAMPLE_RATE * block_ms / 1000) * 2  # 16-bit mono
    stream = sd.RawInputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16")
    stream.start()

    tts_say("Clever voice ready.")

    buffer = b""
    listening = False
    last_speech_ts = 0.0

    while True:
        data, _ = stream.read(block_bytes // 2)
        pcm = bytes(data)
        buffer += pcm

        if model:
            try:
                scores = model.predict(pcm)
                if any(score > 0.5 for score in scores.values()):
                    listening = True
                    tts_say("Yes?")
                    buffer = b""
                    last_speech_ts = time.time()
                    continue
            except Exception:  # pragma: no cover
                pass

        if listening:
            is_speech = vad.is_speech(pcm, SAMPLE_RATE)
            now = time.time()
            if is_speech:
                last_speech_ts = now
            if (now - last_speech_ts) > 0.8 and len(buffer) > SAMPLE_RATE * 2 * 0.6:
                text = stt_transcribe_pcm(buffer)
                buffer = b""
                listening = False
                if text:
                    print(f"[user] {text}")
                    reply = post_chat(text)
                    print(f"[clever] {reply}")
                    try:
                        payload = json.loads(reply)
                        spoken = payload.get("text", "")[:220]
                    except json.JSONDecodeError:
                        spoken = reply[:220]
                    tts_say(spoken or "I'm here.")
                else:
                    tts_say("I didn't catch that.")
        time.sleep(0.01)


if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:  # pragma: no cover
        pass
