#!/usr/bin/env bash
# Install LaunchAgent: soft_poll+harvest every 30m — loop enforces play-night quiet hours.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.kyle.gcs.wow-soft-poll-harvest"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
LOOP="$SCRIPTS/mac_soft_poll_harvest_loop.sh"
chmod +x "$LOOP" "$SCRIPTS/soft_poll_windows.sh" "$SCRIPTS/harvest_if_ready.sh" 2>/dev/null || true
mkdir -p "${HOME}/Library/LaunchAgents" "${HOME}/Library/Logs/gcs-vibecast-wow"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${LOOP}</string>
  </array>
  <key>StartInterval</key>
  <integer>1800</integer>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>${HOME}/Library/Logs/gcs-vibecast-wow/launchagent.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${HOME}/Library/Logs/gcs-vibecast-wow/launchagent.stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>ProcessType</key>
  <string>Background</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true
echo "INSTALLED $PLIST interval=1800s quiet_hours_in_loop=03-19 local RunAtLoad=false"
launchctl print "gui/$(id -u)/${LABEL}" 2>/dev/null | head -30 || true
