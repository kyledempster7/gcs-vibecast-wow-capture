---
type: install-card
status: active
created: 2026-08-10
owner: Windows
rank: ROADMAP P0-1
---

# Stream Deck multi-actions — install card (Layer C)

**Script (SoR on Windows):** `D:\WoW B-Roll Storage\_scripts\Append-StreamDeckMarker.ps1`  
**Map:** `D:\WoW B-Roll Storage\_scripts\DECK_BUTTON_MAP.md`  
**Mac mirror:** `Games/WoW/wow-roster-tracker/scripts/Append-StreamDeckMarker.ps1`  
**Canon gather:** [[GATHERING_BROLL_MODE]]

## Done when (product, not agent_prove)

Human press mid-session writes `markers\SESSION.jsonl` rows for real play (not only `agent_prove_*` labels).  
Join produces non-empty windows for that night.

## Wire each button (Stream Deck software)

**Action type:** System → Open (or Multi Action: Open + hotkey)

```
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Append-StreamDeckMarker.ps1" -ButtonId <ID> -Label "<Label>" -State <begin|end|pulse>
```

| ButtonId | Label | State | Multi-action extras |
|----------|-------|-------|---------------------|
| `layer_c.record_start` | Record start | begin | First press of night — **before** or with OBS record |
| `layer_c.broll_enter` | Enter b-roll | begin | optional OBS chapter |
| `layer_c.broll_exit` | Exit b-roll | end | |
| `layer_c.rotate_begin` | Begin rotate | begin | |
| `layer_c.rotate_end` | End rotate | end | |
| `layer_c.talk_peak` | Talk peak | pulse | |
| `layer_c.skip_zone` | Skip / bad | pulse | |
| `layer_c.record_mark` | Chapter mark | pulse | |
| `layer_c.gather_ui_on` | Gather UI ON | begin | + `WOWCAP.GATHER_UI_ON` after 100ms |
| `layer_c.gather_ui_off` | Gather UI OFF | end | + `WOWCAP.GATHER_UI_OFF` before restore |

## Agent prove (not human done)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Append-StreamDeckMarker.ps1" -ButtonId layer_c.record_start -Label "Record start" -State begin
```

## Residual

- Stream Deck profile JSON export is human UI — agents cannot click Elgato UI without Computer Use go.
- Rank 1 stays **OPEN** until a real play night uses multi-actions.
