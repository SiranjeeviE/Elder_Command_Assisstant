"""
Intent Classification Module
----------------------------
Maps spoken phrases to specific actions.
Used by the main GUI program to determine what the user wants.
"""

INTENTS = {
    "time": ["time", "what time", "tell me the time", "current time"],
    "date": ["date", "today", "what date", "today's date"],
    "help": ["help", "call nurse", "emergency", "i need help", "help me", "call for help"],
    "medicine": ["medicine", "reminder", "take medicine", "remind me", "set reminder"],
    "lights_on": ["turn on light", "lights on", "switch on light"],
    "lights_off": ["turn off light", "lights off", "switch off light"],
}

def classify_intent(transcript: str):
    """
    Simple rule-based intent classifier.
    :param transcript: recognized speech text (lowercased)
    :return: matching intent name (string)
    """
    text = transcript.lower().strip()
    for intent, phrases in INTENTS.items():
        for p in phrases:
            if p in text:
                return intent

    if any(word in text for word in ["yes", "yeah", "okay", "ok"]):
        return "affirm"
    if any(word in text for word in ["no", "not now", "cancel"]):
        return "deny"

    return "unknown"
