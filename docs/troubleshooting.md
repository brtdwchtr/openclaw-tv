# Troubleshooting

## TTS Issues

### "Illegal Instruction" when running TTS

**Cause:** PyTorch version too new for Pi 4's Cortex-A72 CPU.

**Fix:** Reinstall with the pinned version:
```bash
export UV_SKIP_WHEEL_FILENAME_CHECK=1
uv pip install --python ~/.openclaw-tv/venv/bin/python "torch==2.5.1"
```

PyTorch 2.6+ drops support for older ARM instruction sets. **Always use 2.5.1.**

---

### TTS sounds robotic / wrong prosody

**Cause:** The `clean_text` preprocessor is mangling the text.

**Fix:** This is already handled in the daemon and CLI (`clean_text=False`). If you're calling the model directly, always pass `clean_text=False`:

```python
# CORRECT
audio = model.model.generate(text, voice="Hugo", clean_text=False)

# WRONG — breaks prosody
audio = model.model.generate(text, voice="Hugo")
```

---

### TTS very slow (~16 seconds first run)

**Expected:** The model takes ~16s to load cold. After that, it's ~0.7× realtime.

**Fix:** Start the TTS daemon to keep the model in memory:
```bash
openclaw-tv daemon &
# or
systemctl --user start openclaw-tv-tts
```

Subsequent requests through the daemon take ~1-2 seconds instead of 16.

---

### "Python version not supported" / kittentts install fails

**Cause:** Python 3.13+ is not supported by Kitten TTS.

**Fix:** Force Python 3.12:
```bash
uv venv --python 3.12 ~/.openclaw-tv/venv
```

Check your version:
```bash
~/.openclaw-tv/venv/bin/python --version
# Should say: Python 3.12.x
```

---

### No audio output

```bash
# List audio devices
aplay -l

# Test speaker
aplay /usr/share/sounds/alsa/Front_Center.wav

# Check ALSA default device
cat ~/.asoundrc
# If missing or wrong:
# echo 'defaults.pcm.card 0' > ~/.asoundrc
```

---

## Avatar / Web Server Issues

### Avatar not loading in browser

1. Check server is running: `openclaw-tv status`
2. Try: `curl http://localhost:8080/api/state`
3. Check port isn't blocked: `ss -tlnp | grep 8080`

Start manually:
```bash
openclaw-tv serve
```

---

### Audio plays but avatar doesn't animate

**Cause:** Avatar hasn't received the audio URL via `/api/state`.

**Fix:** Use `--avatar` flag when speaking:
```bash
openclaw-tv speak "Hello." --avatar
```

Or push manually:
```bash
curl -X POST http://localhost:8080/api/state \
  -H 'Content-Type: application/json' \
  -d '{"audio":"/static/speech.wav?t=1234","message":"Hello","mood":"talking"}'
```

---

### Browser autoplay blocked (no audio in kiosk)

**Cause:** Chromium blocks autoplay without `--autoplay-policy=no-user-gesture-required`.

**Fix:** Add the flag to your Chromium launch command:
```bash
chromium-browser --kiosk --autoplay-policy=no-user-gesture-required \
  http://localhost:8080/avatar/index.html
```

Check your autostart file has this flag.

---

### Particles not visible / black screen

1. Check WebGL is working: open `chrome://gpu` in Chromium
2. If GPU is unavailable, try removing `--disable-gpu` flag
3. Check Three.js CDN is reachable (needs internet first load)
   - For offline use, download Three.js locally:
     ```bash
     curl -o ~/.openclaw-tv/avatar/three.min.js \
       https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
     ```
   - Then update `index.html` to use local path: `<script src="/avatar/three.min.js">`

---

## Composite / CRT Display Issues

### No signal on TV

1. Check `dtoverlay=vc4-kms-v3d,composite` in `/boot/firmware/config.txt`
2. Check `video=Composite-1:720x576@50ie` in `/boot/firmware/cmdline.txt`
3. **Use X11, not Wayland** — run `raspi-config` → Advanced → Wayland → X11
4. Reboot after any config changes

---

### Black and white image / no color

- Composite signal from Pi is often B&W on PAL CRTs — this is normal for some CRT models
- Check TRRS cable: video is on **RED plug**, not yellow
- Try a different TRRS cable (phone headset cables don't work)

---

### I/O errors, audio crackling, Pi instability

**Cause:** RF modulator powered from Pi USB.

**Fix:** Power the RF modulator from a **separate USB charger** (any 5V/1A charger). Never from the Pi's USB ports.

---

### Screen shows desktop instead of avatar

The kiosk autostart may not be running. Check:
```bash
ls ~/.config/autostart/openclaw-tv.desktop
cat ~/.config/autostart/openclaw-tv.desktop
```

Manually launch kiosk:
```bash
DISPLAY=:0 chromium-browser --kiosk --no-sandbox --autoplay-policy=no-user-gesture-required \
  http://localhost:8080/avatar/index.html &
```

---

## Systemd Service Issues

### Services not starting

```bash
# Check status and logs
systemctl --user status openclaw-tv
systemctl --user status openclaw-tv-tts
journalctl --user -u openclaw-tv -n 50
journalctl --user -u openclaw-tv-tts -n 50
```

### Services don't start on boot

```bash
# Enable lingering (allows user services to start without login)
loginctl enable-linger $USER

# Verify
loginctl show-user $USER | grep Linger
# Should say: Linger=yes
```

---

## Getting Help

If you're stuck:

1. Check `openclaw-tv status`
2. Check logs: `journalctl --user -u openclaw-tv -f`
3. File an issue: https://github.com/brtdwchtr/openclaw-tv/issues
