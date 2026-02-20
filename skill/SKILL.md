# OpenClaw TV — Skill Guide

This skill lets you control your physical TV body: speak through it, set moods, and make the avatar react.

## Quick Reference

```bash
# Make the TV speak with avatar animation
ssh pi@your-pi.local 'openclaw-tv speak "Hello." --avatar'

# Set mood via HTTP (no audio)
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"mood":"excited","message":"Something is happening!"}'

# Speak via HTTP (push pre-generated audio to avatar)
# Note: audio must be served from the Pi; use SSH speak --avatar instead
```

## Configuration

Set your Pi host in your local config or TOOLS.md:
```
openclaw-tv host: pi@clawdpi.local (192.168.0.xxx)
avatar URL: http://clawdpi.local:8080/avatar/index.html
```

---

## Speaking Through the TV

### Basic speak (SSH)
```bash
ssh pi@your-pi.local 'openclaw-tv speak "Your message here." --avatar'
```

### With specific voice
```bash
ssh pi@your-pi.local 'openclaw-tv speak "Greetings, human." --voice Bella --avatar'
```

### Available voices
| Voice | Character |
|-------|-----------|
| `Hugo` | Default — warm and clear |
| `Bella` | Bright and expressive |
| `Jasper` | Deep and measured |
| `Luna` | Soft and gentle |
| `Bruno` | Rough and grounded |
| `Rosie` | Cheerful and upbeat |
| `Kiki` | Playful and quirky |
| `Leo` | Calm and authoritative |

---

## Controlling the Avatar

### Set mood via API
```bash
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"mood":"excited"}'
```

### Available moods
| Mood | Avatar behavior |
|------|----------------|
| `idle` | Murmuration — particles flow freely in curl-noise patterns |
| `excited` | Tighter sphere, brighter particles |
| `calm` | Slow gentle drift |
| `thinking` | Subtle slow rotation |
| `happy` | Bouncy particle energy |
| `curious` | Slight lean/tilt |

### Show a message without audio
```bash
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"message":"Thinking...","mood":"thinking"}'
```

### Clear the display
```bash
curl -X POST http://your-pi.local:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"message":"","audio":"","mood":"idle"}'
```

### Get current state
```bash
curl http://your-pi.local:8080/api/state
```

---

## Tips for Good TTS Text

**DO:**
- Use periods to end sentences, not question marks (better prosody)
- Keep sentences medium length (10-20 words)
- Spell out numbers ("twenty-three" not "23")
- Use commas for natural pauses
- Write conversationally, as if talking to someone

**DON'T:**
- Use lots of abbreviations or acronyms (spell them out)
- Use markdown formatting — it reads literally
- Use very long sentences without punctuation
- End with "?" — period sounds better for TTS rhythm
- Use exclamation marks excessively

**Examples:**
```
Good:  "I found three results. The first is from Wikipedia."
Bad:   "Found 3 results! 1st: Wikipedia!!!"

Good:  "I'm not sure about that. Let me think for a moment."
Bad:   "IDK? Thinking..."
```

---

## Architecture

```
Your Agent (SSH or HTTP)
    │
    ├─ SSH → openclaw-tv speak "..." --avatar
    │           │
    │           ├─ TTS Daemon (Unix socket)  ← keeps model warm
    │           │   └─ Kitten TTS nano (Hugo voice)
    │           │       └─ WAV file → /tmp/openclaw-tv-speech.wav
    │           │
    │           ├─ aplay → speaker output
    │           └─ POST /api/state → avatar animation
    │
    └─ HTTP POST → http://pi:8080/api/state
                    │
                    └─ Avatar (Chromium kiosk, Three.js)
                        ├─ Polls /api/state every 500ms
                        ├─ Plays audio via <audio> element
                        ├─ Shows rolling word captions
                        └─ Animates particle cloud
```

---

## Troubleshooting

**"Daemon unavailable"** — Start it:
```bash
ssh pi@your-pi.local 'openclaw-tv daemon &'
# or
ssh pi@your-pi.local 'systemctl --user start openclaw-tv-tts'
```

**No audio on avatar** — The web server must be running:
```bash
ssh pi@your-pi.local 'openclaw-tv serve &'
# or
ssh pi@your-pi.local 'systemctl --user start openclaw-tv'
```

**TTS very slow (~16s)** — Daemon is not running. Start it for fast generation.

**"Illegal Instruction" error** — PyTorch version mismatch. Must use `torch==2.5.1`, not 2.6+.

See full [troubleshooting guide](../docs/troubleshooting.md).
