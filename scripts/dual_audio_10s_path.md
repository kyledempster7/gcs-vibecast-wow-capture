# Controlled 10s dual-audio path (T3)

**Law:** never invent AUDIO_GREEN · no publish
**Stamp:** `04-Story-and-Capture/AUDIO_GREEN_STAMP.md`
**Probe:** `audio_green_probe.py`

## Purpose

Prove mic + game stems on a short recording **before** a full play night is treated as PRODUCT_GREEN for dual audio.

## Windows (human, ~60s)

1. OBS profile **WoW B-Roll** · path `D:\WoW B-Roll Storage` · RecTracks=3
2. Press **Record**
3. Talk for ~5s while game audio is present
4. **Stop** Record
5. Confirm a new mp4 on `D:\WoW B-Roll Storage` (or day `\raw` after Session-End)

Optional Session-End (after stop, masters stable):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
```

## Mac (agent or Kyle)

```bash
# Copy one 10s+ file to Mac (example path after harvest or scp)
FILE="/Users/kyle/Movies/WoW-Broll-Workflow/Returns/returner-daily-YYYY-MM-DD/candidates/SOME.mp4"

python3 wow-roster-tracker/scripts/audio_green_probe.py \
  --file "$FILE" \
  --out-json "$HOME/Movies/WoW-Broll-Workflow/Returns/AUDIO_GREEN_PROBE_LATEST.json"

# Only if dual stems prove green:
python3 wow-roster-tracker/scripts/audio_green_probe.py \
  --file "$FILE" \
  --write-stamp \
  --out-json "$HOME/Movies/WoW-Broll-Workflow/Returns/AUDIO_GREEN_PROBE_LATEST.json"
```

Or use the wrapper:

```bash
bash wow-roster-tracker/scripts/run_dual_audio_10s_probe.sh /abs/path/to/test.mp4
```

## Done-when

| Field | Green |
|-------|--------|
| File exists | real path |
| ≥2 audio streams **or** honest single-track note | probe JSON |
| Stamp status GREEN | only with `--write-stamp` after dual proof |
| OPEN remains legal | if only one stem |

## Not green

- RecTracks=3 alone
- Soft_poll ready
- League dry montage
