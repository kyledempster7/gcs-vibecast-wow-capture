#!/usr/bin/env bash
# Install the loopback-only review feedback service. No browser or publish path.
set -euo pipefail
LABEL="com.kyle.gcs.vibecast-review-feedback"
DOMAIN="gui/$(id -u)"
ROOT="${GCS_VIBECAST_ROOT:-/Users/kyle/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker}"
SOURCE="$ROOT/launchagents/${LABEL}.plist"
DEST="$HOME/Library/LaunchAgents/${LABEL}.plist"

if [[ ! -f "$SOURCE" ]]; then
  echo "missing source plist: $SOURCE" >&2
  exit 2
fi
/usr/bin/plutil -lint "$SOURCE"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs/gcs-vibecast-wow"
/usr/bin/install -m 0644 "$SOURCE" "$DEST"
launchctl bootout "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "$DOMAIN" "$DEST"
launchctl enable "$DOMAIN/$LABEL"
launchctl kickstart -k "$DOMAIN/$LABEL"
sleep 1
curl --fail --silent --show-error "http://127.0.0.1:8765/healthz"
echo
echo "INSTALLED label=$LABEL loopback_only=true foreground_control=false"
