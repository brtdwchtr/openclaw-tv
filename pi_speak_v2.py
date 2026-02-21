#!/usr/bin/env python3
"""Codie TTS — Generate and play speech on the Pi.
Uses the TTS daemon if running (fast), falls back to direct model load (slow).

Usage:
  speak.py "Hello world"
  speak.py "Hello world" --avatar
  speak.py "Hello world" --no-play
"""

import sys
import os
import time
import argparse
import subprocess
import json
import socket

SOCK_PATH = "/tmp/codie-tts.sock"

def generate_via_daemon(text, voice="Hugo"):
    """Fast path: send to pre-warmed daemon."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCK_PATH)
    sock.sendall((json.dumps({"text": text, "voice": voice}) + "\n").encode())
    
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if b"\n" in data:
            break
    sock.close()
    
    result = json.loads(data.decode().strip())
    if not result.get("ok"):
        raise Exception(result.get("error", "daemon error"))
    return result

def generate_direct(text, voice="Hugo"):
    """Slow path: load model directly."""
    from kittentts import KittenTTS
    import soundfile as sf
    import numpy as np
    
    m = KittenTTS("KittenML/kitten-tts-nano-0.8")
    t0 = time.time()
    audio = m.model.generate(text, voice=voice, clean_text=False)
    gen_time = time.time() - t0
    duration = len(audio) / 24000
    
    wav_path = "/tmp/codie_speech.wav"
    sf.write(wav_path, audio, 24000)
    return {"ok": True, "wav": wav_path, "duration": duration, "gen_time": gen_time}

def play_audio(wav_path):
    subprocess.run(["aplay", wav_path], stderr=subprocess.DEVNULL)

def push_to_avatar(message, audio_path):
    try:
        import urllib.request
        data = json.dumps({
            "message": message,
            "audio": f"/static/{os.path.basename(audio_path)}?t={int(time.time()*1000)}",
            "mood": "talking"
        }).encode()
        req = urllib.request.Request(
            "http://localhost:8080/api/state",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Codie TTS on Pi")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--voice", default="Hugo", help="Voice (default: Hugo)")
    parser.add_argument("--no-play", action="store_true", help="Generate only")
    parser.add_argument("--avatar", action="store_true", help="Push to avatar")
    args = parser.parse_args()

    # Try daemon first, fall back to direct
    try:
        if os.path.exists(SOCK_PATH):
            result = generate_via_daemon(args.text, args.voice)
            print(f"[daemon] Generated {result['duration']}s in {result['gen_time']}s ({result.get('rtf',0)}x RT)")
        else:
            raise FileNotFoundError("no daemon")
    except Exception as e:
        print(f"Daemon unavailable ({e}), loading model directly...")
        result = generate_direct(args.text, args.voice)
        print(f"[direct] Generated {result['duration']:.1f}s in {result['gen_time']:.1f}s")

    wav_path = result["wav"]

    if args.avatar:
        import shutil
        static_path = os.path.expanduser("~/clawdpi-tv/static/codie_speech.wav")
        os.makedirs(os.path.dirname(static_path), exist_ok=True)
        shutil.copy2(wav_path, static_path)
        push_to_avatar(args.text, static_path)
        print("Playing via avatar browser.")
    elif not args.no_play:
        play_audio(wav_path)
        print("Played!")

if __name__ == "__main__":
    main()
