#!/usr/bin/env python3
"""
OpenClaw TV TTS Daemon
Keeps the Kitten TTS model warm in memory.
Listens on a Unix socket for requests, generates speech, returns wav path.

CRITICAL: Uses clean_text=False — the preprocessor breaks prosody.
CRITICAL: Requires Python 3.12 (not 3.13+) and torch==2.5.1.

Usage:
  # Start daemon (blocks):
  python3 tts-daemon.py

  # Test from another terminal:
  echo '{"text":"Hello world","voice":"Hugo"}' | nc -U /tmp/openclaw-tv-tts.sock

  # Response:
  {"ok":true,"wav":"/tmp/openclaw-tv-speech.wav","duration":3.2,"gen_time":4.1,"rtf":0.78}

Socket: /tmp/openclaw-tv-tts.sock
Output: /tmp/openclaw-tv-speech.wav (overwrites on each request)
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

SOCK_PATH = "/tmp/openclaw-tv-tts.sock"
WAV_DIR = "/tmp"
MODEL_ID = "KittenML/kitten-tts-nano-0.8"
DEFAULT_VOICE = "Hugo"

print("OpenClaw TV TTS Daemon starting...", flush=True)
print(f"  Model: {MODEL_ID}", flush=True)
print(f"  Socket: {SOCK_PATH}", flush=True)
print("Loading Kitten TTS model...", flush=True)
t0 = time.time()

from kittentts import KittenTTS
model = KittenTTS(MODEL_ID)

print(f"Model loaded in {time.time()-t0:.1f}s — ready!", flush=True)


def generate(text: str, voice: str = DEFAULT_VOICE) -> dict:
    """Generate speech and save to WAV. Returns metadata dict."""
    t0 = time.time()
    # CRITICAL: clean_text=False — the preprocessor breaks prosody
    audio = model.model.generate(text, voice=voice, clean_text=False)
    gen_time = time.time() - t0
    duration = len(audio) / 24000  # Kitten TTS output is 24kHz

    wav_path = os.path.join(WAV_DIR, "openclaw-tv-speech.wav")
    sf.write(wav_path, audio, 24000)

    return {
        "ok": True,
        "wav": wav_path,
        "duration": round(duration, 2),
        "gen_time": round(gen_time, 2),
        "rtf": round(duration / gen_time, 2) if gen_time > 0 else 0,
    }


def handle_client(conn: socket.socket):
    """Handle a single client connection."""
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
            result = {"ok": False, "error": "no text provided"}
        else:
            print(f"  Generating: \"{text[:60]}{'...' if len(text)>60 else ''}\" ({voice})", flush=True)
            result = generate(text, voice)
            print(f"  Done: {result['duration']}s in {result['gen_time']}s ({result['rtf']}x RT)", flush=True)

        conn.sendall((json.dumps(result) + "\n").encode())

    except json.JSONDecodeError as e:
        try:
            conn.sendall((json.dumps({"ok": False, "error": f"invalid JSON: {e}"}) + "\n").encode())
        except Exception:
            pass
    except Exception as e:
        print(f"  Error: {e}", flush=True)
        try:
            conn.sendall((json.dumps({"ok": False, "error": str(e)}) + "\n").encode())
        except Exception:
            pass
    finally:
        conn.close()


def cleanup(sig=None, frame=None):
    print("\nShutting down daemon...", flush=True)
    try:
        os.unlink(SOCK_PATH)
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

# Remove stale socket
if os.path.exists(SOCK_PATH):
    os.unlink(SOCK_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCK_PATH)
os.chmod(SOCK_PATH, 0o777)
server.listen(5)

print(f"Listening on {SOCK_PATH}", flush=True)
print("Ready to generate speech.", flush=True)

while True:
    conn, _ = server.accept()
    t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
    t.start()
