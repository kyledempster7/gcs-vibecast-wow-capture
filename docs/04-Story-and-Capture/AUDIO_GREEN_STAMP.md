---
type: audio-green-stamp
status: OPEN
created: 2026-08-09
updated: 2026-08-09
---

# Audio green stamp

**Agent rule:** never mark `status: GREEN` without Kyle (or a verified 10s path on disk).  
**Playbook:** [[GAME_AUDIO_RESETUP]] · jump [[../00-Index/JUMP_DESKTOP_PLAYBOOK]]

## Current

| Field | Value |
|-------|-------|
| status | **OPEN** (OBS dual-track **CONFIGURED** 2026-08-10 — stamp still needs 10s dual file) |
| last_10s_test | — |
| path_to_test_file | — |
| mic | routed track 2 (Untitled / WoW_BRoll_Product) |
| game_audio | routed track 1 Desktop |
| stamped_by | — |
| stamped_at | — |
| obs_preflight | Configure-WoW-BRoll-OBS.ps1 · FilePath `D:\WoW B-Roll Storage` · RecTracks=3 |

## When green

Change frontmatter `status: GREEN` and fill the table.  
`engine_pulse.py` / health will show 🟢 only if this file contains GREEN in the first lines.

## Gate (checklist)

- [ ] Mic moves meter  
- [ ] Game audio moves **or** voice-only night noted  
- [ ] 10s test played back  
- [ ] Path written above (real file only)
