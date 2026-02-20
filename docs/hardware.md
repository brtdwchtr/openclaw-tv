# Hardware Setup

## Components

| Part | Purpose | Notes |
|------|---------|-------|
| Raspberry Pi 4 (2GB+) | The brain | 4GB recommended for headroom |
| USB SSD (120GB+) | Boot drive | Much faster than SD card |
| Any display | Shows avatar | HDMI, composite, or via RF modulator |
| Speaker | Audio output | 3.5mm jack or USB audio |
| TRRS cable | Composite video | Only if using composite/CRT |
| RF modulator | Signal conversion | Only if using old CRT TV |

---

## HDMI Setup (Modern Display)

The simplest setup — just plug in an HDMI cable.

```
Pi 4 ──HDMI──▶ Monitor/TV
```

Enable compositing in `/boot/firmware/config.txt`:
```ini
dtoverlay=vc4-kms-v3d
```

---

## Composite Video Setup (CRT / Vintage TV)

This is the full retro setup. More complex but worth it.

```
Pi 4
 └─ 3.5mm ──TRRS cable──▶ RF Modulator ──F-to-IEC──▶ CRT TV antenna input
                ↑
           Video on RED plug
           (NOT yellow — that's TRRS wiring, not RCA)
```

### Step 1: Pi config

Edit `/boot/firmware/config.txt`:
```ini
# Enable composite output (disables HDMI)
dtoverlay=vc4-kms-v3d,composite

# PAL (Europe) resolution
# cmdline.txt: video=Composite-1:720x576@50ie
```

Edit `/boot/firmware/cmdline.txt` — add to the end:
```
video=Composite-1:720x576@50ie
```

### Step 2: X11 (not Wayland)

Wayland does **not** work with composite output. Must use X11:
```bash
sudo raspi-config
# Advanced Options → Wayland → X11/openbox
```

Or set in `/etc/environment`:
```bash
WAYLAND_DISPLAY=
XDG_SESSION_TYPE=x11
```

### Step 3: TRRS cable wiring

The Pi's 3.5mm jack uses TRRS (4-pole):
```
TIP   = Left audio
RING1 = Right audio  
RING2 = Ground
SLEEVE = Composite video
```

Standard RCA cables won't work properly. Use a **Pi-compatible TRRS cable** or adapter.

**⚠️ Critical:** The video signal comes out on the **RED plug** of most TRRS-to-3xRCA adapters (not yellow as you might expect).

### Step 4: RF modulator

For TVs without composite input (only antenna/coax input):
1. Connect Pi's composite out → RF modulator video in
2. Connect RF modulator → TV antenna input (via F-to-IEC or coax adapter)
3. **Power the RF modulator from a SEPARATE USB charger** — not the Pi's USB ports. Powering from the Pi causes I/O errors.
4. Tune TV to channel 3 or 4 (check your modulator's switch)

### Step 5: Hide cursor

```bash
sudo apt install unclutter
# Cursor hides after 0 seconds of inactivity:
unclutter -idle 0 -root &
```

---

## Audio Setup

### 3.5mm jack (built-in)
```bash
# Set audio output to 3.5mm
raspi-config → System Options → Audio → Headphones
```

### USB audio adapter
```bash
# List devices
aplay -l
# Set default (replace card number)
echo 'defaults.pcm.card 1' >> ~/.asoundrc
echo 'defaults.ctl.card 1' >> ~/.asoundrc
```

---

## Verified Working Setup

This is the exact setup used in development:

```
Raspberry Pi 4 Model B (4GB)
 ├─ Boot: 120GB USB SSD
 ├─ Display: Vintage B&W CRT (PAL)
 │    └─ TRRS → RF modulator (separate USB power) → antenna → CRT
 ├─ Audio: 3.5mm to speaker
 └─ Network: Ethernet (more reliable than WiFi for kiosk)
```

---

## Troubleshooting Hardware

**No composite signal:**
- Check `dtoverlay=vc4-kms-v3d,composite` is in config.txt
- Check you're using X11 not Wayland
- Try rebooting after config changes

**Video is black and white / noisy:**
- Use correct TRRS cable (Pi-compatible, not phone headset cable)
- Video is on RED plug
- Check RF modulator tuning (channel 3/4)

**Crackling audio / I/O errors:**
- RF modulator drawing power from Pi USB — use separate charger!

**Screen flickers:**
- Add to config.txt: `config_hdmi_boost=4` (if HDMI) or try lower refresh rate

See [troubleshooting.md](troubleshooting.md) for software issues.
