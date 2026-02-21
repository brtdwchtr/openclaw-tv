# 📺 openclaw-tv

> Give your AI agent a physical body — particle cloud avatar on a TV with text-to-speech.

```
   ✦  ·  ✧   ·  ✦        ┌─────────────────────────┐
  · ✦  ·  ✧  ·            │   ┌─────────────────┐   │
 ✧  ·  ✦  ·  ✦  ·         │   │  · ✦ · ✧ · ✦  │   │
  · ✦  ·  ✧  ✦  ·         │   │ ✧   ✦ · ✦   ✧ │   │
   ✧ · ✦  · ✦  ✧          │   │  · ✦ · ✧ · ✦  │   │
    · ✦ · ✧ · ✦            │   └─────────────────┘   │
                           │  📻  OpenClaw TV Body  │
  Your AI, embodied.       └─────────────────────────┘
```

**openclaw-tv** turns a Raspberry Pi + any display (vintage CRT, modern TV, monitor) into a living, breathing physical presence for your AI agent. When your agent speaks, 3,000 particles snap from a murmuring flock into an audio-reactive sphere. You see it. You hear it. It's *there*.

---

## ✨ What it does

- **Particle cloud avatar** — 3,000 particles idle in murmuration-style curl-noise flow, then snap to a compact sphere when speaking
- **Audio-reactive** — bass expands the cloud, mids add jitter, highs trigger sparkle bursts
- **Rolling captions** — words appear word-by-word as the agent speaks
- **Fast TTS** — Kitten TTS nano (14M params) runs on Pi 4 at ~0.7× realtime; pre-warmed daemon cuts cold start from 16s → 0.3s
- **Simple API** — `POST /api/state` with `{"message":"Hello","mood":"excited"}` from anywhere on your network
- **YouTube playback** — play any YouTube video fullscreen, auto-restores avatar when done
- **Vintage CRT ready** — composite video output, tested on real CRTs via RF modulator

---

## 🚀 Quick Install

```bash
# On your Raspberry Pi 4
git clone https://github.com/brtdwchtr/openclaw-tv.git
cd openclaw-tv
bash install.sh
```

The install script sets up Python 3.12, installs Kitten TTS with the correct PyTorch version, creates systemd services, and configures Chromium kiosk mode.

---

## 🎮 Usage

### Make your agent speak

```bash
# Speak through the avatar (particles react to audio)
codie-say "Hello, I am alive." --avatar

# Speak via aplay only (no avatar)
codie-say "Hello world."

# With the full script (same thing)
python3 speak.py "Hello from the network" --avatar
```

### Play YouTube videos

```bash
# Downloads, plays fullscreen, auto-restores avatar when done
play-yt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### HTTP API (from any language/agent)

```bash
# Set message + mood (avatar reacts)
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello!","mood":"excited"}'

# Set audio (avatar plays + reacts to frequencies)
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello!","audio":"/static/speech.wav"}'

# Read current state
curl http://your-pi.local:8080/api/state
```

### Remote control via SSH

```bash
# Speak from your Mac/laptop
ssh pi@your-pi.local 'codie-say "Hello from remote!" --avatar'

# Play a YouTube video remotely
ssh pi@your-pi.local 'play-yt "https://youtu.be/dQw4w9WgXcQ"'
```

### Available voices
`Hugo` (default) · `Bella` · `Jasper` · `Luna` · `Bruno` · `Rosie` · `Kiki` · `Leo`

### Available moods
`idle` · `excited` · `calm` · `thinking` · `happy` · `curious`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Network                                  │
│                                                                  │
│  ┌──────────────┐   HTTP POST /api/state   ┌─────────────────┐ │
│  │  AI Agent    │ ──────────────────────── ▶│  Pi Web Server  │ │
│  │  (anywhere)  │                          │  port 8080      │ │
│  └──────────────┘   SSH + codie-say        └────────┬────────┘ │
│                                                     │           │
│  ┌──────────────────────────────────────────────────▼────────┐ │
│  │                  Raspberry Pi 4                            │ │
│  │                                                            │ │
│  │  ┌─────────────┐    Unix socket    ┌──────────────────┐   │ │
│  │  │  codie-say  │ ────────────────▶ │   TTS Daemon     │   │ │
│  │  │  speak.py   │  /tmp/codie-tts   │  Kitten nano     │   │ │
│  │  └─────────────┘      .sock        │  model in memory │   │ │
│  │         │                          └──────────────────┘   │ │
│  │         │ --avatar                                         │ │
│  │         ▼                                                  │ │
│  │  ┌─────────────┐   Chromium kiosk   ┌──────────────────┐ │ │
│  │  │   Speaker   │                    │  Avatar (Three.js)│ │ │
│  │  │  (browser)  │                    │  particle cloud  │ │ │
│  │  └─────────────┘                    └────────┬─────────┘ │ │
│  └──────────────────────────────────────────────│───────────┘ │
│                                                  │              │
└──────────────────────────────────────────────────│──────────────┘
                                                   │ HDMI / composite
                                            ┌──────▼──────┐
                                            │  Display 📺  │
                                            └─────────────┘
```

---

## 📁 Project Structure

```
openclaw-tv/
├── avatar.html          # Particle cloud avatar (Three.js)
├── server.py            # Web server with /api/state API
├── speak.py             # TTS client (daemon-first, fallback to direct)
├── codie-tts-daemon.py  # TTS daemon (keeps model pre-warmed)
├── index.html           # Teletext-style clock display
├── start-kiosk.sh       # Chromium kiosk launcher
├── bin/
│   ├── codie-say        # Quick TTS wrapper
│   ├── play-yt          # YouTube download + fullscreen play
│   └── openclaw-tv      # Full CLI (install, daemon, serve, speak)
├── config/
│   ├── default.json     # Default configuration
│   └── systemd/         # Systemd service templates
├── docs/
│   ├── hardware.md      # Pi wiring, CRT connection, TRRS cable
│   ├── setup.md         # Full installation guide
│   └── troubleshooting.md
├── skill/
│   ├── SKILL.md         # OpenClaw agent skill definition
│   └── scripts/speak.sh # Skill speak helper
└── install.sh           # Automated installer
```

---

## 📚 Documentation

- [Hardware setup](docs/hardware.md) — Pi wiring, CRT connection, TRRS cable
- [Software setup](docs/setup.md) — Full installation guide
- [Troubleshooting](docs/troubleshooting.md) — Common issues and fixes

---

## 🔌 OpenClaw Skill

If you're using [OpenClaw](https://openclaw.ai), drop the `skill/` folder into your agent's skills directory:

```bash
cp -r skill/ ~/clawd/skills/openclaw-tv/
```

Your agent will automatically know how to speak through the TV, set moods, and interact with the avatar. See [skill/SKILL.md](skill/SKILL.md) for details.

---

## 🛠️ Built with

| Component | What it does |
|-----------|-------------|
| **[OpenClaw](https://openclaw.ai)** | AI agent framework that runs this whole show |
| **[Kitten TTS](https://huggingface.co/KittenML/kitten-tts-nano-0.8)** | 14M param TTS model, runs on Pi 4 |
| **[Three.js](https://threejs.org)** | WebGL particle system for the avatar |
| **Raspberry Pi 4** | The physical body hardware |

---

## 🔧 Requirements

- Raspberry Pi 4 (2GB+ RAM)
- Python 3.12 (not 3.13+, Kitten TTS compatibility)
- PyTorch 2.5.1 (2.6+ crashes on Pi 4 Cortex-A72)
- `uv` package manager
- Any display: HDMI monitor, TV, or vintage CRT via composite

---

## ⚡ Critical Notes

> **PyTorch version:** Must be `2.5.1` — PyTorch 2.6+ causes "Illegal Instruction" on Pi 4's Cortex-A72.

> **TTS preprocessor:** Always use `clean_text=False` — the built-in preprocessor breaks prosody.

> **CRT users:** Video signal goes on the **RED** plug of the TRRS cable (not yellow). RF modulator must be powered from a **separate USB charger** (not the Pi — causes I/O errors).

---

## 📄 License

MIT © 2026 brtdwchtr

---

*Made with ☕ and a vintage CRT TV that really shouldn't still be working.*
