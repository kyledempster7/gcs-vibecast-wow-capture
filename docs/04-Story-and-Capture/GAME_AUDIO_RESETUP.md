---
type: ops-checklist
status: open
created: 2026-08-09
updated: 2026-08-09
role: GAME_AUDIO_GAP
---

# Game audio re-setup — open gap

**Kyle note (2026-08-09):** game audio capture has **failed / not been captured recently**. Needs a deliberate re-setup before “stream muddy” or video+SFX nights feel complete.

**Voice-only remains a full win** for EP talk. This card is for **game sound in the recording**.

---

## Pass test (definition of done)

1. OBS (or your record app) armed.  
2. Record **10 seconds** in-world (footsteps / UI / music).  
3. Playback: **you hear game audio** + mic if both are wanted.  
4. One-line note: “game audio OK YYYY-MM-DD” on Daily Note or Kyle OS mental check.

Until that pass exists, treat game audio as **red**.

---

## Agent preflight (2026-08-10 — CONFIGURED on disk)

| Done | Item | Proof |
|------|------|-------|
| ✅ | Profile `WoW_BRoll_1440p60` FilePath → `D:\WoW B-Roll Storage` | `Configure-WoW-BRoll-OBS.ps1` · receipt OBS_CONFIGURE_* |
| ✅ | RecTracks=3 (dual track Advanced) | basic.ini |
| ✅ | Desktop mixers=track1 · Mic mixers=track2 | Untitled.json + WoW_BRoll_Product.json |
| ❌ | 10s dual playback proof | **Still OPEN** — needs real record + `audio_green_probe.py --write-stamp` |

## Checklist (Windows · OBS Hybrid path)

| ☐ | Step | Notes |
|---|------|-------|
| ☐ | Open OBS · profile **WoW B-Roll 1440p60** · scene with **WOW** window capture | Prefer `WoW_BRoll_Product` / Untitled — **not** Fable Anniversary |
| ☐ | Confirm meters: Desktop + Mic both move in-game | Config routes separate tracks; still verify live |
| ☐ | Windows sound: WoW not exclusive-stuck on wrong device | Check Playback devices if silent |
| ☐ | If using **Application Audio Capture** (Win): WoW process selected | Re-pick after client update |
| ☐ | 10s test → `D:\WoW B-Roll Storage\` then Move-TodayMastersToDayRoot | **Only green after probe** |
| ☐ | Optional: Stream Deck record / Layer C markers | Don’t block on process night |

**Runbook pointer:** `Kyle's Notes/Research/World of Warcraft/WoW Capture-to-Publish Workflow.md`  
Raw default was `C:\Users\kyled\Videos\WoW B-Roll` (Known Folder / mount trust issues — prefer trusted D: storage when listing paths).

---

## If stuck

| Symptom | Try |
|---------|-----|
| Mic OK, game silent | Desktop/Application audio source missing or muted |
| Everything silent | Wrong OBS scene / recording not started |
| Game only in headphones, not OBS | Device routing / Voicemeeter / exclusive mode |
| Worked last month | Client update · Windows update · OBS scene reset |

**Agents:** do not claim game audio fixed without a playback proof note from Kyle or a verified test file path.

---

## Product impact

| Content shape | Needs game audio? |
|---------------|-------------------|
| Clean flight-path VO (podcast) | Nice · **not required** |
| Stream muddy (play+talk) | **Strongly preferred** |
| Silent B-roll harvest | Video only · SFX optional |
| Achievement stills | None |

Related: [[../00-Index/KYLE_OS|Kyle OS]] · [[YouTube/STREAM_MUDDY_TALK_CARD|stream-muddy card]] · [[YouTube/FLIGHTPATH_VO_TOPICS_EP01|flight-path topics]]
