---
type: checklist
status: active
created: 2026-08-10
area: Games/WoW
role: PHASE_A_PLAY_NIGHT
parent: ROADMAP_P0_P2_TOP10 · RIGHTSIZE_SWARM
---

# Play night checklist (Phase A close)

**Human door:** [[../00-Index/KYLE_OS]] only.  
**Agent harvest button:** `wow-roster-tracker/scripts/post_play_harvest.sh`  
**Laws:** no invent FOOTAGE · no silent publish · ARM deny  

## Before / during play (Kyle)

| ☐ | Item | Done-when |
|---|------|-----------|
| A1 | Deck multi-act mid-session | SESSION.jsonl has real `record_start` + broll/rotate/skip (not only agent_prove) |
| A2 | Dual audio 10s | Mic + game meters; path on [[AUDIO_GREEN_STAMP]] → GREEN only if real file |
| — | Optional B | Cinematic hide UI orbit · Titan location module up |
| A3 prep | Record + Export candidates | `D:\WoW B-Roll Storage\<day>\candidates\` + MANIFEST (or Stage) |

## After play (agent or one Mac command)

```bash
bash ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/post_play_harvest.sh
# or: post_play_harvest.sh YYYY-MM-DD
```

| Step | Script | Expect |
|------|--------|--------|
| soft_poll | multi-day READY | today ready when candidates/stage mp4 exist |
| harvest | harvest_if_ready → harvest_mac → enhance | Returns/returner-daily-DAY · SHORTLIST |
| KEEP | Kyle ≤60s review-pack | human_verdicts KEEP |
| archive | enhance / archive_keep_to_moments --drive | Moments + Drive archive-broll |

**Not this path:** `post_night_mac.sh` (legacy vibe pulse / boards) — different product surface.

## Agent bans

- Invent masters for empty days  
- Re-harvest locked days without new export  
- Mark AUDIO_GREEN without 10s path  
- Stack more LaunchAgents to “close” A1–A3  
