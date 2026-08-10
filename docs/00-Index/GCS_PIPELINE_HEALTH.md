# GCS pipeline health — 2026-08-10 18:25

| Check | State | Note |
|-------|-------|------|
| Windows online | 🟢 | verdict=ONLINE_TS+soft_poll_ssh_fresh_31s |
| Soft-poll READY | 🟡 | ready_today=false · stale other-day READY still staged · 2026-08-10:markers_only_no_candidates, 2026-08-09:candidates_present |
| OBS product path | 🟡 | running=True path_ok=True tracks=3 today_masters=False raw=0 cand=0 · press OBS Record then Session-End |
| Harvest freshness | 🟡 | `returner-daily-2026-08-09` · day ~42h old · STALE prior day |
| Audio stamp | 🟡 | OPEN (not GREEN) |
| Latest return day | — | `returner-daily-2026-08-09` |
| Markers SESSION.jsonl | 🟢 | |
| Candidates | 🟡 15 mp4 (prior day — not tonight) | |
| Pride vertical | 🟡 3 vertical | |
| Speech peaks | — | `SKIP_AMBIENCE_OR_EMPTY` |
| Review SHORTLIST | 🟡 | |
| Publish arm | 🟢 | ARM_STATE default deny (armed=false) · ARM_STATE.json |

## Next

- If OBS path OK but no today masters: press **OBS Record** during play, then Session-End.
- League pitch: `CAPTURE_LEAGUE_PITCH_TONIGHT.md` · storyboard cutlist NOT_ARMED.
- LaunchAgent quiet morning 03–11; active 12:00–02:59. No invent FOOTAGE.

Spec: `04-Story-and-Capture/PRODUCT_SYSTEM_SPEC.md`
