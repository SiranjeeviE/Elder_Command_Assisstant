
Elder Voice Command Assistant (Emergency Enabled)

Abstract

Elderly people and patients with reduced mobility often face difficulties operating electronic devices or calling for help quickly during emergencies. Traditional interfaces such as keyboards, mice, and touchscreens may not be suitable for them, especially when they are weak, visually impaired, or under medication.

This mini-project presents an offline voice-based assistant designed specifically for elders. The system listens to spoken commands, recognizes speech using the Vosk speech recognition engine, classifies the user’s intent using a simple rule-based intent classifier, and responds with natural speech using the pyttsx3 text-to-speech engine. A graphical user interface (GUI) built with Tkinter displays a log of interactions, provides a Speak button to start listening, and an Emergency Demo button to simulate an emergency scenario.

The assistant can respond to basic queries such as time and date, set medicine reminders, simulate light control, and most importantly, trigger an emergency alert that continuously announces a warning and simulates notifying a caregiver. The system works offline, making it suitable for scenarios where internet access may be limited or unavailable.

Introduction

A. Background and Motivation

As the global population ages, there is an increasing need for technologies that support independent and safe living for elderly people. Many elders live alone or spend long periods without direct supervision. During emergencies such as falls, dizziness, chest pain, or sudden illness, they may not be able to reach a phone or call for help.

Voice-based interfaces offer a natural, hands-free way of interacting with devices. Commercial voice assistants are powerful but require stable internet connectivity and are not always configured for emergency assistance. For critical care, an offline, dedicated, and easy-to-use assistant can be highly beneficial.

This project, Elder Voice Command Assistant, focuses on building a prototype of such a system. It combines offline speech recognition, simple intent identification, text-to-speech output, and a clean GUI to make interaction effortless for elderly users.

B. Problem Statement

Design and implement a voice-controlled assistant application that can:

• Recognize spoken commands from an elder user
• Understand the basic intent behind each command
• Provide spoken responses using offline text-to-speech
• Trigger an emergency alert and simulate notifying a caregiver
• Work without internet connectivity


C. Objectives

• Develop a Tkinter-based GUI application for elder-friendly voice interaction
• Integrate Vosk for offline speech recognition
• Implement a simple rule-based intent classification system
• Provide speech responses using pyttsx3
• Design an emergency alert mechanism with a popup and repeated alerts
• Simulate caregiver notification during emergencies


System Analysis

A. Existing System

Existing solutions typically depend on:
• Physical emergency buttons
• Mobile phones
• General-purpose assistants requiring internet

These solutions may fail when the user is weak, unable to reach a device, or does not have stable internet.

B. Proposed System

The proposed system addresses these issues by:
• Offering a simple, large-button GUI
• Using voice commands as the main interaction method
• Operating fully offline
• Providing an emergency alert with a red popup and repeated warnings
• Simulating caregiver notification

The system runs on a computer with a microphone and speakers but can be extended to IoT or embedded devices.

Appendices

Main.py

import tkinter as tk
from tkinter import scrolledtext
import sounddevice as sd
import queue
import json
import time
import threading
import re
from vosk import Model, KaldiRecognizer
import os
from intents import classify_intent
from tts_utils import speak
MODEL_PATH = "models/vosk_model"
SAMPLE_RATE = 16000
INPUT_DEVICE_INDEX = None
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Please download Vosk model into models/vosk-model")
try:
    sd.default.samplerate = SAMPLE_RATE
    sd.default.channels = 1
    if INPUT_DEVICE_INDEX is not None:
        sd.default.device = (INPUT_DEVICE_INDEX, None)
except Exception as e:
    print("[Audio init warning] Could not initialize default input device:", e)
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
audio_q = queue.Queue()
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)
    audio_q.put(bytes(indata))
def listen_and_recognize(timeout=8):
    recognizer.AcceptWaveform(b"")
    start_time = time.time()
    text = ""
    last_partial = ""
    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=4000, dtype='int16',
                               channels=1, callback=audio_callback, device=INPUT_DEVICE_INDEX):
            while True:
                if (time.time() - start_time) > timeout:
                    break
                try:
                    data = audio_q.get(timeout=timeout)
                except queue.Empty:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text.strip():
                        break
                else:
                    try:
                        pres = json.loads(recognizer.PartialResult())
                        ptxt = pres.get("partial", "")
                        if ptxt:
                            last_partial = ptxt
                    except Exception:
                        pass
    except Exception as e:
        print("[Audio error] Could not open input stream:", e)
        return ""
    if not text:
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "")
        if not text and last_partial:
            text = last_partial
    return text.strip()
root = tk.Tk()
root.title("Elder Voice Command Assistant (Emergency Enabled)")
root.geometry("760x520")
root.configure(bg="#F3F3F3")
title_label = tk.Label(root, text="🎙 Elder Voice Command Assistant", font=("Arial", 20, "bold"), bg="#F3F3F3")
title_label.pack(pady=10)
output_box = scrolledtext.ScrolledText(root, width=85, height=14, font=("Arial", 13))
output_box.pack(padx=10, pady=10)
output_box.insert(tk.END, "Click 'Speak' and say something...\n"
def log_message(msg):
    ts = time.strftime("%I:%M:%S %p")
    output_box.insert(tk.END, f"[{ts}] {msg}\n")
    output_box.see(tk.END)
    root.update()
reminders = []
def set_reminder(delay_seconds):
    def reminder_action():
        speak("It’s time to take your medicine.")
        log_message("\n💊 Reminder: It's time to take your medicine!")
    threading.Timer(delay_seconds, reminder_action).start()
def parse_time_phrase(text):
    text = text.lower()
    match = re.search(r'in (\d+) minute', text)
    if match:
        mins = int(match.group(1))
        return mins * 60
    match = re.search(r'in (\d+) hour', text)
    if match:
        hrs = int(match.group(1))
        return hrs * 3600
    match = re.search(r'at (\d+)(?:\s*)(am|pm)', text)
    if match:
        hour = int(match.group(1))
        ampm = match.group(2)
        if ampm == "pm" and hour != 12:
            hour += 12
        now = time.localtime()
        reminder_time = time.struct_time((
            now.tm_year, now.tm_mon, now.tm_mday, hour, 0, 0,
            now.tm_wday, now.tm_yday, now.tm_isdst
        ))
        target = time.mktime(reminder_time)
        diff = target - time.time()
        if diff < 0:
            diff += 86400
        return diff
    return None
_emergency_active = False
_emergency_thread = None
def _speak_repeated_emergency(stop_event):
    """Speak the emergency message repeatedly until stop_event is set."""
    while not stop_event.is_set():
        speak("Emergency! Help is needed. Notifying caregiver.")
        for _ in range(6):
            if stop_event.is_set():
                break
            time.sleep(0.5)
def notify_caregiver_simulated(details="User requested help"):
    """Simulated caregiver notification — replace with real API later."""
    # For demo: log to GUI and print
    log_message("!!! SIMULATION: Notifying caregiver: " + details)
    print("SIMULATION: notify caregiver ->", details)
def show_emergency_popup(details="Help requested"):
    global _emergency_active, _emergency_thread
    if _emergency_active:
        return
    _emergency_active = True
    popup = tk.Toplevel(root)
    popup.title("!! EMERGENCY ALERT !!")
    popup.geometry("680x320")
    popup.configure(bg="red")
    popup.attributes("-topmost", True)

    lbl = tk.Label(popup, text="EMERGENCY!", font=("Arial", 36, "bold"), bg="red", fg="white")
    lbl.pack(pady=10)
    detail_label = tk.Label(popup, text=details, font=("Arial", 18), bg="red", fg="white")
    detail_label.pack(pady=5)
    info_label = tk.Label(popup, text="The assistant will keep alerting. Press 'Notify' to simulate notifying caregiver, or 'Cancel' to stop.", 
                          font=("Arial", 12), bg="red", fg="white", wraplength=640, justify="center")
    info_label.pack(pady=8)
    button_frame = tk.Frame(popup, bg="red")
    button_frame.pack(pady=12)
    stop_event = threading.Event()
    def on_notify():
        notify_caregiver_simulated(details)
        stop_event.set()
        cleanup()
    def on_cancel():
        log_message("Emergency canceled by user.")
        stop_event.set()
        cleanup()
    def cleanup():
        global _emergency_active, _emergency_thread
        _emergency_active = False
        try:
            popup.destroy()
        except:
            pass
    notify_btn = tk.Button(button_frame, text="Notify Caregiver (Simulate)", font=("Arial", 14, "bold"),
                           bg="#FFD700", command=on_notify, padx=12, pady=8)
    notify_btn.pack(side="left", padx=12)

    cancel_btn = tk.Button(button_frame, text="Cancel Alert", font=("Arial", 14, "bold"),
                           bg="#D3D3D3", command=on_cancel, padx=12, pady=8)
    cancel_btn.pack(side="left", padx=12)
    _emergency_thread = threading.Thread(target=_speak_repeated_emergency, args=(stop_event,), daemon=True)
    _emergency_thread.start()
    log_message("!!! Emergency mode active. Popup shown and repeated alerting started.")
def start_listening():
    log_message("\nListening... please speak now.")
    speak("I'm listening.")
    text = listen_and_recognize()
    if not text:
        log_message("No speech detected.")
        speak("I didn't hear you clearly.")
        return
    log_message("You said: " + text)
    intent = classify_intent(text)
    log_message(f"→ Detected intent: {intent}")
    handle_intent(intent, text)
controls_frame = tk.Frame(root, bg="#F3F3F3")
controls_frame.pack(pady=6)
speak_button = tk.Button(controls_frame, text="🎤 Speak", font=("Arial", 16), bg="#4CAF50", fg="white",padx=30, pady=10, command=start_listening)
speak_button.pack(side="left", padx=8) help_demo_btn = tk.Button(controls_frame, text="🔴 Emergency Demo", font=("Arial", 12), bg="#FF5555", fg="white", padx=12, pady=8,
                          command=lambda: (log_message("Emergency demo triggered."), show_emergency_popup("Demo: Emergency triggered manually.")))
help_demo_btn.pack(side="left", padx=8)
root.mainloop()

Result

A. GUI Screenshot

When the program is executed, the main window appears with the title “Elder Voice Command Assistant (Emergency Enabled)”. The top area contains a label with a microphone icon and the project name. A large scrollable text box displays status messages and conversation logs. At the bottom, there are two buttons:

- A green “Speak button” used to start listening.
- A red “Emergency Demo” button used to trigger an emergency scenario for testing.

In a sample run, the log area displays:

- `Click 'Speak' and say something...`
- `[07:19:05 AM] Listening... please speak now.`



 
B. Console Output

A sample console output captured during one of the runs is:

 [Assistant speaking]: I'm listening.
[Assistant speaking]: I didn't hear you clearly.
[Assistant speaking]: Emergency! Help is needed. Notifying caregiver.
SIMULATION: notify caregiver -> Demo: Emergency triggered manually.




Advantages, Limitations, and Future Enhancements

A. Advantages
• Fully offline
• Easy to use
• Emergency alert system included
• Modular and extendable
• 
B. Limitations
• Basic rule-based intent recognition
• English only
• Desktop-only
• Caregiver notification is simulated
• 
C. Future Enhancements
• Real SMS or call notifications
• NLP-based intent detection
• Multi-language support
• Smart home integration
• Wake-word activation

Conclusion

The Elder Voice Command Assistant successfully demonstrates how offline speech technologies can assist elderly users by providing hands-free interaction, reminders, and emergency support. The emergency alert feature makes the system especially useful for safety-critical scenarios. Although this prototype is basic, it provides a strong foundation for more advanced elder-care systems involving IoT devices, machine learning, and real-world notification mechanisms.

References

1. Vosk Speech Recognition – https://alphacephei.com/vosk  
2. pyttsx3 Text-to-Speech – https://pyttsx3.readthedocs.io  
3. Python Tkinter Documentation – https://docs.python.org/3/library/tkinter.html  
4. Python `sounddevice` Library – https://python-sounddevice.readthedocs.io  
5. Official Python Documentation – https://www.python.org/doc/
