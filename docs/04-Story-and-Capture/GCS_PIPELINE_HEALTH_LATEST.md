# GCS pipeline health — 2026-08-10 12:25

| Check | State | Note |
|-------|-------|------|
| Windows online | 🟡 | verdict=ONLINE_TS (TS ok; SCH unproven until ONLINE_SSH) |
| Soft-poll READY | 🟡 | ready_today=false · stale other-day READY still staged · 2026-08-10:markers_only_no_candidates, 2026-08-09:candidates_present |
| Harvest freshness | 🟡 | `returner-daily-2026-08-09` · 0h ago · prior harvest |
| Audio stamp | 🟡 | OPEN (not GREEN) |
| Latest return day | — | `returner-daily-2026-08-09` |
| Markers SESSION.jsonl | 🟢 | |
| Candidates | 🟡 15 mp4 (prior day — not tonight) | |
| Pride vertical | 🟡 3 vertical | |
| Speech peaks | — | `SKIP_AMBIENCE_OR_EMPTY` |
| Review SHORTLIST | 🟡 | |
| Publish arm | 🟢 | ARM_STATE default deny (armed=false) · ARM_STATE.json |

## Next

- Phase A play night: Deck multi-act + AUDIO_GREEN + export → `post_play_harvest.sh`.
- Idle daytime LaunchAgent quiet hours are intentional. Agents: no invent FOOTAGE.

Spec: `04-Story-and-Capture/PRODUCT_SYSTEM_SPEC.md`
