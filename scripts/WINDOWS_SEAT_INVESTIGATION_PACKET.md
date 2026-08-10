# WINDOWS SEAT — Investigation packet (Mac → you)

**When:** 2026-08-10  
**From:** Mac / Grok VibeCast lane  
**To:** Local Windows model + Kyle on 3900X  
**Law:** no invent FOOTAGE · no silent publish · human KEEP · ARM default deny  

**Folder on Windows:** `D:\WoW B-Roll Storage\_scripts\`  
Read this file first, then the linked tickets in the same folder.

---

## Mission (what Kyle wants from you)

### P0 — Minimap-only **harvester B-roll**
Character runs herb/mine routes with HUD = **basically only minimap** (+ node tracking if needed).  
That is the good B-roll. **Not solved yet.**

| Keep | Hide |
|------|------|
| Minimap | Chat |
| Herb/mine nodes (if needed) | Objective / quest tracker |
| | Unit frames, bags, sticky chrome |
| | Bars ideally fully gone while gathering (hover-hide is OK interim) |

**Already good (do not undo):** bottom action bars **hide until hover**.  
**Edit Mode alone:** often leaves chat + tracker. Expect **Auto Hide UI v1.2.13** (install only if WoW **closed**) and/or named Edit Mode layout `VibeCast Gather`.  
**Not:** full Alt+Z for this mode (kills minimap too — Alt+Z = cinematic only).  
**Detail tickets:** `MINIMAP_ONLY_GATHER_BROLL.md` · (Mac canon mirrored as `GATHERING_BROLL_MODE.md` if present)

### P0 — After any video B-roll: **Session-End**
Soft-poll often shows **today = markers_only** until candidates exist.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
```

Expect: `day\raw` + `candidates\*.mp4` + MANIFEST. Then Mac harvest can run.

### P1 — Stream Deck (Kyle authorized updates on Windows)
- Layer C multi-act: record_start, broll_enter/exit, rotate, talk_peak, skip_zone, gather_ui_on/off  
- Wire from `DECK_MULTI_ACTION_INSTALL.md` / `DECK_OPEN_COMMANDS` / Install-LayerC if needed  
- Markers must be **human** presses mid-play (not only agent_prove)

### P1 — Dual audio green
OBS Desktop + Mic meters both move; 10s talk+game at record start.  
Profile: **WoW B-Roll 1440p60** → path **D:\WoW B-Roll Storage** (not Fable).

### P2 — Field Notes (audio product)
**Series name:** Explorers League · **Field Notes** (The WoW Explorer brand).  
Script: `FIELD_NOTES_SCRIPT_TODAY.md`  
Audacity truth: `AUDACITY_FIELD_NOTES_WINDOWS.md`  
- No Codex/Grok Audacity plugin — Kyle records, export WAV under `D:\...\YYYY-MM-DD\audio\`  
- Agent cleanup later = ffmpeg on file, not UI automation  

### P2 — OBS crop/zoom
Kyle found a good **zoom-in** for herb/mine capture. Preserve that scene/filter setup; document path if you change it.

---

## Soft-poll honesty (do not lie green)

| Signal | Meaning |
|--------|---------|
| `ready_today` | **Today’s** candidates/stage mp4 only |
| `ready_any` | Prior day (e.g. 08-09) may still be staged — **not** “today ready” |
| markers_only | SESSION.jsonl/markers without candidates — **do not invent FOOTAGE** |

Mac will **not** invent masters. Your job is real export → Session-End.

---

## Files in this folder (packet index)

| File | Use |
|------|-----|
| **WINDOWS_SEAT_INVESTIGATION_PACKET.md** | This index (start here) |
| MINIMAP_ONLY_GATHER_BROLL.md | Minimap-only gather ticket |
| GATHERING_BROLL_MODE.md | Full gather UI contract (if deployed) |
| CINEMATIC_ORBIT_UI_MODE.md | Alt+Z / clean orbit vs gather |
| FIELD_NOTES_SCRIPT_TODAY.md | 3–6 min Field Notes spine |
| AUDACITY_FIELD_NOTES_WINDOWS.md | Audacity + agent limits |
| FIELD_NOTES_EXPLORERS_LEAGUE.md | Product naming / shapes |
| TODAY_SESSION.md | Zero-thought capture card |
| DECK_MULTI_ACTION_INSTALL.md | Deck Layer C |
| Session-End-Ship.ps1 | Export after play |
| Auto-Session-End-If-Masters.ps1 | Today-only masters → ship |
| Windows-Preflight.ps1 | Pre-record checks |
| Configure-WoW-BRoll-OBS.ps1 | OBS path dual-track (WoW closed if reconfig) |

---

## Profession mesh (context only — not Windows code)

Kyle corrected dual-LW plan. Live lean: Blood **Herb+Mine** keep; Rot retrain toward **Tailor+Enchant**; Rage default **Herb+Mine**; **no LW on Blood DK**.  
Vault SoT: Mac `Characters/PROFESSION_MESH_KYLE.md` — not required for capture work tonight.

---

## Public surface (FYI — Mac already shipped path B)

- GitHub **public:** https://github.com/kyledempster7/gcs-vibecast-wow-capture  
- Release: `vibe-public-2026-08-10` with real KEEP sample  
- Social still **NOT_ARMED** / kyle_go false  

Windows does **not** publish social.

---

## Suggested work order for Windows seat

1. Confirm OBS path D: + dual meters (Preflight)  
2. If Kyle recorded video without candidates → **Session-End-Ship**  
3. Stream Deck Layer C human multi-act (authorized)  
4. **Minimap-only gather:** Edit Mode layout + Auto Hide UI plan (WoW closed to install)  
5. Leave Field Notes script available; do not block on Audacity automation  
6. Receipt: one short `D:\_scripts\` or inbox note what you changed  

## Bans

- Invent candidates/mp4s  
- Silent publish / arm social  
- Install ElvUI for this  
- Mass WTF thrash under live client  
- Re-harvest 08-09 as “today”  
- Factory Saturday fleet paths  

---

**Mac continues:** harvest when ready_today, Moments, package NOT_ARMED, public repo mirror.  
**You own:** Windows capture, Deck, minimap-only UI, Session-End, OBS.
