---
type: gap-ledger
status: active
created: 2026-08-10
updated: 2026-08-10
area: Games/WoW
role: UNLINKED_UNWIRED_UNSCHEDULED
---

# 20 things unlinked / unwired / unscheduled (live inventory)

**Source:** soft_poll · health · Windows SCH · LaunchAgents · dual SoT · roadmap OPEN.  
**Not Kyle homework** — agents close agent rows; play-night rows stay honest OPEN.

| # | Item | Class | State after this wave |
|---|------|-------|------------------------|
| 1 | Mac soft_poll + harvest_if_ready cron/LaunchAgent | scheduled | **RIGHT-SIZED** 30m + quiet hours 03–19; 1 poll/tick |
| 2 | Windows Stage-ShipCandidates scheduled | demoted | **UNREGISTERED** (broken -Day; harvest_mac owns stage) |
| 3 | Export-ShipCandidates never auto after record | unscheduled | **DOCUMENTED** — stays human/agent-run (masters required); script deployed |
| 4 | Dual SoT: vault scripts vs `D:\_scripts` drift | unwired | **WIRED** `deploy_windows_scripts.sh` + harvest_mac calls it |
| 5 | Install-RemainingTasks pointed at Documents tree | unlinked | **FIXED** prefer `D:\_scripts` |
| 6 | Soft-poll health green when only yesterday ready | false-green | **FIXED** today-aware yellow |
| 7 | Windows ONLINE_TS shown as full green | false-green | **FIXED** yellow until ONLINE_SSH |
| 8 | Archive zone hardcoded `archive` not ZONE_LABEL | unlinked | **WIRED** enhance reads ZONE_LABEL.json |
| 9 | Moments tag vocabulary not machine-enforced | unlinked | **WIRED** TAG_VOCAB.json + catalog_query --lint |
| 10 | Receipts not mirrored to Drive backup-code | unscheduled | **WIRED** `mirror_receipts_to_drive.sh` → Drive backup-code/receipts-wow |
| 11 | Deck multi-act product (human press night) | unlinked product | OPEN play night (agent_install_prove + Open cmds ready) |
| 12 | AUDIO_GREEN dual meters | unlinked product | OPEN play night (OBS dual-track CONFIGURED; stamp still OPEN) |
| 13 | Marker export e2e new masters | unlinked product | OPEN play night (code + fixture CLOSED) |
| 14 | Gather UI live Deck buttons | unwired product | OPEN play + Auto Hide install (markers ready) |
| 15 | Cinematic orbit UI mode closed | unlinked product | OPEN play night |
| 16 | Titan/zone OCR → Moments tags end-to-end | partial | probe exists; needs Titan-up night |
| 17 | Chat detector 223313 edge | residual | documented irreducible; vision later optional |
| 18 | Review one-tap board (vs CLI feedback) | unwired UI | **SHIPPED** review_pack_feedback_server + build_review_pack buttons |
| 19 | HyperFrames brand stitch from Moments | unlinked product | dry stitch + **HTML brand kit slots shipped** |
| 20 | Zernio go-path from ARM package | fail-closed unlinked | intentional deny until Kyle go |

## Windows SCH (proved 2026-08-10)

Ready: Capture Inbox · CareSix · Memento · Nightly Inbox Chain · Engine Health Weekly · ThrallAutoLogout.  
**Was missing ship path:** Stage/Export GCS tasks → added Stage Nightly this wave.

## Mac LaunchAgents (before)

Only Saturday GCS fleet / front-door / unrelated IG harvest — **no** soft_poll/harvest for WoW B-roll until this wave.

## Right-size note (same day)
Swarm verdict: spine yes, fleet heavy. Receipt: `receipts/wow/RIGHTSIZE_SWARM_20260810.md` · GitHub `afa5228`.
