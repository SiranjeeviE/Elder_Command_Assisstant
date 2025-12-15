"""
Text-to-Speech Utility
----------------------
Provides the speak() function for verbal responses.
Uses pyttsx3 (offline TTS).
"""

import pyttsx3
import time

engine = pyttsx3.init()

engine.setProperty('rate', 145)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
if len(voices) > 1:
    for v in voices:
        if "female" in v.name.lower() or "zira" in v.name.lower():
            engine.setProperty('voice', v.id)
            break

def speak(text: str):
    """
    Speak text aloud with small delay for natural pacing.
    :param text: Text to speak aloud.
    """
    print(f"[Assistant speaking]: {text}")
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)
