# Stream Deck → record marker sidecar (contract v0)

**Status:** Mac-authored contract for Windows Codex implement  
**Goal:** When Kyle hits multi-actions (Enter b-roll · Begin rotate · etc.), stamp **intent** next to the OBS session so agents cut on *human state*, not dumb time slices.

## Law

- Sidecar is **machine-readable SoT** for markers.  
- Optional: also fire OBS hotkey / chapter if available — never replace the sidecar.  
- **No publish** from markers alone.  
- Do not require Kyle to re-speak button IDs after a night.

## File location (Windows)

```
D:\WoW B-Roll Storage\<YYYY-MM-DD>\
  markers\
    SESSION.jsonl          # append-only, one event per line
  candidates\
  proxy\
  MANIFEST.json
```

If OBS still lands under Fable profile folder, **also** write a pointer row with `obs_output_path` when record starts.

## Event schema (one JSON object per line)

```json
{
  "schema": "gcs_obs_marker/v1",
  "ts_utc": "2026-08-09T23:15:01.123Z",
  "ts_local": "2026-08-09T19:15:01.123-04:00",
  "host": "3900x",
  "session_id": "2026-08-09T19-00-00",
  "button_id": "layer_c.broll_enter",
  "label": "Enter b-roll",
  "state": "begin",
  "obs_output_path": "D:\\WoW B-Roll Storage\\2026-08-09\\raw\\....mp4",
  "recording": true,
  "source": "stream_deck"
}
```

| Field | Required | Notes |
|-------|----------|--------|
| `ts_utc` | yes | ISO-8601 |
| `button_id` | yes | stable machine id |
| `label` | yes | human string |
| `state` | yes | `begin` \| `end` \| `pulse` |
| `session_id` | yes | day or record-start stamp |
| `obs_output_path` | when known | join to file later |
| `recording` | yes | false = ignore for cuts |

## Button map (v0 — extend, don’t rename)

| button_id | Label (spoken) | state | Agent meaning |
|-----------|----------------|-------|----------------|
| `layer_c.broll_enter` | Enter b-roll | begin | Prefer next N minutes as b-roll |
| `layer_c.broll_exit` | Exit b-roll | end | Stop b-roll prefer window |
| `layer_c.rotate_begin` | Begin rotate | begin | Rotate / establish start |
| `layer_c.rotate_end` | End rotate | end | Rotate end |
| `layer_c.talk_peak` | Talk peak | pulse | Personality / VO-ish moment |
| `layer_c.skip_zone` | Skip / bad | pulse | Mark reject region |
| `layer_c.record_mark` | Chapter mark | pulse | Generic scrub point |
| `layer_c.gather_ui_on` | Gather UI ON | begin | Gathering B-Roll mode on (`WOWCAP.GATHER_UI_ON`) |
| `layer_c.gather_ui_off` | Gather UI OFF | end | Gathering B-Roll mode off (`WOWCAP.GATHER_UI_OFF`) |

Wire these to Stream Deck multi-actions **after** existing game binds — capture layer / Vault-Tec, not Layer A combat.  
Gathering mode SoT: `04-Story-and-Capture/GATHERING_BROLL_MODE.md` (Alt+Z unchanged).

## Join rule (Mac or Windows post)

1. Load `SESSION.jsonl` for the day.  
2. Load master duration + mtime or OBS record start.  
3. Convert marker `ts_utc` → **seconds into file** (needs record_start_utc in first row or OBS log).  
4. Export ship candidates **only** inside `broll_enter…broll_exit` windows and/or ±15s around `talk_peak` / `rotate_*`.  
5. Never ship regions marked `skip_zone` within ±5s.

## Minimum Windows deliverable (Codex)

1. Folder `markers\` created by post-night or on first Deck press.  
2. One PowerShell or Stream Deck CLI hook that **appends** a JSONL line (fail-open: if path missing, create).  
3. Prove with one manual fire: file gains a line; receipt path.  
4. Document which Deck profile/page owns Layer C capture.

## Out of scope v0

- Embedding chapters inside MP4 atoms (nice later).  
- AI classifying load screens without markers (Mac has auto black probe; complement not replace).  
- Auto-publish.

## Related

- Mac reject probe: `Returns/…/analysis/REJECT_PROBE.json`  
- Export: `Export-ShipCandidates.ps1`  
- Human feedback: `Returns/…/CANDIDATE_FEEDBACK.md`  
