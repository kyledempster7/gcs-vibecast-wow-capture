#!/usr/bin/env bash
# M1: One-command Mac offsite backup for GCS·VibeCast (code/docs/receipts/indexes).
# No masters dump. No secrets. No Factory paths.
set -euo pipefail
WOW="${WOW_ROOT:-$HOME/Kyles_Vault/kyles_corner/Games/WoW}"
SCRIPTS="$WOW/wow-roster-tracker/scripts"
RECEIPTS="$HOME/Library/Application Support/UAH/butler/control-plane/receipts/wow"
MEDIA="$HOME/Movies/WoW-Broll-Workflow"
REPO="${GCS_VIBECAST_REPO:-$HOME/src/gcs-vibecast-wow-capture}"
PLIST="$HOME/Library/LaunchAgents/com.kyle.gcs.wow-soft-poll-harvest.plist"
TS=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$RECEIPTS"

AUTH_REPO=$(git -C "$WOW" rev-parse --show-toplevel)
AUTH_BRANCH=$(git -C "$AUTH_REPO" branch --show-current)
EXPECTED_AUTH_BRANCH=$(python3 "$SCRIPTS/resolve_windows_host.py" --authority-branch)
if [[ "$AUTH_BRANCH" != "$EXPECTED_AUTH_BRANCH" ]]; then
  echo "BACKUP_WARN_NON_AUTHORITY current=$AUTH_BRANCH expected=$EXPECTED_AUTH_BRANCH — backing up live scripts anyway"
fi

LOCKDIR="$HOME/Library/Logs/gcs-vibecast-wow/mac_backup_vibecast.lockdir"
PIDFILE="$LOCKDIR/pid"
release_backup_lock() {
  rm -f "$PIDFILE" 2>/dev/null || true
  rmdir "$LOCKDIR" 2>/dev/null || true
}
mkdir -p "$(dirname "$LOCKDIR")"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  OLD_PID=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null \
    && ps -p "$OLD_PID" -o command= 2>/dev/null | grep -q 'mac_backup_vibecast\.sh'; then
    echo "BACKUP_SKIP_ALREADY_RUNNING pid=$OLD_PID"
    exit 0
  fi
  rm -f "$PIDFILE" 2>/dev/null || true
  if ! rmdir "$LOCKDIR" 2>/dev/null || ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "BACKUP_LOCK_UNKNOWN_CONTENT preserve=$LOCKDIR" >&2
    exit 2
  fi
fi
echo "$$" >"$PIDFILE"
trap release_backup_lock EXIT

DRIVE="$(python3 "$SCRIPTS/resolve_windows_host.py" --drive-offload)"
if [[ -z "$DRIVE" ]]; then
  echo "DRIVE_MISSING GCS-VibeCast-Offload" >&2
  exit 2
fi
if [[ ! -d "$DRIVE" ]]; then
  echo "DRIVE_MISSING configured path: $DRIVE" >&2
  exit 2
fi
BC="$DRIVE/backup-code"
mkdir -p "$BC/gcs-vibecast-wow-capture" "$BC/receipts-wow" "$BC/moments-index" \
  "$BC/launchagents" "$BC/00-Index-pins" "$BC/RESTORE" "$BC/authority-bundles" \
  "$BC/returns-working-set"

echo "== mac_backup_vibecast ts=$TS =="
python3 "$SCRIPTS/assert_vibecast_write_fence.py"
# Dual-SoT: always redeploy Windows-facing scripts (gauntlet #19/#82)
if [[ -f "$SCRIPTS/deploy_windows_scripts.sh" ]]; then
  bash "$SCRIPTS/deploy_windows_scripts.sh" || echo "WARN deploy_windows non-zero"
fi
# Log rotate (gauntlet #85)
if [[ -f "$SCRIPTS/rotate_gcs_logs.sh" ]]; then
  bash "$SCRIPTS/rotate_gcs_logs.sh" || true
fi
# Schema audit snapshot (decades #96)
if [[ -f "$SCRIPTS/schema_audit.py" ]]; then
  python3 "$SCRIPTS/schema_audit.py" || true
fi

# --- GitHub working tree ---
if [[ -d "$REPO/.git" ]]; then
  rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' --exclude '.DS_Store' \
    "$SCRIPTS/" "$REPO/scripts/"
  mkdir -p "$REPO/docs/04-Story-and-Capture" "$REPO/docs/00-Index" "$REPO/launchagents" "$REPO/extensions"
  # Product doctrine (markdown/json/html only — skip heavy binaries if any)
  rsync -a --delete \
    --exclude 'GCS_PIPELINE_HEALTH_LATEST.md' \
    --include '*/' \
    --include '*.md' --include '*.json' --include '*.html' --include '*.txt' --include '*.seed.md' \
    --exclude '*' \
    "$WOW/04-Story-and-Capture/" "$REPO/docs/04-Story-and-Capture/"
  rsync -a "$WOW/04-Story-and-Capture/hyperframes-brand-kit/" \
    "$REPO/docs/04-Story-and-Capture/hyperframes-brand-kit/" || true
  if [[ -d "$WOW/wow-roster-tracker/launchagents" ]]; then
    rsync -a --delete "$WOW/wow-roster-tracker/launchagents/" "$REPO/launchagents/"
  fi
  if [[ -d "$WOW/wow-roster-tracker/extensions" ]]; then
    rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' "$WOW/wow-roster-tracker/extensions/" "$REPO/extensions/"
  fi
  for f in GCS_CITADEL.md VIBECAST_OS.md MEDIA_SOR_DUAL_MACHINE.md KYLE_OS.md \
           TODAY_WINDOWS_SESSION.md media_roots.json GITHUB_PORTABLE.md GCS_STATUS.md \
           VIBECAST_STATUS.md PRODUCT_THESIS_VIBECAST.md GCS_PIPELINE_HEALTH.md; do
    [[ -f "$WOW/00-Index/$f" ]] && cp "$WOW/00-Index/$f" "$REPO/docs/00-Index/" || true
  done
  [[ -f "$PLIST" ]] && cp "$PLIST" "$REPO/launchagents/" || true
else
  echo "WARN repo missing $REPO"
fi

# --- Drive ---
if [[ -d "$REPO" ]]; then
  rsync -a --delete --exclude '.git' --exclude '__pycache__' --exclude '.DS_Store' \
    "$REPO/" "$BC/gcs-vibecast-wow-capture/"
fi
rsync -a --delete --exclude '.DS_Store' "$RECEIPTS/" "$BC/receipts-wow/"
if [[ -d "$MEDIA/Returns" ]]; then
  rsync -a --delete --include '*/' --include '*.json' --include '*.md' --include '*.html' --include '*.txt' --include '*.csv' --include '*.xml' --include '*.fcpxml' --include '*.jpg' --include '*.jpeg' --include '*.png' --include '.harvest_once' --exclude '*' "$MEDIA/Returns/" "$BC/returns-working-set/"
fi
if [[ -d "$MEDIA/Moments-Library" ]]; then
  for f in CATALOG.json KEEP_ONLY_INDEX.json KEEP_ONLY_INDEX.md README.md; do
    [[ -f "$MEDIA/Moments-Library/$f" ]] && cp "$MEDIA/Moments-Library/$f" "$BC/moments-index/" || true
  done
fi
[[ -f "$PLIST" ]] && cp "$PLIST" "$BC/launchagents/" || true
for f in GCS_CITADEL.md VIBECAST_OS.md MEDIA_SOR_DUAL_MACHINE.md KYLE_OS.md \
         TODAY_WINDOWS_SESSION.md media_roots.json VIBECAST_STATUS.md; do
  [[ -f "$WOW/00-Index/$f" ]] && cp "$WOW/00-Index/$f" "$BC/00-Index-pins/" || true
done
cp "$WOW/04-Story-and-Capture/RESTORE_AND_BACKUP.md" "$BC/RESTORE/" 2>/dev/null || true
cp "$WOW/04-Story-and-Capture/VIBECAST_WRITE_FENCE.md" "$BC/RESTORE/" 2>/dev/null || true

# --- Git commit/push ---
PUSH_RC=0
if [[ -d "$REPO/.git" ]]; then
  set +e
  (
    cd "$REPO"
    git add -- scripts docs launchagents extensions
    if git diff --cached --quiet; then
      echo "GIT clean no commit"
    else
      git commit -m "mac_backup_vibecast $TS — scripts docs fence restore pins"
    fi
    git push origin main
  )
  PUSH_RC=$?
  set -e
fi

BUNDLE="$BC/authority-bundles/gcs-vibecast-authority.bundle"
BUNDLE_OK=false
if [[ -n "$AUTH_BRANCH" ]]; then
  BUNDLE_TMP="$BUNDLE.tmp"
  rm -f "$BUNDLE_TMP"
  if git -C "$AUTH_REPO" bundle create "$BUNDLE_TMP" "$AUTH_BRANCH" \
    && git -C "$AUTH_REPO" bundle verify "$BUNDLE_TMP" >/dev/null; then
    mv -f "$BUNDLE_TMP" "$BUNDLE"
    BUNDLE_OK=true
  fi
fi

COUNT_R=$( { rg --files "$BC/receipts-wow" 2>/dev/null || true; } | wc -l | tr -d ' ')
COUNT_S=$( { rg --files "$BC/gcs-vibecast-wow-capture/scripts" 2>/dev/null || true; } | wc -l | tr -d ' ')
COUNT_E=$( { rg --files "$BC/gcs-vibecast-wow-capture/extensions" 2>/dev/null || true; } | wc -l | tr -d ' ')
COUNT_W=$( { rg --files --hidden "$BC/returns-working-set" 2>/dev/null || true; } | wc -l | tr -d ' ')
WORKING_SET_OK=false
if [[ "$COUNT_W" -gt 0 && -f "$BC/returns-working-set/SOFT_POLL_LATEST.json" ]]; then
  WORKING_SET_OK=true
fi
cat > "$RECEIPTS/MAC_BACKUP_VIBECAST_${TS}.md" <<EOF
# Mac backup VibeCast — $TS
**Drive:** $BC
**scripts_files:** $COUNT_S
**extension_files:** $COUNT_E
**returns_working_set_files:** $COUNT_W
**returns_working_set_verified:** $WORKING_SET_OK
**receipts_files:** $COUNT_R
**git_push_rc:** $PUSH_RC
**authority_branch:** $AUTH_BRANCH
**authority_bundle_verified:** $BUNDLE_OK
**repo:** $REPO
**law:** no_masters_in_github; no_factory_paths; no_secrets
EOF
cp "$RECEIPTS/MAC_BACKUP_VIBECAST_${TS}.md" "$RECEIPTS/MAC_BACKUP_VIBECAST_LATEST.md"
python3 - "$RECEIPTS/MAC_BACKUP_VIBECAST_LATEST.json" "$TS" "$BC" "$COUNT_S" "$COUNT_E" "$COUNT_W" "$WORKING_SET_OK" "$COUNT_R" "$PUSH_RC" "$AUTH_BRANCH" "$BUNDLE" "$BUNDLE_OK" <<'PY'
import json, sys
from pathlib import Path

out, ts, drive, scripts, extensions, working_set, working_set_ok, receipts, push_rc, branch, bundle, bundle_ok = sys.argv[1:]
body = {
    "schema": "gcs_vibecast_backup/v4",
    "utc_stamp": ts,
    "status": "PASS" if int(push_rc) == 0 and bundle_ok == "true" and working_set_ok == "true" else "PARTIAL",
    "drive_backup_code": drive,
    "script_files": int(scripts),
    "extension_files": int(extensions),
    "returns_working_set_files": int(working_set),
    "returns_working_set_verified": working_set_ok == "true",
    "receipt_files": int(receipts),
    "public_sample_push_rc": int(push_rc),
    "authority_branch": branch,
    "authority_bundle": bundle,
    "authority_bundle_verified": bundle_ok == "true",
    "masters_copied": False,
    "may_publish": False,
    "provider_effects": ["git_push_public_sample", "google_drive_sync_surface"],
}
Path(out).write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
PY
echo "BACKUP_OK drive=$BC scripts=$COUNT_S extensions=$COUNT_E working_set=$COUNT_W receipts=$COUNT_R git_push_rc=$PUSH_RC bundle_ok=$BUNDLE_OK working_set_ok=$WORKING_SET_OK"
if [[ "$PUSH_RC" -ne 0 || "$BUNDLE_OK" != "true" || "$WORKING_SET_OK" != "true" ]]; then
  exit 2
fi
exit 0
