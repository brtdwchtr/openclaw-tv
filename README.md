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
- **Vintage CRT ready** — composite video output, tested on real CRTs via RF modulator

---

## 🚀 Quick Install

```bash
# On your Raspberry Pi 4
curl -sSL https://raw.githubusercontent.com/brtdwchtr/openclaw-tv/main/install.sh | bash

# Start the services
sudo systemctl start openclaw-tv
sudo systemctl start openclaw-tv-tts

# Make your agent speak
openclaw-tv speak "Hello, I am alive." --avatar
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Network                                  │
│                                                                  │
│  ┌──────────────┐   HTTP POST /api/state   ┌─────────────────┐ │
│  │  AI Agent    │ ──────────────────────── ▶│  Pi Web Server  │ │
│  │  (anywhere)  │                          │  port 8080      │ │
│  └──────────────┘   SSH + openclaw-tv      └────────┬────────┘ │
│                      speak "..."                    │           │
│                                                     │           │
│  ┌──────────────────────────────────────────────────▼────────┐ │
│  │                  Raspberry Pi 4                            │ │
│  │                                                            │ │
│  │  ┌─────────────┐    Unix socket    ┌──────────────────┐   │ │
│  │  │ openclaw-tv │ ────────────────▶ │   TTS Daemon     │   │ │
│  │  │    CLI      │  /tmp/.../tts.sock│  Kitten nano     │   │ │
│  │  └─────────────┘                  │  model in memory │   │ │
│  │         │                         └──────────────────┘   │ │
│  │         │ aplay                                           │ │
│  │         ▼                                                  │ │
│  │  ┌─────────────┐   Chromium kiosk   ┌──────────────────┐ │ │
│  │  │   Speaker   │                    │  Avatar (Three.js)│ │ │
│  │  └─────────────┘                    │  particle cloud  │ │ │
│  │                                     └────────┬─────────┘ │ │
│  └──────────────────────────────────────────────│───────────┘ │
│                                                  │              │
└──────────────────────────────────────────────────│──────────────┘
                                                   │ composite video
                                            ┌──────▼──────┐
                                            │  CRT TV  📺 │
                                            └─────────────┘
```

---

## 🎮 Usage

### Make your agent speak
```bash
# Via SSH (from anywhere)
ssh pi@your-pi.local 'openclaw-tv speak "Hello, world!" --avatar'

# With specific voice
ssh pi@your-pi.local 'openclaw-tv speak "Greetings." --voice Bella --avatar'

# Via HTTP API (from any language)
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello from the network","mood":"excited"}'
```

### CLI commands
```bash
openclaw-tv speak "text" [--voice Hugo] [--avatar]  # Generate + play TTS
openclaw-tv serve                                    # Start web server
openclaw-tv daemon                                   # Start TTS daemon (foreground)
openclaw-tv status                                   # Check service status
openclaw-tv config                                   # Show/edit config
```

### Available voices
`Hugo` (default) · `Bella` · `Jasper` · `Luna` · `Bruno` · `Rosie` · `Kiki` · `Leo`

### Available moods
`idle` · `excited` · `calm` · `thinking` · `happy` · `curious`

---

## 📚 Documentation

- [Hardware setup](docs/hardware.md) — Pi wiring, CRT connection, TRRS cable
- [Software setup](docs/setup.md) — Full installation guide
- [Troubleshooting](docs/troubleshooting.md) — Common issues and fixes

---

## 🔌 OpenClaw Skill

If you're using OpenClaw, drop the `skill/` folder into your agent's skills directory:

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
