#!/usr/bin/env python3
"""Codie TTS Daemon — keeps Kitten TTS model warm in memory.
Listens on a Unix socket for requests, generates speech, returns wav path.

Usage:
  # Start daemon:
  codie-tts-daemon.py

  # Client (from codie-say or any script):
  echo '{"text":"Hello world","voice":"Hugo"}' | nc -U /tmp/codie-tts.sock
  # Returns: {"ok":true,"wav":"/tmp/codie_speech.wav","duration":3.2,"gen_time":4.1}
"""

import os
import sys
import json
import time
import socket
import signal
import threading
import numpy as np
import soundfile as sf

SOCK_PATH = "/tmp/codie-tts.sock"
WAV_DIR = "/tmp"
MODEL_ID = "KittenML/kitten-tts-nano-0.8"
DEFAULT_VOICE = "Hugo"

print("Loading Kitten TTS model...", flush=True)
t0 = time.time()
from kittentts import KittenTTS
model = KittenTTS(MODEL_ID)
print(f"Model loaded in {time.time()-t0:.1f}s — ready!", flush=True)

def generate(text, voice=DEFAULT_VOICE):
    t0 = time.time()
    audio = model.model.generate(text, voice=voice, clean_text=False)
    gen_time = time.time() - t0
    duration = len(audio) / 24000
    
    wav_path = os.path.join(WAV_DIR, "codie_speech.wav")
    sf.write(wav_path, audio, 24000)
    
    return {
        "ok": True,
        "wav": wav_path,
        "duration": round(duration, 2),
        "gen_time": round(gen_time, 2),
        "rtf": round(duration / gen_time, 2) if gen_time > 0 else 0
    }

def handle_client(conn):
    try:
        data = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in data or len(data) > 0:
                break
        
        if not data:
            return
        
        req = json.loads(data.decode().strip())
        text = req.get("text", "")
        voice = req.get("voice", DEFAULT_VOICE)
        
        if not text:
            result = {"ok": False, "error": "no text"}
        else:
            result = generate(text, voice)
            print(f"  Generated {result['duration']}s in {result['gen_time']}s ({result['rtf']}x RT)", flush=True)
        
        conn.sendall((json.dumps(result) + "\n").encode())
    except Exception as e:
        try:
            conn.sendall((json.dumps({"ok": False, "error": str(e)}) + "\n").encode())
        except:
            pass
    finally:
        conn.close()

def cleanup(sig=None, frame=None):
    print("\nShutting down...", flush=True)
    try:
        os.unlink(SOCK_PATH)
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

# Clean up stale socket
if os.path.exists(SOCK_PATH):
    os.unlink(SOCK_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCK_PATH)
os.chmod(SOCK_PATH, 0o777)
server.listen(5)

print(f"Listening on {SOCK_PATH}", flush=True)

while True:
    conn, _ = server.accept()
    t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
    t.start()
