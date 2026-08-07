"""
Interactive voice loop demonstration for JaysAuthenticClever.

Why: Provide a quick manual test harness showing how Jay can wake Clever by
voice and receive synthesized responses without launching the full stack.
Where: Used during development spikes to validate speech recognition and TTS
integration while staying offline.
How: Listens for wake phrases through `speech_recognition`, delegates replies to
`JaysAuthenticClever`, and speaks them via `pyttsx3`.

File Usage:
    - `voice_loop_example.py`: launched directly for ad-hoc voice testing.
    - `docs/` voice tutorials: referenced as a minimal integration sample.
Connects to:
    - `jays_authentic_clever.py`: generates persona-aligned responses.
    - `pyttsx3`: offline TTS engine for playback.
    - `speech_recognition`: captures Jay's microphone input locally.
"""

import pyttsx3
import speech_recognition as sr

from jays_authentic_clever import JaysAuthenticClever


def speak(text):
    """
    Convert Clever's text into spoken audio using pyttsx3.

    Why: Keep the test loop fully offline while confirming voice delivery.
    Where: Called for every response inside `main()` after Clever replies.
    How: Initializes the TTS engine, queues the text, and blocks until playback
    finishes.

    File Usage:
        - `voice_loop_example.py`: primary caller within the while loop.
    Connects to:
        - `pyttsx3`: handles the offline voice synthesis work.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def listen():
    """
    Capture audio from the default microphone and transcribe locally.

    Why: Provide the wake phrase and follow-up command capture for Clever’s
    responses while keeping the flow offline.
    Where: Invoked by `main()` to await Jay's prompts before invoking Clever.
    How: Uses `speech_recognition` to listen and attempt transcription; error
    cases return an empty string to keep the loop alive.

    File Usage:
        - `voice_loop_example.py`: used for both wake detection and follow-ups.
    Connects to:
        - `speech_recognition`: supplies recognizer and microphone abstractions.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Say something (or 'Hey Clever!')...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"🗣️ Heard: {text}")
            return text
        except Exception as e:
            print("Sorry, I didn't catch that.")
            return ""


def main():
    """
    Run the interactive loop that routes microphone input to Clever.

    Why: Demonstrate end-to-end wake word listening and persona responses for
    manual QA without spinning up Flask routes.
    Where: Executes when this module is run directly (`python voice_loop_example.py`).
    How: Creates a `JaysAuthenticClever` instance, waits for the wake phrase,
    and alternates between `listen()` and `speak()` calls until Jay says
    "goodbye".

    File Usage:
        - `voice_loop_example.py`: script entry point.
    Connects to:
        - `JaysAuthenticClever.generate_authentic_response`: supplies replies.
        - `listen`/`speak`: helper functions defined in this module.
    """
    clever = JaysAuthenticClever()
    while True:
        heard = listen()
        if "hey clever" in heard.lower() or "yo clever" in heard.lower():
            speak("Ay! Sup Jay! I'm here! Ready for whatever!")
            while True:
                user_input = listen()
                if user_input:
                    response = clever.generate_authentic_response(user_input)
                    speak(response["text"])
                if "goodbye" in user_input.lower():
                    speak("Peace out, Jay!")
                    break


if __name__ == "__main__":
    main()
