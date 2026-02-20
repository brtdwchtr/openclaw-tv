# Software Setup Guide

## Requirements

- Raspberry Pi 4 (2GB+ RAM, 4GB recommended)
- Raspberry Pi OS (64-bit, Bookworm)
- Python 3.12 (via `uv`)
- Network access for installation

---

## Quick Install

```bash
git clone https://github.com/brtdwchtr/openclaw-tv.git
cd openclaw-tv
bash install.sh
```

---

## Manual Setup

If you prefer to set up step by step:

### 1. Install `uv` (Python version manager + package installer)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env
```

### 2. Create Python 3.12 venv

```bash
mkdir -p ~/.openclaw-tv
uv venv --python 3.12 ~/.openclaw-tv/venv
```

### 3. Install dependencies

**CRITICAL version pins:**
- `torch==2.5.1` — PyTorch 2.6+ crashes on Pi 4 Cortex-A72 with "Illegal Instruction"
- Python 3.12 — Kitten TTS doesn't support Python 3.13+

```bash
export UV_SKIP_WHEEL_FILENAME_CHECK=1

# Install PyTorch first (pinned version!)
uv pip install --python ~/.openclaw-tv/venv/bin/python \
    "torch==2.5.1" \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Install TTS and audio dependencies
uv pip install --python ~/.openclaw-tv/venv/bin/python \
    kittentts \
    soundfile \
    numpy
```

### 4. Copy files

```bash
cp -r server/ avatar/ config/ bin/ ~/.openclaw-tv/
mkdir -p ~/.openclaw-tv/static
chmod +x ~/.openclaw-tv/bin/openclaw-tv
```

### 5. Add to PATH

```bash
# Option A: symlink to ~/bin
mkdir -p ~/bin
ln -sf ~/.openclaw-tv/bin/openclaw-tv ~/bin/openclaw-tv

# Option B: add to .bashrc
echo 'export PATH="$HOME/.openclaw-tv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 6. Install systemd services

```bash
INSTALL_DIR="$HOME/.openclaw-tv"
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

# Substitute paths
sed -e "s|INSTALL_DIR|$INSTALL_DIR|g" -e "s|PI_USER|$USER|g" \
    config/systemd/openclaw-tv.service > "$SYSTEMD_DIR/openclaw-tv.service"

sed -e "s|INSTALL_DIR|$INSTALL_DIR|g" -e "s|PI_USER|$USER|g" \
    config/systemd/openclaw-tv-tts.service > "$SYSTEMD_DIR/openclaw-tv-tts.service"

systemctl --user daemon-reload
systemctl --user enable openclaw-tv openclaw-tv-tts
```

### 7. Set up Chromium kiosk autostart

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/openclaw-tv.desktop <<EOF
[Desktop Entry]
Type=Application
Name=OpenClaw TV Avatar
Exec=bash -c 'sleep 5 && chromium-browser --kiosk --no-sandbox --disable-gpu --password-store=basic --autoplay-policy=no-user-gesture-required http://localhost:8080/avatar/index.html'
X-GNOME-Autostart-enabled=true
EOF
```

---

## Starting Services

### Manual start (testing)

```bash
# Terminal 1: web server
openclaw-tv serve

# Terminal 2: TTS daemon  
openclaw-tv daemon

# Terminal 3: test it
openclaw-tv speak "Hello. I am alive." --avatar
```

### Systemd (production)

```bash
systemctl --user start openclaw-tv
systemctl --user start openclaw-tv-tts

# Check status
openclaw-tv status

# Enable on boot (requires lingering)
loginctl enable-linger $USER
```

---

## Kiosk Mode Setup

### Chromium flags explained

```bash
chromium-browser \
  --kiosk \                               # Full screen, no browser chrome
  --no-sandbox \                          # Required for Pi/kiosk use
  --disable-gpu \                         # Avoids GPU driver issues on Pi
  --password-store=basic \               # No keyring popup
  --autoplay-policy=no-user-gesture-required \  # Allow audio autoplay!
  http://localhost:8080/avatar/index.html
```

**`--autoplay-policy=no-user-gesture-required` is essential** — without it, the audio won't play automatically.

### Hide the cursor

```bash
sudo apt install -y unclutter
# Add to autostart:
echo 'unclutter -idle 0 -root &' >> ~/.bashrc
```

### Prevent screen blanking

```bash
# In ~/.config/lxsession/LXDE-pi/autostart (or equivalent):
@xset s off
@xset -dpms
@xset s noblank
```

---

## OpenClaw Skill Installation

If you're using OpenClaw as your agent framework:

```bash
cp -r skill/ ~/clawd/skills/openclaw-tv/
```

Your agent will automatically pick up the skill instructions.

---

## Testing Without a Display

You can test the server and TTS without a physical display:

```bash
# Start server
openclaw-tv serve &

# Start TTS daemon
openclaw-tv daemon &

# Generate speech only (no avatar push)
openclaw-tv speak "Test message." --voice Hugo
# (plays through speaker)

# Check avatar API
curl http://localhost:8080/api/state
```

Access the avatar in any browser:
```
http://your-pi.local:8080/avatar/index.html
```

---

## Updating

```bash
cd ~/openclaw-tv
git pull
bash install.sh
systemctl --user restart openclaw-tv openclaw-tv-tts
```
