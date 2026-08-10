# Windows today — markers only (honest)

**Day:** 2026-08-10  
**Probed:** Mac soft_poll + SSH dir of `D:\WoW B-Roll Storage\2026-08-10`

## Truth

| Path | State |
|------|--------|
| `raw\` | **empty** (0 mp4) |
| `candidates\` | **empty** (0 mp4) |
| `markers\SESSION.jsonl` | present · **agent_prove / agent_install_prove only** (Deck install test, not human play night) |
| soft_poll | `ready_today=false` · `markers_only_no_candidates` |
| OBS (probe 2026-08-10) | **Running** · profile `WoW_BRoll_1440p60` · FilePath `D:\WoW B-Roll Storage` · RecTracks **3** (Desktop+Mic) · **0 today masters** on base/raw/candidates |

**Read:** path + dual-track look product-ready. Gap is **no real record** for today (newest masters still 2026-08-09).

## What this means

Mac golden/watch are **correct** to wait. There is **nothing to harvest** for today.  
Playing WoW without OBS writing masters to this day root = no product.

## Fix (when you want product from play)

1. OBS profile **WoW B-Roll 1440p60** · path under `D:\WoW B-Roll Storage`  
2. **Start record** for real (not only Deck prove)  
3. Play · optional League pitch shots from `CAPTURE_LEAGUE_PITCH_TONIGHT.md`  
4. Stop ·  
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
```

## Do not

- Invent candidates from prove markers  
- Re-harvest 2026-08-09 as “today”  
