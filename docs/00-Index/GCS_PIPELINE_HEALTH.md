# GCS pipeline health — 2026-08-12 23:15

| Check | State | Note |
|-------|-------|------|
| Windows online | 🟢 | verdict=OFFLINE+soft_poll_ssh_fresh_0s |
| Soft-poll READY | 🟢 | ready_today=true · 2026-08-12:candidates_qualified, 2026-08-11:candidates_qualified |
| OBS product path | 🟢 | running=True path_ok=True tracks=7 today_masters=True raw=1 cand=0 |
| Harvest freshness | 🟢 | today · harvest 7h age |
| Audio stamp | 🟡 | OPEN (not GREEN) |
| Latest return day | — | `returner-daily-2026-08-12` |
| Markers SESSION.jsonl | 🟡 empty/missing | |
| Candidates | 🟢 20 mp4 | |
| Pride vertical | 🟡 0 vertical | |
| Speech peaks | — | `SKIP_AMBIENCE_OR_EMPTY` |
| Review SHORTLIST | 🟢 | |
| Publish arm | 🟡 | ARMED/may_publish files: returner_daily_2026-08-09.ARMED.json — verify go |

## Next

- If OBS path OK but no today masters: press **OBS Record** during play, then Session-End.
- League pitch: `CAPTURE_LEAGUE_PITCH_TONIGHT.md` · storyboard cutlist NOT_ARMED.
- LaunchAgent quiet morning 03–11; active 12:00–02:59. No invent FOOTAGE.

Spec: `04-Story-and-Capture/PRODUCT_SYSTEM_SPEC.md`
