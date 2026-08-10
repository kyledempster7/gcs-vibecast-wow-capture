# Stream Deck Layer C — button map (v0)

Wire each multi-action to PowerShell (Windows):

```
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Append-StreamDeckMarker.ps1" -ButtonId <ID> -Label "<Label>" -State <begin|end|pulse>
```

| ButtonId | Label | State | When to press |
|----------|-------|-------|---------------|
| layer_c.record_start | Record start | begin | **First press of night** — before or with OBS record |
| layer_c.broll_enter | Enter b-roll | begin | Start beauty / orbit window |
| layer_c.broll_exit | Exit b-roll | end | End beauty window |
| layer_c.rotate_begin | Begin rotate | begin | Start camera orbit |
| layer_c.rotate_end | End rotate | end | End orbit |
| layer_c.talk_peak | Talk peak | pulse | Personality / VO moment |
| layer_c.funny_moment | Funny moment | pulse | Laugh / herb-rival / shared-node energy (~5–10s) — see FUNNY_MIC_CUE_MOMENTS |
| layer_c.skip_zone | Skip / bad | pulse | Load / bad stretch |
| layer_c.record_mark | Chapter mark | pulse | Generic scrub |
| layer_c.gather_ui_on | Gather UI ON | begin | Enter Gathering B-Roll mode (`WOWCAP.GATHER_UI_ON`) |
| layer_c.gather_ui_off | Gather UI OFF | end | Exit Gathering B-Roll (`WOWCAP.GATHER_UI_OFF`) |

**Gathering mode operating note (canon):** `Games/WoW/04-Story-and-Capture/GATHERING_BROLL_MODE.md`

Vault-Tec sequence (also fire in-game addon/event):

- Enter: toggle mode → 100 ms → `WOWCAP.GATHER_UI_ON`
- Exit: `WOWCAP.GATHER_UI_OFF` → 100 ms → restore interface

Sidecar: `D:\WoW B-Roll Storage\<YYYY-MM-DD>\markers\SESSION.jsonl`

Law: fail-open create folder · no publish · OBS path prefer day root not Fable · Layer A bars-to-Deck remains P0 in parallel.

Proved: Append-StreamDeckMarker.ps1 appends gcs_obs_marker/v1 lines.
