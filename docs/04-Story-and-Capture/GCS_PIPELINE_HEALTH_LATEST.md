# GCS pipeline health — 2026-08-11 01:22

| Check | State | Note |
|-------|-------|------|
| Windows online | 🟢 | verdict=ONLINE_TS+soft_poll_ssh_fresh_3s |
| Soft-poll READY | 🟡 | ready_today=false · 2026-08-11:no_day_root, 2026-08-10:markers_only_no_candidates |
| OBS product path | 🟡 | running=False path_ok=True tracks=7 today_masters=False raw=0 cand=0 · press OBS Record then Session-End |
| Harvest freshness | 🟡 | `returner-daily-2026-08-09` · day ~49h old · STALE prior day |
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
