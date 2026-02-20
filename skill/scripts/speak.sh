#!/usr/bin/env bash
# openclaw-tv speak wrapper — SSH to Pi and speak
# Usage: speak.sh "Your message" [voice] [pi-host]
#
# Examples:
#   speak.sh "Hello, world!"
#   speak.sh "Hello." Hugo clawdpi.local
#   PI_HOST=192.168.0.133 speak.sh "Testing."

set -euo pipefail

TEXT="${1:-}"
VOICE="${2:-Hugo}"
PI_HOST="${3:-${PI_HOST:-clawdpi.local}}"
PI_USER="${PI_USER:-bart}"

if [[ -z "$TEXT" ]]; then
  echo "Usage: speak.sh \"text\" [voice] [pi-host]" >&2
  exit 1
fi

echo "→ Speaking on $PI_HOST: \"$TEXT\" ($VOICE)"
ssh "${PI_USER}@${PI_HOST}" "openclaw-tv speak $(printf '%q' "$TEXT") --voice $VOICE --avatar"
