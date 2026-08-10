# Today — Windows product session (zero thought)

**Mode:** KYLE_OS → **Record content**  
**Laws:** fun first · no invent · no publish · ARM deny  

## 0. Sync (you said Obsidian was off)

1. Open Obsidian on **this PC** and on Mac.  
2. Wait until vault is not stuck offline.  
3. You do **not** need Obsidian to capture — scripts live on `D:\WoW B-Roll Storage\_scripts\`.

## 1. Preflight (2 min)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Windows-Preflight.ps1"
```

- OBS profile: **WoW B-Roll 1440p60** (not Fable)  
- Scene: **WOW** window capture  
- Meters: **Desktop + Mic both move**  
- Deck Layer C wired once from `DECK_OPEN_COMMANDS.txt` (if buttons still empty)

## 2. Play

| When | Press |
|------|--------|
| Start record | `record_start` |
| First 10s | Talk + game sound (dual audio proof) |
| Beauty / orbit | `broll_enter` … `rotate` … `broll_exit` |
| Personality line | `talk_peak` |
| Bad stretch | `skip_zone` |
| Optional clean gather | `gather_ui_on` / `off` · Alt+Z for full cinematic |

Stop when fun ends. Full logout.

## 3. After stop (one command)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
```

Expect: masters in `day\raw` · `candidates\*.mp4` · `MANIFEST.json`.

## 4. Walk away

Mac agent (or you once):

```bash
bash ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/post_play_harvest.sh
```

Then ≤60s KEEP on review-pack. Done.

## If something is red

| Symptom | Fix |
|---------|-----|
| No masters after stop | OBS path not D: storage — re-run `Configure-WoW-BRoll-OBS.ps1` only if OBS closed |
| Session-End NO_MASTERS | Record actually started? Check `D:\WoW B-Roll Storage\*.mp4` |
| Markers only agent_* | Press Deck mid-play with human multi-actions |
| Audio silent | Desktop source muted / wrong device — meters first |

## UI goal (OPEN) — minimap-only gather B-roll

See `MINIMAP_ONLY_GATHER_BROLL.md` in this folder (and Mac `GATHERING_BROLL_MODE.md`).  
Target: harvest routes with **only minimap** (+ nodes). Hover-hide bars = good interim. Chat/tracker still stick — figure via Edit Mode layout + Auto Hide UI (WoW closed to install).
