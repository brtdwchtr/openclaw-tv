#!/usr/bin/env bash
# openclaw-tv installer
# Installs the OpenClaw TV body on a Raspberry Pi 4
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[openclaw-tv]${NC} $*"; }
ok()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[✗]${NC} $*"; exit 1; }

INSTALL_DIR="$HOME/.openclaw-tv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── 1. Check architecture ───────────────────────────────────────────────────
info "Checking system..."
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" ]]; then
    warn "Not running on aarch64 (detected: $ARCH)."
    warn "openclaw-tv is designed for Raspberry Pi 4 (aarch64)."
    read -rp "Continue anyway? [y/N] " confirm
    [[ "$confirm" == "y" || "$confirm" == "Y" ]] || die "Aborted."
fi
ok "Architecture: $ARCH"

# ─── 2. Install uv if missing ────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    ok "uv installed"
else
    ok "uv already installed ($(uv --version))"
fi

# ─── 3. Create Python 3.12 venv ──────────────────────────────────────────────
VENV_DIR="$INSTALL_DIR/venv"
info "Creating Python 3.12 virtual environment at $VENV_DIR..."
mkdir -p "$INSTALL_DIR"
uv venv --python 3.12 "$VENV_DIR"
ok "venv created"

# ─── 4. Install Python dependencies ─────────────────────────────────────────
info "Installing Python dependencies (this may take a few minutes)..."
info "  Pinning torch==2.5.1 (CRITICAL: 2.6+ crashes on Pi 4 Cortex-A72)"

export UV_SKIP_WHEEL_FILENAME_CHECK=1

# Install torch first at the pinned version
uv pip install --python "$VENV_DIR/bin/python" \
    "torch==2.5.1" \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    || die "Failed to install torch. Check your internet connection."

# Install kittentts and audio deps
uv pip install --python "$VENV_DIR/bin/python" \
    kittentts \
    soundfile \
    numpy \
    || die "Failed to install kittentts dependencies."

ok "Python dependencies installed"

# ─── 5. Copy files to ~/.openclaw-tv/ ────────────────────────────────────────
info "Copying files to $INSTALL_DIR..."
cp -r "$SCRIPT_DIR/server"   "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/avatar"   "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/config"   "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/bin"      "$INSTALL_DIR/"

# Create static dir for serving generated audio
mkdir -p "$INSTALL_DIR/static"

# Make CLI executable
chmod +x "$INSTALL_DIR/bin/openclaw-tv"

# Symlink CLI to ~/bin if it exists, otherwise to /usr/local/bin
if [[ -d "$HOME/bin" ]]; then
    ln -sf "$INSTALL_DIR/bin/openclaw-tv" "$HOME/bin/openclaw-tv"
    ok "CLI linked to ~/bin/openclaw-tv"
elif [[ -d "/usr/local/bin" ]]; then
    sudo ln -sf "$INSTALL_DIR/bin/openclaw-tv" "/usr/local/bin/openclaw-tv"
    ok "CLI linked to /usr/local/bin/openclaw-tv"
fi

ok "Files installed to $INSTALL_DIR"

# ─── 6. Install systemd services ─────────────────────────────────────────────
info "Installing systemd services..."
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

# Substitute INSTALL_DIR and USER into service files
sed -e "s|INSTALL_DIR|$INSTALL_DIR|g" \
    -e "s|PI_USER|$USER|g" \
    "$SCRIPT_DIR/config/systemd/openclaw-tv.service" \
    > "$SYSTEMD_DIR/openclaw-tv.service"

sed -e "s|INSTALL_DIR|$INSTALL_DIR|g" \
    -e "s|PI_USER|$USER|g" \
    "$SCRIPT_DIR/config/systemd/openclaw-tv-tts.service" \
    > "$SYSTEMD_DIR/openclaw-tv-tts.service"

systemctl --user daemon-reload
systemctl --user enable openclaw-tv openclaw-tv-tts
ok "Systemd services installed and enabled"

# ─── 7. Set up Chromium kiosk autostart ──────────────────────────────────────
info "Setting up Chromium kiosk autostart..."
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_DIR/openclaw-tv.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=OpenClaw TV Avatar
Exec=bash -c 'sleep 5 && chromium-browser --kiosk --no-sandbox --disable-gpu --password-store=basic --autoplay-policy=no-user-gesture-required http://localhost:8080/avatar/index.html'
X-GNOME-Autostart-enabled=true
EOF

ok "Kiosk autostart configured"

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  openclaw-tv installed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Start services:"
echo "    systemctl --user start openclaw-tv"
echo "    systemctl --user start openclaw-tv-tts"
echo ""
echo "  Test it:"
echo "    openclaw-tv speak \"Hello, I am alive.\" --avatar"
echo ""
echo "  Reboot to start kiosk automatically:"
echo "    sudo reboot"
echo ""
